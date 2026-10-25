"""Supported full-storage Qdrant snapshot and isolated same-image restore."""
import pathlib,json,subprocess,hashlib,urllib.request,urllib.parse,time,os
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/private-recovery-20261024/qdrant-current-proof');assert not W.exists();W.mkdir(mode=0o700)
d=json.loads(subprocess.check_output(['docker','inspect','mem0-dev-qdrant-1']))[0];env=dict(e.split('=',1) for e in d['Config']['Env']);key=env['QDRANT__SERVICE__API_KEY'];ip=next(iter(d['NetworkSettings']['Networks'].values()))['IPAddress'];base='http://'+ip+':6333';fixture='cody-qdrant-current-restore';snap=W/'storage.snapshot'
def req(url,method='GET',data=None,auth=True,timeout=300):
 headers={'api-key':key} if auth else {}
 if data is not None:headers['Content-Type']='application/json';data=json.dumps(data).encode()
 with urllib.request.urlopen(urllib.request.Request(url,data=data,headers=headers,method=method),timeout=timeout) as response:return json.load(response)
def counts(url,auth):
 collections=req(url+'/collections',auth=auth)['result']['collections'];return {c['name']:req(url+'/collections/'+urllib.parse.quote(c['name'],safe=''),auth=auth)['result']['points_count'] for c in collections}
before=counts(base,True);result=req(base+'/snapshots','POST',{})['result'];assert result['name']
(W/'snapshot-metadata.private.json').write_text(json.dumps(result))
with urllib.request.urlopen(urllib.request.Request(base+'/snapshots/'+urllib.parse.quote(result['name'],safe=''),headers={'api-key':key}),timeout=300) as response,snap.open('xb') as out:
 while True:
  block=response.read(1024*1024)
  if not block:break
  out.write(block)
assert snap.stat().st_size>1024
with snap.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
print(json.dumps({'qdrantBackup':'snapshot-created','bytes':snap.stat().st_size,'collectionCount':len(before)}),flush=True)
storage=W/'restore-data';storage.mkdir();assert subprocess.run(['docker','inspect',fixture],capture_output=True).returncode!=0
try:
 p=subprocess.run(['docker','run','-d','--name',fixture,'--label','cody.qdrant-current-proof=true','--memory','1g','--cpus','1','-p','127.0.0.1:16339:6333','-v',str(storage)+':/qdrant/storage','-v',str(snap)+':/restore/storage.snapshot:ro',d['Image'],'./qdrant','--storage-snapshot','/restore/storage.snapshot','--disable-telemetry'],capture_output=True,text=True,timeout=90);(W/'start.private.log').write_text(p.stdout+p.stderr);assert p.returncode==0
 start=time.monotonic()
 while True:
  try:restored=counts('http://127.0.0.1:16339',False);break
  except Exception:
   assert time.monotonic()-start<180;assert json.loads(subprocess.check_output(['docker','inspect',fixture]))[0]['State']['Running'];time.sleep(3)
 assert restored==before,'Restored collection counts differ; inspect snapshot versus active-write timing'
 proof={'passed':True,'productionImage':d['Image'],'snapshotSha256':digest,'snapshotBytes':snap.stat().st_size,'collectionCount':len(before),'totalPoints':sum(before.values()),'allCollectionCountsMatched':True,'isolatedSameImageRestoreVerified':True}
 (W/'proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
finally:
 if subprocess.run(['docker','inspect',fixture],capture_output=True).returncode==0:
  subprocess.run(['docker','stop','-t','15',fixture],capture_output=True,timeout=60);subprocess.run(['docker','rm',fixture],capture_output=True,timeout=60)
