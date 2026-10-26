"""Pilot each dashboard against copied state, then update only its pinned compose image."""
import pathlib,subprocess,json,os,sys,time,shutil,urllib.request,urllib.error,sqlite3,hashlib,datetime
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/shared-updates-20261026');name=sys.argv[1];assert name in ['portainer','uptime-kuma','dozzle','homepage'];A=W/('update-'+name);A.mkdir(mode=0o700);catalog=json.loads((W/'candidate-images.json').read_text());candidate=catalog[name];network='cody-dashboard-proof-20261026';clone='cody-dashboard-'+name+'-20261026'
def inspect(n):return json.loads(subprocess.check_output(['docker','inspect',n]))[0]
def run(args,label,timeout=300):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
old=inspect(name);assert old['State']['Running'];(A/'before.inspect.private.json').write_text(json.dumps(old));env=dict(e.split('=',1) for e in old['Config']['Env']);(A/'runtime.env').write_text('\n'.join(old['Config']['Env'])+'\n');labels=old['Config']['Labels'];compose=P(labels['com.docker.compose.project.config_files']);assert ',' not in str(compose);service=labels['com.docker.compose.service'];original=compose.read_bytes();(A/'compose-before.private').write_bytes(original);render=json.loads(run(['docker','compose','-f',str(compose),'config','--format','json'],'config-before'));originalRef=render['services'][service]['image'];assert original.decode().count(originalRef)==1;assert originalRef==old['Config']['Image'];assert originalRef!=candidate['pinnedRef']
port={'portainer':9000,'uptime-kuma':3001,'dozzle':8080,'homepage':3000}[name];paths={'portainer':['/api/status','/api/users/admin/check'],'uptime-kuma':['/'],'dozzle':['/','/healthcheck'],'homepage':['/api/healthcheck','/']}[name]
host=env.get('HOMEPAGE_ALLOWED_HOSTS','').split(',')[0].strip();headers={'Host':host} if name=='homepage' and host and host!='*' else {}
def probe(container,requiredVersion=None):
 d=inspect(container);assert d['State']['Running'] and not d['State']['OOMKilled'];ip=next(iter(d['NetworkSettings']['Networks'].values()))['IPAddress'];results=[]
 for path in paths:
  try:
   with urllib.request.urlopen(urllib.request.Request('http://'+ip+':'+str(port)+path,headers=headers),timeout=8) as response:body=response.read();status=response.status
  except urllib.error.HTTPError as e:status=e.code;body=e.read()
  assert status in [200,204],'HTTP '+str(status)+' '+path;results.append({'path':path,'status':status})
  if name=='portainer' and path=='/api/status' and requiredVersion:assert json.loads(body).get('Version',json.loads(body).get('version'))==requiredVersion
 return results
def wait(container,version=None,health=False):
 start=time.monotonic()
 while True:
  try:
   result=probe(container,version)
   if health:assert inspect(container)['State'].get('Health',{}).get('Status') in [None,'healthy']
   return result
  except Exception:
   d=inspect(container);assert d['State']['Running'] and time.monotonic()-start<240,'Service readiness failed: '+container;time.sleep(3)
baseline=wait(name);(A/'http-before.json').write_text(json.dumps(baseline));dataMounts=[m for m in old['Mounts'] if m['Destination']!='/var/run/docker.sock'];sources={m['Source']:P(m['Source']) for m in dataMounts};stopped=False
try:
 if name in ['portainer','uptime-kuma']:run(['docker','stop','-t','15',name],'stop-for-consistent-copy',90);stopped=True
 for source,p in sources.items():
  assert p.resolve()==p and not p.is_symlink();dest=A/'before-data'/p.name;dest.parent.mkdir(exist_ok=True);run(['cp','-a',str(p),str(dest)],'snapshot-'+p.name);run(['cp','-a',str(dest),str(A/('pilot-'+p.name))],'pilot-copy-'+p.name)
finally:
 if stopped:run(['docker','start',name],'resume-original',90);wait(name)
if subprocess.run(['docker','network','inspect',network],capture_output=True).returncode:run(['docker','network','create','--internal','--label','cody.dashboard-proof=true',network],'network')
args=['docker','run','-d','--name',clone,'--label','cody.dashboard-proof=true','--network',network,'--memory','1g','--env-file',str(A/'runtime.env')]
for m in old['Mounts']:
 source=m['Source'];dest=m['Destination']
 if source=='/var/run/docker.sock':
  if name=='portainer':continue
  args+=['-v',source+':'+dest+':ro']
 else:args+=['-v',str(A/('pilot-'+P(source).name))+':'+dest+('' if m['RW'] else ':ro')]
