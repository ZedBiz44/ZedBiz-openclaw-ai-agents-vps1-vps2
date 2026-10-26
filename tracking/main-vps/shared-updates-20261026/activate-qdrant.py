"""Activate the accepted Qdrant image after idle checks and a coherent exact-volume copy."""
import pathlib,subprocess,json,os,time,urllib.request,urllib.parse,hashlib,datetime
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/shared-updates-20261026');A=W/'update-qdrant';A.mkdir(mode=0o700);pilot=json.loads((W/'qdrant-pilot/proof.json').read_text());assert pilot['passed'];candidate=pilot['candidate'];name='mem0-dev-qdrant-1';rpc=P('/opt/openclaw/backups/mem0-repair-20261024-r2/rpc.mjs').read_text()
def run(args,label,timeout=300,input=None):
 p=subprocess.run(args,input=input,capture_output=True,text=True,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
def inspect(n):return json.loads(subprocess.check_output(['docker','inspect',n]))[0]
def call(agent,method,params=None):return json.loads(run(['docker','exec','-i','-e','CODY_RPC_REQUEST='+json.dumps({'method':method,'params':params or {}}),agent,'node','--input-type=module'],agent+'-'+method,120,rpc))
started=time.monotonic()
while True:
 idle=True
 for agent in ['terry','edith']:
  work=call(agent,'status').get('shutdownBudget',{}).get('activeWork');assert work;idle &= all(v==0 for v in work.values());jobs=call(agent,'cron.list',{'includeDisabled':True})['jobs'];idle &= not any(j.get('state',{}).get('runningAtMs') for j in jobs)
 if idle:break
 assert time.monotonic()-started<1200,'Mem0 users remain busy';time.sleep(15)
old=inspect(name);assert old['State']['Running'];(A/'before.inspect.private.json').write_text(json.dumps(old));labels=old['Config']['Labels'];compose=P(labels['com.docker.compose.project.config_files']);service=labels['com.docker.compose.service'];original=compose.read_bytes();(A/'compose-before.private').write_bytes(original);render=json.loads(run(['docker','compose','-f',str(compose),'config','--format','json'],'config-before'));oldRef=render['services'][service]['image'];assert original.decode().count(oldRef)==1 and oldRef==old['Config']['Image'];storage=next(P(m['Source']) for m in old['Mounts'] if m['Destination']=='/qdrant/storage');assert storage==P('/var/lib/docker/volumes/mem0-dev_qdrant_storage/_data') and storage.resolve()==storage and not storage.is_symlink();key=dict(e.split('=',1) for e in old['Config']['Env'])['QDRANT__SERVICE__API_KEY']
def req(path):
 d=inspect(name);ip=next(iter(d['NetworkSettings']['Networks'].values()))['IPAddress']
 with urllib.request.urlopen(urllib.request.Request('http://'+ip+':6333'+path,headers={'api-key':key}),timeout=20) as r:return json.load(r)
def counts():return {c['name']:req('/collections/'+urllib.parse.quote(c['name'],safe=''))['result']['points_count'] for c in req('/collections')['result']['collections']}
before=counts();(A/'counts-before.private.json').write_text(json.dumps(before));changed=False
try:
 run(['docker','stop','-t','30',name],'stop',90);changed=True;run(['cp','-a',str(storage),str(A/'before-storage')],'storage-checkpoint');compose.write_bytes(original.decode().replace(oldRef,candidate['pinnedRef']).encode());after=json.loads(run(['docker','compose','-f',str(compose),'config','--format','json'],'config-after'));expected=json.loads(json.dumps(render));expected['services'][service]['image']=candidate['pinnedRef'];assert after==expected
 run(['docker','compose','-f',str(compose),'up','-d','--no-deps',service],'activate');start=time.monotonic()
 while True:
  try:
   version=req('/')['version'];afterCounts=counts();assert version=='1.20.0' and afterCounts==before;break
  except Exception:assert inspect(name)['State']['Running'] and time.monotonic()-start<180;time.sleep(3)
 d=inspect(name);assert d['Image']==candidate['imageId'] and d['HostConfig']['PortBindings']==old['HostConfig']['PortBindings'];assert d['Mounts']==old['Mounts'];assert dict(e.split('=',1) for e in d['Config']['Env'])['QDRANT__SERVICE__API_KEY']==key
 proof={'passed':True,'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':version,'oldImageId':old['Image'],'newImageId':d['Image'],'pinnedRef':candidate['pinnedRef'],'actualMem0SdkPilotPassed':True,'businessCollectionCountsPreserved':True,'collections':len(before),'allPoints':sum(before.values()),'authKeyMountsAndPortBindingsPreserved':True,'onlyComposeImageChanged':True,'coherentRollbackStoragePreserved':True};(A/'acceptance.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
except Exception:
 if changed:
  d=inspect(name)
  if d['State']['Running']:run(['docker','stop','-t','30',name],'rollback-stop',90)
  assert storage.resolve()==storage and not (A/'failed-storage').exists();storage.rename(A/'failed-storage');run(['cp','-a',str(A/'before-storage'),str(storage)],'restore-storage');compose.write_bytes(original);run(['docker','compose','-f',str(compose),'up','-d','--no-deps',service],'rollback');(A/'rollback.json').write_text(json.dumps({'oldImageAndStorageRestored':True}))
 raise
