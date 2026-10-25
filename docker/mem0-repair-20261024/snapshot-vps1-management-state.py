"""Briefly stop only management UIs for consistent Bolt databases, then prove their restored copies."""
import pathlib,subprocess,json,shutil,hashlib,os,time
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/private-recovery-20261024/management-state');assert not W.exists();W.mkdir(mode=0o700);inputs=W/'inputs';inputs.mkdir();receipts=[]
def obj(name):return json.loads(subprocess.check_output(['docker','inspect',name]))[0]
def run(args,label,timeout=120):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(W/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
for name in ['portainer','filebrowser']:
 d=obj(name);assert d['State']['Running'];source=P('/opt/portainer/data') if name=='portainer' else P('/opt/filebrowser/filebrowser.db');assert source.exists() and not source.is_symlink();assert any(m['Source']==str(source) for m in d['Mounts']);destination=inputs/str(source).lstrip('/');destination.parent.mkdir(parents=True,exist_ok=True);start=time.monotonic();stopped=False
 try:
  run(['docker','stop','-t','20',name],name+'-stop');stopped=True
  if source.is_dir():shutil.copytree(source,destination,symlinks=True)
  else:shutil.copy2(source,destination)
 finally:
  if stopped:run(['docker','start',name],name+'-start')
 assert obj(name)['Id']==d['Id'] and obj(name)['State']['Running'];interruption=round(time.monotonic()-start,2);fixture=W/'restore-check'/name;fixture.parent.mkdir(exist_ok=True)
 originalItems=[source,*source.rglob('*')] if source.is_dir() else [source]
 for original in originalItems:
  copied=destination/original.relative_to(source) if source.is_dir() else destination;info=original.lstat();os.lchown(copied,info.st_uid,info.st_gid)
  if not copied.is_symlink():os.chmod(copied,info.st_mode&0o7777)
  assert copied.lstat().st_uid==info.st_uid and copied.lstat().st_gid==info.st_gid
 if destination.is_dir():shutil.copytree(destination,fixture,symlinks=True)
 else:shutil.copy2(destination,fixture)
 if name=='filebrowser':
  run(['docker','run','--rm','--network','none','--memory','256m','--entrypoint','/bin/filebrowser','-v',str(fixture)+':/fixture.db',d['Image'],'config','cat','--database','/fixture.db'],'filebrowser-restored-config')
 else:
  test='cody-portainer-database-restore';assert subprocess.run(['docker','inspect',test],capture_output=True).returncode!=0
  try:
   run(['docker','run','-d','--name',test,'--label','cody.management-restore=true','--network','none','--memory','512m','-v',str(fixture)+':/data',d['Image']],'portainer-restore-start');pid=obj(test)['State']['Pid'];deadline=time.monotonic()+90
   code="import urllib.request,ssl,json; r=urllib.request.urlopen('https://127.0.0.1:9443/api/status',context=ssl._create_unverified_context(),timeout=5); print(json.dumps(json.load(r)))"
   while True:
    p=subprocess.run(['nsenter','-t',str(pid),'-n','--','/usr/bin/python3','-c',code],capture_output=True,text=True)
    if p.returncode==0:
     status=json.loads(p.stdout);assert status.get('Version');(W/'portainer-restored-status.private.json').write_text(p.stdout);break
    assert time.monotonic()<deadline and obj(test)['State']['Running'],'Portainer restored DB/API did not become ready';time.sleep(2)
  finally:
   if subprocess.run(['docker','inspect',test],capture_output=True).returncode==0:
    run(['docker','stop','-t','15',test],'portainer-restore-stop');run(['docker','rm',test],'portainer-restore-remove')
 files=[p for p in destination.rglob('*') if p.is_file()] if destination.is_dir() else [destination];hashes={}
 for p in files:
  with p.open('rb') as file:hashes[str(p.relative_to(inputs))]=hashlib.file_digest(file,'sha256').hexdigest()
 receipts.append({'service':name,'source':str(source),'imageId':d['Image'],'sameProductionContainerResumed':True,'interruptionSeconds':interruption,'restoredDatabaseReadPassed':True,'files':hashes});print(json.dumps({k:v for k,v in receipts[-1].items() if k!='files'}),flush=True)
proof={'passed':True,'services':receipts,'agentGatewaysNotStoppedByThisScript':True,'ownershipMetadataVerified':True};(W/'proof.json').write_text(json.dumps(proof,indent=2));restore=W/'restore-check';assert restore.resolve()==W/'restore-check';shutil.rmtree(restore);print('Management database restore checks passed.',flush=True)
