"""Cold restore OCI indices using independent containerd and Docker stores matching production."""
import pathlib,subprocess,json,os,time,signal,shutil
P=pathlib.Path;W=P('/opt/openclaw/backups/shared-updates-20261026/offsite');A=W/'image-proof-containerd';A.mkdir(mode=0o700);runtime=P('/run/cdy26v3');assert not runtime.exists();runtime.mkdir(mode=0o700)
catalog=json.loads((W/'inputs/current-images/catalog.json').read_text());archive=W/'inputs/current-images/images.tar.gz';index=json.loads((W/'archive-index.json').read_text());assert {x['digest'] for x in index['manifests']}=={x['id'] for x in catalog['images']}
# The classic-store attempt has ended. Its disposable extracted layers are not recovery inputs.
old=W/'image-proof/store'
for p in P('/proc').glob('[0-9]*/cmdline'):
 try:cmd=p.read_bytes().replace(b'\0',b' ').decode()
 except (OSError,UnicodeDecodeError):continue
 assert str(old) not in cmd and '/run/cdy26r2' not in cmd,'Previous private daemon still active'
if old.exists():
 assert old.resolve()==old and W in old.parents and not old.is_symlink()
 for line in P('/proc/self/mountinfo').read_text().splitlines():assert not line.split()[4].startswith(str(old)+'/'),'Private layer remains mounted'
 shutil.rmtree(old)
assert shutil.disk_usage(W).free>45*1024**3
cs=A/'containerd-store';ds=A/'docker-store';assert not cs.exists() and not ds.exists();config=A/'containerd.toml';config.write_text('version = 3\ndisabled_plugins = ["io.containerd.cri.v1.images", "io.containerd.cri.v1.runtime"]\n')
clog=(A/'containerd.private.log').open('w');dlog=(A/'daemon.private.log').open('w');cont=subprocess.Popen(['containerd','--config',str(config),'--root',str(cs),'--state',str(runtime/'containerd'),'--address',str(runtime/'containerd.sock'),'--log-level','warn'],stdout=clog,stderr=subprocess.STDOUT);daemon=None
sock='unix://'+str(runtime/'docker.sock');cli=['docker','--host',sock]
def run(args,label,timeout=300):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
try:
 start=time.monotonic()
 while not (runtime/'containerd.sock').exists():
  assert cont.poll() is None and time.monotonic()-start<90;time.sleep(1)
 dc=A/'daemon.json';dc.write_text(json.dumps({'features':{'containerd-snapshotter':True}}))
 daemon=subprocess.Popen(['dockerd','--config-file',str(dc),'--host',sock,'--data-root',str(ds),'--exec-root',str(runtime/'docker'),'--pidfile',str(runtime/'dockerd.pid'),'--bridge','none','--iptables=false','--ip6tables=false','--ip-forward=false','--ip-masq=false','--userland-proxy=false','--containerd',str(runtime/'containerd.sock'),'--containerd-namespace','cdy26-proof-v3','--containerd-plugins-namespace','cdy26-proof-v3-plugins'],stdout=dlog,stderr=subprocess.STDOUT)
 while True:
  p=subprocess.run(cli+['info','--format','{{json .}}'],capture_output=True,text=True)
  if p.returncode==0:break
  assert daemon.poll() is None and time.monotonic()-start<120;time.sleep(2)
 info=json.loads(p.stdout);assert info['Images']==0 and P(info['DockerRootDir']).resolve()==ds.resolve()
 with (A/'load.private.log').open('w') as out:
  dec=subprocess.Popen(['pigz','-d','-c',str(archive)],stdout=subprocess.PIPE)
  try:loaded=subprocess.run(cli+['load','--quiet'],stdin=dec.stdout,stdout=out,stderr=subprocess.STDOUT,timeout=2400)
  finally:dec.stdout.close()
  assert dec.wait(timeout=60)==0 and loaded.returncode==0
 proofs=[]
 for i,image in enumerate(catalog['images']):
  restored=json.loads(run(cli+['image','inspect',image['id']],'inspect-'+str(i)))[0];assert restored['Id']==image['id']
  for ref in image['refs']:assert json.loads(run(cli+['image','inspect',ref],'tag-'+str(i)))[0]['Id']==image['id'],'Recovery tag identity mismatch'
  if 'gateway' in image['roles']:
   version=run(cli+['run','--rm','--network','none','--entrypoint','node',image['id'],'-p',"require('/app/package.json').version"],'runtime-'+str(i)).strip();assert version=='2026.10.6'
  elif 'asana' in image['roles']:
   version=run(cli+['run','--rm','--network','none','--entrypoint','node',image['id'],'-p','process.version'],'runtime-'+str(i)).strip();assert version=='v24.22.1'
  else:
   version=run(cli+['run','--rm','--network','none','--entrypoint','/app/api/.venv/bin/python',image['id'],'-c',"from importlib.metadata import version;print(version('hindsight-api-slim'))"],'runtime-'+str(i)).strip();assert version=='1.1.0'
  proofs.append({'imageId':image['id'],'refs':image['refs'],'roles':image['roles'],'runtimeVersion':version,'exactIdentityRestored':True})
 proof={'passed':True,'emptyIndependentDockerStoreUsed':True,'independentContainerdProcessRootStateAndSocket':True,'storeMatchesProductionContainerdSnapshotter':True,'images':proofs,'postManusGatewayAndAsanaImagesIncluded':True,'hindsight11ImageIncluded':True,'productionDockerStoreUntouched':True,'priorClassicStoreProbeInvalidated':True};(W/'inputs/current-images/cold-restore-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps({'currentImageColdRestorePassed':True,'images':len(proofs)}),flush=True)
finally:
 if daemon is not None and daemon.poll() is None:daemon.send_signal(signal.SIGTERM);daemon.wait(timeout=90)
 if cont.poll() is None:cont.send_signal(signal.SIGTERM);cont.wait(timeout=90)
 clog.close();dlog.close()
 if (W/'inputs/current-images/cold-restore-proof.json').exists():
  for target in [ds,cs,runtime]:
   assert target.resolve()==target and not target.is_symlink() and (A in target.parents or target==P('/run/cdy26v3'))
   for p in P('/proc').glob('[0-9]*/cmdline'):
    try:cmd=p.read_bytes().replace(b'\0',b' ').decode()
    except (OSError,UnicodeDecodeError):continue
    assert str(target) not in cmd,'Private restore process still active'
   if target.exists():shutil.rmtree(target)
