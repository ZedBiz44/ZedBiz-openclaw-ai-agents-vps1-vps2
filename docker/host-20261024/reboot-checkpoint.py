"""Protect live databases and host context before an authorized maintenance reboot."""
import pathlib,subprocess,json,os,sqlite3,hashlib,time,urllib.request,urllib.parse
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/host-20261024');D=W/'database-checkpoint';D.mkdir(mode=0o700,exist_ok=True)
def sha(p):
 with P(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(a):return subprocess.run(a,capture_output=True,text=True,timeout=900)
fleet=json.loads((W/'before-reboot-fleet.json').read_text());assert len(fleet)==11
assert all(x['activeWork'] is not None and not any(x['activeWork'].values()) and x['runningSchedules']==0 for x in fleet),'Active or unknown work; refresh fleet check and wait'
proof={'sqlite':[],'postgres':{},'qdrant':[],'bootIdBefore':P('/proc/sys/kernel/random/boot_id').read_text().strip()}
for row in fleet:
 base=P('/opt/openclaw/agents')/row['agent'];out=D/row['agent'];out.mkdir(mode=0o700,exist_ok=True)
 # Consistent SQLite backup APIs retain committed WAL content without copying live files.
 dbs=[base/'config/state/openclaw.sqlite',*(base/'agents').glob('*/agent/openclaw-agent.sqlite')]
 for index,db in enumerate(dbs):
  if not db.exists():continue
  target=out/(str(index)+'-'+db.name)
  with sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) as src,sqlite3.connect(target) as dst:
   src.backup(dst);dst.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True);assert dst.execute('pragma quick_check').fetchall()==[('ok',)]
  proof['sqlite'].append({'agent':row['agent'],'source':str(db),'backup':str(target),'sha256':sha(target)})
 cfg=base/'config/openclaw.json';(out/'openclaw.json').write_bytes(cfg.read_bytes())
 p=run(['docker','logs',row['agent']]);(W/('pre-reboot-'+row['agent']+'.log')).write_text(p.stdout+p.stderr)
with (D/'hindsight-postgres.dump').open('wb') as f:
 p=subprocess.run(['docker','exec','hindsight-db','sh','-c','exec pg_dump -Fc -U "$POSTGRES_USER" "$POSTGRES_DB"'],stdout=f,stderr=subprocess.PIPE,timeout=900);assert p.returncode==0,'Postgres backup failed'
with (D/'hindsight-postgres.dump').open('rb') as f:
 p=subprocess.run(['docker','exec','-i','hindsight-db','pg_restore','--list'],stdin=f,capture_output=True,timeout=120);assert p.returncode==0,'Postgres archive listing failed';(D/'hindsight-postgres-list.txt').write_bytes(p.stdout)
proof['postgres']={'archive':str(D/'hindsight-postgres.dump'),'sha256':sha(D/'hindsight-postgres.dump'),'archiveListingPassed':True}
qd=json.loads(subprocess.check_output(['docker','inspect','mem0-dev-qdrant-1']))[0];ip=next(x['IPAddress'] for x in qd['NetworkSettings']['Networks'].values() if x.get('IPAddress'));base='http://'+ip+':6333';env=dict(x.split('=',1) for x in qd['Config']['Env'] if '=' in x);headers={}
if env.get('QDRANT__SERVICE__API_KEY'):headers['api-key']=env['QDRANT__SERVICE__API_KEY']
def api(path,method='GET'):
 with urllib.request.urlopen(urllib.request.Request(base+path,method=method,headers=headers),timeout=300) as r:return json.load(r)
for c in api('/collections')['result']['collections']:
 name=c['name'];path='/collections/'+urllib.parse.quote(name,safe='')+'/snapshots';result=api(path+'?wait=true','POST')['result'];filename=result['name'];dest=D/('qdrant-'+filename)
 with urllib.request.urlopen(urllib.request.Request(base+path+'/'+urllib.parse.quote(filename,safe=''),headers=headers),timeout=300) as response,dest.open('wb') as f:
  import shutil;shutil.copyfileobj(response,f)
 assert dest.stat().st_size>0;proof['qdrant'].append({'collection':name,'snapshot':filename,'backup':str(dest),'sha256':sha(dest)})
proof['passed']=True;proof['timeUTC']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());(W/'reboot-checkpoint.json').write_text(json.dumps(proof,indent=2));print(json.dumps({'rebootCheckpointPassed':True,'sqliteDatabases':len(proof['sqlite']),'postgresArchiveVerified':True,'qdrantCollections':len(proof['qdrant'])}),flush=True)

