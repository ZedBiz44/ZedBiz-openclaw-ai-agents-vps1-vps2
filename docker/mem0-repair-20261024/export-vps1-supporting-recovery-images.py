"""Preserve custom service images and an allocator filesystem whose original image metadata is unavailable."""
import pathlib,json,subprocess,hashlib,tarfile,os
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/private-recovery-20261024/supporting-images');assert not W.exists();W.mkdir(mode=0o700)
names=['hindsight','z-code-allocator','z-code-admin','z-code-notion-mirror','zedbiz-restart-api','rocky-restart-bridge','rocky-tunnel-bridge'];images={};exports=[]
def stream(args,path,label):
 with path.open('xb') as out,(W/(label+'.private.err')).open('w') as err:
  source=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=err);compress=subprocess.Popen(['nice','-n','15','pigz','-p','2','-3'],stdin=source.stdout,stdout=out,stderr=err);source.stdout.close();assert compress.wait(timeout=1800)==0;assert source.wait(timeout=60)==0
 with tarfile.open(path,'r:gz') as tar:
  members=tar.getmembers();assert members
 with path.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 return {'archive':path.name,'bytes':path.stat().st_size,'sha256':digest,'tarAndGzipTraversed':True,'entries':len(members)}
for name in names:
 d=json.loads(subprocess.check_output(['docker','inspect',name]))[0];r=subprocess.run(['docker','image','inspect',d['Image']],capture_output=True,text=True)
 if r.returncode==0:images[d['Image']]={'imageId':d['Image'],'container':name,'sourceRef':d['Config']['Image']}
 else:
  assert name in ['z-code-allocator','z-code-admin'],'Unexpected missing image; inspect before broad fallback'
  proof=stream(['docker','export',name],W/(name+'-running-rootfs.tar.gz'),name+'-export');proof.update(container=name,originalImageId=d['Image'],currentTag=d['Config']['Image'],method='docker export; bind-mounted data excluded and backed up separately; runtime configuration retained in shared recovery')
  exports.append(proof)
  # Preserve the currently tagged recovery build too, without replacing the running service.
  tagged=json.loads(subprocess.check_output(['docker','image','inspect',d['Config']['Image']]))[0];images[tagged['Id']]={'imageId':tagged['Id'],'container':name,'sourceRef':d['Config']['Image'],'differentFromRunningImage':True}
archive=stream(['docker','image','save',*images.keys()],W/'custom-services-images.tar.gz','save-images')
proof={'passed':True,'archive':archive,'images':list(images.values()),'runningFilesystemExports':exports,'servicesUnchanged':True,'coldLoadNotYetTested':True}
(W/'proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
