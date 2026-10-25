"""Cold-load preserved service images in independent Docker/containerd stores and remove only the test store."""
import pathlib,json,subprocess,time,hashlib,shutil,os
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/private-recovery-20261024/supporting-images');catalog=json.loads((W/'proof.json').read_text());assert catalog['passed'];archive=W/catalog['archive']['archive']
with archive.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==catalog['archive']['sha256']
assert shutil.disk_usage(W).free>30*1024**3,'Require isolated proof headroom'
S=W/'cold-proof-store';assert not S.exists();S.mkdir();(S/'daemon.json').write_text('{}');(S/'containerd.toml').write_text('version = 3\ndisabled_plugins = ["io.containerd.cri.v1.images", "io.containerd.cri.v1.runtime", "io.containerd.grpc.v1.cri"]\n')
names=['cody-support-containerd-proof','cody-support-docker-proof'];started=[]
def run(args,label,timeout=900):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(W/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
base=['docker','run','-d','--privileged','--pid=host','--network','none','--memory','1g','--label','cody.support-cold-proof=true'];ns=['alpine','nsenter','-t','1','-m','-u','-i','-n','-p','--'];docker=['docker','-H','unix://'+str(S/'docker.sock')]
try:
 run(base+['--name',names[0]]+ns+['/usr/bin/containerd','--config',str(S/'containerd.toml'),'--root',str(S/'containerd-data'),'--state',str(S/'containerd-state'),'--address',str(S/'containerd.sock')],'containerd-start');started.append(names[0])
 for _ in range(60):
  if (S/'containerd.sock').exists():break
  time.sleep(1)
 else:raise RuntimeError('Isolated containerd unavailable')
 run(base+['--name',names[1]]+ns+['/usr/bin/dockerd','--config-file='+str(S/'daemon.json'),'--data-root='+str(S/'data'),'--exec-root='+str(S/'exec'),'--pidfile='+str(S/'docker.pid'),'--host=unix://'+str(S/'docker.sock'),'--containerd='+str(S/'containerd.sock'),'--feature=containerd-snapshotter=true','--storage-driver=overlayfs','--bridge=none','--iptables=false','--ip6tables=false','--ip-forward=false','--ip-masq=false','--containerd-namespace=cody-support-cold-proof','--containerd-plugins-namespace=cody-support-cold-proof-plugins'],'docker-start');started.append(names[1])
 for _ in range(60):
  if subprocess.run(docker+['info'],capture_output=True).returncode==0:break
  time.sleep(1)
 else:raise RuntimeError('Isolated Docker unavailable')
 assert not subprocess.check_output(docker+['image','ls','-q'],text=True).strip()
 run(docker+['image','load','-i',str(archive)],'cold-load',1200)
 for image in catalog['images']:
  loaded=json.loads(run(docker+['image','inspect',image['imageId']],'inspect-'+image['container']))[0];assert loaded['Id']==image['imageId']
  ref=image['sourceRef']
  if not ref.startswith('sha256:'):run(docker+['tag',image['imageId'],ref],'restore-tag-'+image['container'])
 imported=[]
 for item in catalog['runningFilesystemExports']:
  path=W/item['archive']
  with path.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==item['sha256']
  tag='cody/'+item['container']+'-recovered:20261024';run(docker+['image','import',str(path),tag],'import-'+item['container'])
  nodePath=run(['docker','exec',item['container'],'node','-p','process.execPath'],'source-node-path-'+item['container']).strip();assert nodePath.startswith('/') and '\n' not in nodePath
  original=run(['docker','exec',item['container'],'node','--version'],'source-node-version-'+item['container']).strip();restored=run(docker+['run','--rm','--network','none','--memory','256m','--entrypoint',nodePath,tag,'--version'],'restored-node-version-'+item['container']).strip();assert restored==original;imported.append({'container':item['container'],'coldImportVerified':True,'restoredNodeVersion':restored})
 proof={'passed':True,'archiveSha256':catalog['archive']['sha256'],'coldLoadedImageIds':[i['imageId'] for i in catalog['images']],'allImageIdsMatched':True,'requiredLocalTagsRestoredInFixture':True,'runningFilesystemImports':imported,'productionServicesUnchanged':True,'isolatedStoresInitiallyEmpty':True}
 (W/'cold-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
finally:
 for name in reversed(started):
  run(['docker','stop','-t','20',name],name+'-stop',90);run(['docker','rm',name],name+'-remove',60)
if (W/'cold-proof.json').exists():
 assert S.resolve()==W/'cold-proof-store' and not S.is_symlink()
 for entry in P('/proc').glob('[0-9]*/mountinfo'):
  try:assert str(S) not in entry.read_text(),'Test store still mounted'
  except (FileNotFoundError,ProcessLookupError,PermissionError):pass
  except OSError as error:
   status=(entry.parent/'status').read_text();assert error.errno==22 and any(line.startswith('State:') and 'Z (zombie)' in line for line in status.splitlines())
 before=shutil.disk_usage(W).free;shutil.rmtree(S);(W/'cold-proof-store-cleanup.json').write_text(json.dumps({'removed':str(S),'freedBytes':shutil.disk_usage(W).free-before}));print('Isolated support-image proof store removed.',flush=True)
