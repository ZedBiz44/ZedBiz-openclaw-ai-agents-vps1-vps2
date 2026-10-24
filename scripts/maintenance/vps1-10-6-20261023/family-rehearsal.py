"""Restored-state memory-family checks. Production mounts are never writable."""
import json,os,pathlib,shutil,sqlite3,subprocess,sys,time
os.umask(0o077)
agent,action=sys.argv[1:];assert agent in ['amanda','gohzed']
base=pathlib.Path('/opt/openclaw/agents')/agent
w=pathlib.Path('/opt/openclaw/backups/release-20261023')/agent;stage=w/'rehearsal'
name='release-20261023-'+agent+'-gateway'
candidate='zedbiz/'+('amanda' if agent=='amanda' else 'openclaw-base')+':2026.10.6-core-20261023'
if action=='release-cloned-lease':
 assert stage.resolve()==pathlib.Path('/opt/openclaw/backups/release-20261023')/agent/'rehearsal'
 for container in subprocess.check_output(['docker','ps','-q'],text=True).split():
  d=json.loads(subprocess.check_output(['docker','inspect',container]))[0]
  assert not any(m['Source'].startswith(str(stage)+'/') for m in d['Mounts']),'A rehearsal process still owns this copy'
 p=stage/'config/state/openclaw.sqlite'
 with sqlite3.connect(p) as db:
  rows=db.execute("select * from state_leases where scope='gateway-owner' and lease_key='global'").fetchall()
  assert len(rows)==1 and db.execute('select count(*) from state_leases').fetchone()[0]==1
  assert db.execute('select count(*) from agent_database_leases').fetchone()[0]==0
  (w/'cloned-owner-lease-before.json').write_text(json.dumps(rows))
  db.execute("delete from state_leases where scope='gateway-owner' and lease_key='global'")
 print('Released only the copied gateway owner lease; live database untouched',flush=True);sys.exit()
if action=='prepare':
 w.mkdir(mode=0o700)
 d=json.loads(subprocess.check_output(['docker','inspect',agent]))[0]
 (w/'runtime.env').write_text('\n'.join(d['Config']['Env'])+'\n')
 (w/'mounts.json').write_text(json.dumps(d['Mounts']))
 # SQLite backup below replaces hot database copies with transactionally consistent snapshots.
 def skip(directory,names):
  return {'tmp','cache'}&set(names) if pathlib.Path(directory)==base/'config' else set()
 shutil.copytree(base,stage,symlinks=True,ignore=skip,copy_function=shutil.copy2)
 for src in [base/'config/state/openclaw.sqlite',*(base/'agents').glob('*/agent/openclaw-agent.sqlite')]:
  dst=stage/src.relative_to(base)
  for p in [dst,pathlib.Path(str(dst)+'-wal'),pathlib.Path(str(dst)+'-shm')]:
   if p.exists():p.unlink()
  with sqlite3.connect('file:'+str(src)+'?mode=ro',uri=True) as old,sqlite3.connect(dst) as new:old.backup(new)
  st=src.stat();os.chown(dst,st.st_uid,st.st_gid);os.chmod(dst,st.st_mode&0o777)
 # copytree preserves modes but not owners; restore ownership without following symlinks.
 for srcdir,dirs,files in os.walk(base,followlinks=False):
  for src in [pathlib.Path(srcdir),*[pathlib.Path(srcdir)/n for n in files+dirs]]:
   dst=stage/src.relative_to(base)
   if dst.exists() or dst.is_symlink():
    st=src.lstat();os.chown(dst,st.st_uid,st.st_gid,follow_symlinks=False)
 config=stage/'config/openclaw.json';shutil.copy2(config,w/'config-before.json')
 c=json.loads(config.read_text());c.setdefault('cron',{})['enabled']=False
 c.setdefault('hooks',{})['enabled']=False;c['hooks'].setdefault('internal',{})['enabled']=False
 c['agents']['defaults'].setdefault('heartbeat',{})['every']='0m'
 for a in [*c['agents'].get('list',[]),*c['agents'].get('entries',{}).values()]:a.setdefault('heartbeat',{})['every']='0m'
 if agent=='gohzed':
  cfg=c['plugins']['entries']['hindsight-openclaw']['config']
  cfg['hindsightApiUrl']='http://release-20261023-hindsight-rehearsal-api:8888'
 config.write_text(json.dumps(c,indent=2)+'\n')
 shutil.copytree('/opt/openclaw/shared/knowledge/wiki',w/'wiki',copy_function=shutil.copy2)
 subprocess.run(['chown','-R','1000:1000',str(w/'wiki')],check=True)
 print('Prepared isolated '+agent+' state and SQLite snapshots',flush=True);sys.exit()
