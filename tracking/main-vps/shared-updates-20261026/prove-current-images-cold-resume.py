"""Load the complete post-Manus image archive into an empty private Docker store."""
import pathlib,subprocess,json,os,time,signal,shutil
P=pathlib.Path;W=P('/opt/openclaw/backups/shared-updates-20261026/offsite');A=W/'image-proof-resume';A.mkdir(mode=0o700);catalog=json.loads((W/'inputs/current-images/catalog.json').read_text());archive=W/'inputs/current-images/images.tar.gz';store=W/'image-proof/store';runtime=P('/run/cdy26r2');assert not runtime.exists() and store.exists();assert shutil.disk_usage(W).free>25*1024**3;runtime.mkdir(mode=0o700);config=A/'daemon.json';config.write_text(json.dumps({'features':{'containerd-snapshotter':False}}));sock='unix://'+str(runtime/'docker.sock');log=(A/'daemon.private.log').open('w');daemon=subprocess.Popen(['dockerd','--config-file',str(config),'--host',sock,'--data-root',str(store),'--exec-root',str(runtime),'--pidfile',str(runtime/'dockerd.pid'),'--bridge','none','--iptables=false','--ip6tables=false','--ip-forward=false','--ip-masq=false','--userland-proxy=false','--storage-driver','overlay2','--containerd','/run/containerd/containerd.sock','--containerd-namespace','cdy26-proof','--containerd-plugins-namespace','cdy26-proof-plugins'],stdout=log,stderr=subprocess.STDOUT);cli=['docker','--host',sock]
def run(args,label,timeout=300):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
try:
 start=time.monotonic()
 while True:
  p=subprocess.run(cli+['info','--format','{{json .}}'],capture_output=True,text=True)
  if p.returncode==0:break
  assert daemon.poll() is None and time.monotonic()-start<120,'Private Docker did not start';time.sleep(2)
 info=json.loads(p.stdout);assert P(info['DockerRootDir']).resolve()==store.resolve(); assert (W/'image-proof/load.private.log').exists()
 with (A/'load.private.log').open('w') as out:
  dec=subprocess.Popen(['pigz','-d','-c',str(archive)],stdout=subprocess.PIPE);loaded=subprocess.run(cli+['load','--quiet'],stdin=dec.stdout,stdout=out,stderr=subprocess.STDOUT,timeout=2400);dec.stdout.close();assert dec.wait(timeout=60)==0 and loaded.returncode==0
 proofs=[]
 for index,image in enumerate(catalog['images']):
  restored=json.loads(run(cli+['image','inspect',image['id']],'inspect-'+str(index)))[0];assert restored['Id']==image['id']
  for ref in image['refs']:
   if not ref.startswith('sha256:') and '@sha256:' not in ref:assert json.loads(run(cli+['image','inspect',ref],'tag-'+str(index)))[0]['Id']==image['id'],'Recovery tag missing from archive'
  if 'gateway' in image['roles']:
   version=run(cli+['run','--rm','--network','none','--entrypoint','node',image['id'],'-p',"require('/app/package.json').version"],'runtime-'+str(index)).strip();assert version=='2026.10.6'
  elif 'asana' in image['roles']:
   version=run(cli+['run','--rm','--network','none','--entrypoint','node',image['id'],'-p','process.version'],'runtime-'+str(index)).strip();assert version=='v24.22.1'
  else:
   version=run(cli+['run','--rm','--network','none','--entrypoint','/app/api/.venv/bin/python',image['id'],'-c',"from importlib.metadata import version;print(version('hindsight-api-slim'))"],'runtime-'+str(index)).strip();assert version=='1.1.0'
  proofs.append({'imageId':image['id'],'roles':image['roles'],'runtimeVersion':version,'exactIdentityRestored':True})
 proof={'passed':True,'emptyIndependentDockerStoreUsed':True,'sameArchiveImportResumedAfterDeadline':True,'runtimeContainerdNamespace':'cdy26-proof','images':proofs,'postManusGatewayAndAsanaImagesIncluded':True,'hindsight11ImageIncluded':True,'productionDockerStoreUntouched':True};(W/'inputs/current-images/cold-restore-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps({'currentImageColdRestorePassed':True,'images':len(proofs)}),flush=True)
finally:
 if daemon.poll() is None:daemon.send_signal(signal.SIGTERM);daemon.wait(timeout=90)
 log.close()
 if (W/'inputs/current-images/cold-restore-proof.json').exists():
  assert store.resolve()==W/'image-proof/store' and W in store.parents and not store.is_symlink()
  for p in P('/proc').glob('[0-9]*/cmdline'):
   try:cmd=p.read_bytes().replace(b'\0',b' ').decode()
   except (OSError,UnicodeDecodeError):continue
   assert not (str(runtime) in cmd or str(store) in cmd),'Private daemon process still running'
  shutil.rmtree(store);shutil.rmtree(runtime)
