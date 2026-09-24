"""Install only explicitly named skill packages; verify exact runtime file hashes."""
import sys,json,hashlib,os,stat,tarfile,tempfile
from pathlib import Path

archive,root,*names=sys.argv[1:]
root=Path(root).resolve(strict=True)
assert root.name=='skills',root
with tempfile.TemporaryDirectory(prefix='zedbiz-skill-release-') as tmp:
 stage=Path(tmp)
 with tarfile.open(archive) as tar:
  for member in tar.getmembers():
   out=(stage/member.name).resolve()
   assert stage.resolve() in out.parents and not member.issym() and not member.islnk(),member.name
   if member.isdir():out.mkdir(parents=True,exist_ok=True)
   else:
    assert member.isfile(),member.name
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_bytes(tar.extractfile(member).read())
 manifest=json.loads((stage/'manifest.json').read_text())
 for name in names:
  assert name in manifest and '/' not in name and '..' not in name,name
  dst=root/name
  assert not dst.is_symlink(),dst
  expected=manifest[name]
  previous={}
  if dst.exists():
   assert dst.resolve().parent==root,dst
   for f in dst.rglob('*'):
    assert not f.is_symlink(),f
    if f.is_file():previous[f.relative_to(dst).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
  extras=set(previous)-set(expected)
  allowed_extras={'SKILL.md.before-task-memory-20260916'}
  assert extras<=allowed_extras,('unexpected existing files; inspect before replacing',name,sorted(extras))
  uid,gid=(dst.stat().st_uid,dst.stat().st_gid) if dst.exists() else (root.stat().st_uid,root.stat().st_gid)
  for rel,digest in expected.items():
   src=stage/name/rel;data=src.read_bytes()
   assert hashlib.sha256(data).hexdigest()==digest,(name,rel)
   target=dst/rel;target.parent.mkdir(parents=True,exist_ok=True)
   temp=target.with_name('.'+target.name+'.release')
   temp.write_bytes(data);os.chmod(temp,0o644)
   if os.geteuid()==0:os.chown(temp,uid,gid)
   os.replace(temp,target)
  for d in [dst]+[d for d in dst.rglob('*') if d.is_dir()]:
   os.chmod(d,0o755)
   if os.geteuid()==0:os.chown(d,uid,gid)
  actual={f.relative_to(dst).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in dst.rglob('*') if f.is_file()}
  assert {k:v for k,v in actual.items() if k not in extras}==expected,(name,'verification failed')
  print(json.dumps({'skill':name,'root':str(root),'previous':previous,'installed':actual,'preserved_existing_extras':sorted(extras),'verified':True}),flush=True)