def args(detached=False):
 a=['docker','run','-d' if detached else '--rm','--network','openclaw']
 if agent=='gohzed':a+=['--network','release-20261023-hindsight-rehearsal']
 if detached:a+=['--name',name]
 a+=['--memory','3g','--env-file',str(w/'runtime.env'),'--user','node','--entrypoint','node']
 for key in ['OPENCLAW_SKIP_CHANNELS','OPENCLAW_SKIP_CRON','OPENCLAW_SKIP_GMAIL_WATCHER','OPENCLAW_DISABLE_BONJOUR']:a+=['-e',key+'=1']
 for m in json.loads((w/'mounts.json').read_text()):
  src=m['Source'];dst=m['Destination']
  if src in ['/var/run/docker.sock','/dev/shm']:continue
  if src.startswith(str(base)+'/'):src=str(stage/src[len(str(base))+1:]);mode='' if m['RW'] else ':ro'
  else:mode=':ro'
  a+=['-v',src+':'+dst+mode]
 a+=['-v',str(w/'wiki')+':/opt/openclaw/shared/knowledge/wiki',candidate,'/app/openclaw.mjs']
 return a
if action in ['migrate','plugin-update','plugin-plan']:
 assert action=='migrate' or agent=='gohzed'
 tail=['doctor','--fix','--non-interactive'] if action=='migrate' else ['plugins','update','@vectorize-io/hindsight-openclaw@1.2.0']
 if action=='plugin-plan':tail+=['--dry-run']
 with (w/(action+'.log')).open('w') as out:p=subprocess.run(args()+tail,stdout=out,stderr=subprocess.STDOUT)
 if action=='plugin-update' and p.returncode==0:
  config=stage/'config/openclaw.json';c=json.loads(config.read_text())
  c['plugins']['entries']['hindsight-openclaw']['config']['allowKnowledgeDelete']=False
  config.write_text(json.dumps(c,indent=2)+'\n')
 (w/(action+'-receipt.json')).write_text(json.dumps({'exit':p.returncode}));print(action,p.returncode,flush=True);sys.exit(p.returncode)
elif action=='start':
 assert json.loads((w/'migrate-receipt.json').read_text())['exit']==0
 if agent=='gohzed':assert json.loads((w/'plugin-update-receipt.json').read_text())['exit']==0
 port=json.loads((stage/'config/openclaw.json').read_text())['gateway']['port']
 subprocess.run(args(True)+['gateway','run','--port',str(port),'--bind','loopback'],check=True,stdout=subprocess.DEVNULL)
 print('Started isolated '+agent+' gateway',flush=True)
elif action=='stop':
 with (w/'gateway.log').open('w') as out:subprocess.run(['docker','logs',name],stdout=out,stderr=subprocess.STDOUT,check=True)
 subprocess.run(['docker','stop',name],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['docker','rm',name],check=True,stdout=subprocess.DEVNULL)
 print('Stopped isolated '+agent+' gateway',flush=True)
else:raise SystemExit('Expected prepare, migrate, plugin-update, start or stop')
