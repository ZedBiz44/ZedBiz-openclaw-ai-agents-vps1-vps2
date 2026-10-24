import os,json,subprocess,shutil,hashlib,sys
from pathlib import Path
os.umask(0o077)
names=['cody-frank-maintenance-20261003','cody-suzy-maintenance-20261003','cody-harry-maintenance-20261003','cody-vps2-20261018','cody-components-20261018','cody-vps2-followup-20261003','openclaw-fleet94-20260912','openclaw-pilot-20260912']
if sys.argv[1:]==['test-only']:names=['/opt/zedbiz-tests/mem0-clean-20260929']
dest=Path('/root/zedbiz-maintenance-archives/2026-10-23');dest.mkdir(parents=True,exist_ok=True,mode=0o700)
record=dest/'manifest.json';results=json.loads(record.read_text()) if record.exists() else []
for name in names:
 source=Path('/root')/name
 if any(r['source']==str(source) for r in results):continue
 assert source.is_dir() and not source.is_symlink() and source.resolve().parent in [Path('/root'),Path('/opt/zedbiz-tests')]
 for proc in Path('/proc').glob('[0-9]*'):
  for link in [proc/'cwd',proc/'exe',*list((proc/'fd').glob('*'))]:
   try:v=os.readlink(link)
   except OSError:continue
   assert not (v==str(source) or v.startswith(str(source)+'/')),'Active reference '+str(link)
 for base in ['/etc/systemd/system','/etc/cron.d']:
  for p in Path(base).rglob('*'):
   if p.is_file():assert str(source) not in p.read_text(errors='ignore'),'Service/schedule reference '+str(p)
 for n in ['frank','harry','suzy']:
  root=Path('/root/.openclaw-'+n)
  assert str(source) not in (root/'openclaw.json').read_text()
  for p in root.rglob('*'):
   if p.is_symlink():assert not p.resolve().is_relative_to(source),'Live symlink '+str(p)
 size=int(subprocess.check_output(['du','-sxB1',str(source)],text=True).split()[0])
 existing=dest/(source.name+'.tar.gz')
 archive=existing if existing.exists() else dest/(source.name+'.tar.zst')
 if archive==existing:
  subprocess.run(['gzip','-t',str(archive)],check=True,timeout=900)
  subprocess.run(['tar','-C','/','-dzf',str(archive)],check=True,timeout=1800)
 else:
  assert not archive.exists()
  subprocess.run(['tar','-C','/','-I','zstd -T2 -1','-cf',str(archive),str(source).lstrip('/')],check=True,timeout=1800)
  subprocess.run(['zstd','-t',str(archive)],check=True,timeout=900)
  subprocess.run(['tar','-C','/','--zstd','-df',str(archive)],check=True,timeout=1800)
 with archive.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 r={'source':str(source),'originalBytes':size,'archive':str(archive),'archiveBytes':archive.stat().st_size,'sha256':digest,'contentCompared':True}
 shutil.rmtree(source);results.append(r);record.write_text(json.dumps(results,indent=2));print(json.dumps(r),flush=True)
