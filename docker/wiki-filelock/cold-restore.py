"""Prove recovery from an empty independent Docker/containerd store on VPS1."""
import json,os,pathlib,shutil,signal,subprocess,time
P=pathlib.Path;ROOT=P('/opt/openclaw/recovery/wiki-filelock-20261026');A=ROOT/'restore-proof';A.mkdir(mode=0o700)
runtime=P('/run/wiki-v2-proof');runtime.mkdir(mode=0o700);cs=A/'containerd-store';ds=A/'docker-store';os.umask(0o077)
config=A/'containerd.toml';config.write_text('version = 3\ndisabled_plugins = ["io.containerd.cri.v1.images", "io.containerd.cri.v1.runtime"]\n')
clog=(A/'containerd.private.log').open('w');dlog=(A/'docker.private.log').open('w')
cont=subprocess.Popen(['containerd','--config',str(config),'--root',str(cs),'--state',str(runtime/'containerd'),'--address',str(runtime/'containerd.sock'),'--log-level','warn'],stdout=clog,stderr=subprocess.STDOUT);daemon=None
cli=['docker','--host','unix://'+str(runtime/'docker.sock')]
def run(args,timeout=120):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);assert p.returncode==0,p.stderr[-1000:];return p.stdout
try:
 start=time.monotonic()
 while not (runtime/'containerd.sock').exists():
  assert cont.poll() is None and time.monotonic()-start<90;time.sleep(1)
 dc=A/'daemon.json';dc.write_text(json.dumps({'features':{'containerd-snapshotter':True}}))
 daemon=subprocess.Popen(['dockerd','--config-file',str(dc),'--host',cli[2],'--data-root',str(ds),'--exec-root',str(runtime/'docker'),'--pidfile',str(runtime/'dockerd.pid'),'--bridge','none','--iptables=false','--ip6tables=false','--ip-forward=false','--ip-masq=false','--userland-proxy=false','--containerd',str(runtime/'containerd.sock'),'--containerd-namespace','wiki-v2-proof','--containerd-plugins-namespace','wiki-v2-proof-plugins'],stdout=dlog,stderr=subprocess.STDOUT)
 while True:
  p=subprocess.run(cli+['info','--format','{{json .}}'],capture_output=True,text=True)
  if p.returncode==0:break
  assert daemon.poll() is None and time.monotonic()-start<120;time.sleep(2)
 info=json.loads(p.stdout);assert info['Images']==0 and P(info['DockerRootDir']).resolve()==ds.resolve()
 with (A/'load.private.log').open('w') as out:
  dec=subprocess.Popen(['pigz','-d','-c',str(ROOT/'images.tar.gz')],stdout=subprocess.PIPE)
  loaded=subprocess.run(cli+['load','--quiet'],stdin=dec.stdout,stdout=out,stderr=subprocess.STDOUT,timeout=2400);dec.stdout.close()
  assert dec.wait(timeout=60)==0 and loaded.returncode==0
 proofs=[]
 for image in json.loads((ROOT/'catalog.json').read_text())['images']:
  for ref in image['refs']:assert json.loads(run(cli+['image','inspect',ref]))[0]['Id']==image['id']
  if 'gateway' in image['roles']:
   result=run(cli+['run','--rm','--network','none','--entrypoint','python3',image['id'],'-I','-B','/opt/zedbiz/wiki-lock/verify.py'])
   assert 'descriptor v2 verified' in result
  else:assert run(cli+['run','--rm','--network','none','--entrypoint','node',image['id'],'-p','process.version']).strip()=='v24.22.1'
  proofs.append({'imageId':image['id'],'refs':image['refs'],'exactIdentityRestored':True,'runtimeChecked':True})
 proof={'passed':True,'emptyIndependentDockerAndContainerdStore':True,'productionDockerStoreUntouched':True,'images':proofs}
 (ROOT/'cold-restore-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps({'coldRestorePassed':True,'images':len(proofs)}),flush=True)
finally:
 if daemon is not None and daemon.poll() is None:daemon.send_signal(signal.SIGTERM);daemon.wait(timeout=90)
 if cont.poll() is None:cont.send_signal(signal.SIGTERM);cont.wait(timeout=90)
 clog.close();dlog.close()
 if (ROOT/'cold-restore-proof.json').exists():
  for target in [ds,cs,runtime]:
   assert target.resolve()==target and not target.is_symlink() and (A in target.parents or target==P('/run/wiki-v2-proof'))
   for line in P('/proc/self/mountinfo').read_text().splitlines():assert not line.split()[4].startswith(str(target)+'/')
   for p in P('/proc').glob('[0-9]*/cmdline'):
    try:cmd=p.read_bytes().replace(b'\0',b' ').decode()
    except (OSError,UnicodeDecodeError):continue
    assert str(target) not in cmd
   if target.exists():shutil.rmtree(target)