args+=[candidate['imageId'],*(old['Config'].get('Cmd') or [])];run(args,'pilot-start');pilotVersion='2.45.3' if name=='portainer' else None
try:
 pilotHttp=wait(clone,pilotVersion)
 if name=='uptime-kuma':assert run(['docker','exec',clone,'node','-p',"require('/app/package.json').version"],'pilot-version').strip()=='2.5.7'
 rowCounts={}
 if name=='uptime-kuma':
  oldDb=A/'before-data/data/kuma.db';newDb=A/'pilot-data/kuma.db';assert oldDb.exists() and newDb.exists()
  for table in ['monitor','notification','user']:
   values=[]
   for dbfile in [oldDb,newDb]:
    with sqlite3.connect('file:'+str(dbfile)+'?mode=ro',uri=True) as db:assert db.execute('pragma quick_check').fetchone()==('ok',);values.append(db.execute('select count(*) from '+table).fetchone()[0])
   assert values[0]==values[1];rowCounts[table]=values[0]
 proof={'passed':True,'candidate':candidate,'http':pilotHttp,'copiedState':True,'outboundNetworkDisabled':True,'rowCountsPreserved':rowCounts};(A/'pilot.json').write_text(json.dumps(proof,indent=2));print(json.dumps({'dashboard':name,'pilotPassed':True}),flush=True)
finally:
 with (A/'pilot-container.private.log').open('w') as out:subprocess.run(['docker','logs',clone],stdout=out,stderr=subprocess.STDOUT)
 run(['docker','stop','-t','10',clone],'pilot-stop',60);run(['docker','rm',clone],'pilot-remove',60)
assert inspect(name)['Id']==old['Id'] and compose.read_bytes()==original,'Production changed during pilot';assert json.loads((A/'pilot.json').read_text())['passed'];activationStarted=False
try:
 if name in ['portainer','uptime-kuma']:
  run(['docker','stop','-t','15',name],'activation-stop',90);activationStarted=True
  for p in sources.values():
   dest=A/'pre-activation-data'/p.name;dest.parent.mkdir(exist_ok=True);run(['cp','-a',str(p),str(dest)],'activation-snapshot-'+p.name)
 text=original.decode().replace(originalRef,candidate['pinnedRef']);compose.write_bytes(text.encode());activationStarted=True
 after=json.loads(run(['docker','compose','-f',str(compose),'config','--format','json'],'config-after'));expected=json.loads(json.dumps(render));expected['services'][service]['image']=candidate['pinnedRef'];assert after==expected,'Unexpected rendered compose change'
 run(['docker','compose','-f',str(compose),'up','-d','--no-deps',service],'activate',300);checks=wait(name,pilotVersion,True);new=inspect(name);assert new['Image']==candidate['imageId'];assert [(m['Source'],m['Destination'],m['RW']) for m in new['Mounts']]==[(m['Source'],m['Destination'],m['RW']) for m in old['Mounts']];newEnv=dict(e.split('=',1) for e in new['Config']['Env']);assert all(newEnv.get(k)==str(v) for k,v in render['services'][service].get('environment',{}).items() if v is not None);assert not new['State']['OOMKilled']
 result={'passed':True,'service':name,'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'oldImageId':old['Image'],'newImageId':new['Image'],'pinnedRef':candidate['pinnedRef'],'pilotPassed':True,'http':checks,'onlyComposeImageChanged':True,'environmentAndMountsPreserved':True,'rollbackStatePreserved':True};(A/'acceptance.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
except Exception:
 if activationStarted:
  d=inspect(name)
  if d['State']['Running']:run(['docker','stop','-t','15',name],'rollback-stop',90)
  compose.write_bytes(original)
  if name in ['portainer','uptime-kuma']:
   for p in sources.values():
    backup=A/'pre-activation-data'/p.name;assert backup.is_dir() and p.resolve()==p and not p.is_symlink();failed=A/('failed-live-'+p.name);assert not failed.exists();p.rename(failed);run(['cp','-a',str(backup),str(p)],'rollback-data-'+p.name)
  run(['docker','compose','-f',str(compose),'up','-d','--no-deps',service],'rollback',300);wait(name);assert inspect(name)['Image']==old['Image'];(A/'rollback.json').write_text(json.dumps({'passed':True,'oldImageRestored':True,'oldStateRestored':name in ['portainer','uptime-kuma']}))
 raise
