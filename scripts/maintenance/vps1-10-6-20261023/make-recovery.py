"""Archive candidate images and prove recovery in an independent Docker store."""
import hashlib,json,os,pathlib,subprocess,sys,time
os.umask(0o077)
root=pathlib.Path('/opt/openclaw/recovery/release-20261023-core')
root.mkdir(mode=0o700,parents=True,exist_ok=True)
refs=['zedbiz/openclaw-base:2026.10.6-core-20261023','zedbiz/asana-http-mcp:2.0.0-components-20261018']
def sha(p):
 with pathlib.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
if sys.argv[1]=='archive':
 archive=root/'images.tar.gz';assert not archive.exists()
 images=[{'ref':ref,'id':json.loads(subprocess.check_output(['docker','image','inspect',ref]))[0]['Id'],'automatic':True} for ref in refs]
 with archive.open('xb') as out:
  save=subprocess.Popen(['docker','image','save',*refs],stdout=subprocess.PIPE)
  compressed=subprocess.run(['nice','-n','15','pigz','-p','2','-3'],stdin=save.stdout,stdout=out)
  save.stdout.close();assert save.wait()==0 and compressed.returncode==0
 catalog={'archive':str(archive),'sha256':sha(archive),'images':images}
 (root/'catalog.json').write_text(json.dumps(catalog,indent=2));print(json.dumps(catalog),flush=True)
elif sys.argv[1]=='prove':
 catalog=json.loads((root/'catalog.json').read_text());assert sha(catalog['archive'])==catalog['sha256']
 p=root/'native-proof';p.mkdir(mode=0o700)
 (p/'daemon.json').write_text('{}')
 (p/'containerd.toml').write_text('version = 3\ndisabled_plugins = ["io.containerd.cri.v1.images", "io.containerd.cri.v1.runtime", "io.containerd.grpc.v1.cri"]\n')
 base=['docker','run','-d','--privileged','--pid=host','--network','none']
 ns=['alpine','nsenter','-t','1','-m','-u','-i','-n','-p','--']
 subprocess.run(base+['--name','release-20261023-containerd-proof']+ns+['/usr/bin/containerd','--config',str(p/'containerd.toml'),'--root',str(p/'containerd-data'),'--state',str(p/'containerd-state'),'--address',str(p/'containerd.sock')],check=True)
 for _ in range(60):
  if (p/'containerd.sock').exists():break
  time.sleep(1)
 else:raise RuntimeError('Isolated containerd unavailable')
 subprocess.run(base+['--name','release-20261023-docker-proof']+ns+['/usr/bin/dockerd','--config-file='+str(p/'daemon.json'),'--data-root='+str(p/'data'),'--exec-root='+str(p/'exec'),'--pidfile='+str(p/'docker.pid'),'--host=unix://'+str(p/'docker.sock'),'--containerd='+str(p/'containerd.sock'),'--feature=containerd-snapshotter=true','--storage-driver=overlayfs','--bridge=none','--iptables=false','--ip6tables=false','--ip-forward=false','--ip-masq=false','--containerd-namespace=release-20261023-proof','--containerd-plugins-namespace=release-20261023-proof-plugins'],check=True)
 docker=['docker','-H','unix://'+str(p/'docker.sock')]
 for _ in range(60):
  if subprocess.run(docker+['info'],capture_output=True).returncode==0:break
  time.sleep(1)
 else:raise RuntimeError('Isolated Docker unavailable')
 assert not subprocess.check_output(docker+['image','ls','-q'],text=True).strip()
 subprocess.run(docker+['image','load','-i',catalog['archive']],check=True,stdout=subprocess.DEVNULL)
 for item in catalog['images']:
  assert subprocess.check_output(docker+['image','inspect','--format','{{.Id}}',item['ref']],text=True).strip()==item['id']
 version=subprocess.check_output(docker+['run','--rm','--network','none','--memory','768m','--entrypoint','node',refs[0],'/app/openclaw.mjs','--version'],text=True)
 assert '2026.10.6' in version
 proof={'archiveSha256':catalog['sha256'],'allImageIdsVerified':True,'restoredVersion':version.strip(),'imageCount':len(refs)}
 (root/'archive-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
 subprocess.run(['docker','stop','release-20261023-docker-proof','release-20261023-containerd-proof'],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['docker','rm','release-20261023-docker-proof','release-20261023-containerd-proof'],check=True,stdout=subprocess.DEVNULL)
else:raise SystemExit('Expected archive or prove')

