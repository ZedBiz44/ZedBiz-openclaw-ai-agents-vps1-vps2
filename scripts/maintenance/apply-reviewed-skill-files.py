"""Deploy only reviewed package files, refusing local changes since the audit."""
import json,pathlib,hashlib,shutil,os,tempfile,sys
source=pathlib.Path(sys.argv[1]).resolve()
manifest=json.loads(pathlib.Path(sys.argv[2]).read_text())
dest=pathlib.Path('/home/node/.openclaw/workspace/skills')
backup=pathlib.Path('/home/node/.openclaw/workspace/.cody-skill-update-backups-20261003')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
for r in manifest:
 relative=pathlib.PurePosixPath(r['skill'])/r['file']
 if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe relative path')
 live=dest/relative;new=source/relative
 if live.is_symlink() or new.is_symlink():raise ValueError('Unexpected symlink')
 if sha(live)!=r['before']:raise ValueError('Live file changed since review: '+str(relative))
 if sha(new)!=r['after']:raise ValueError('Staged checksum mismatch')
backup.mkdir(parents=True,exist_ok=False)
for r in manifest:
 relative=pathlib.PurePosixPath(r['skill'])/r['file'];live=dest/relative
 if live.exists():
  old=backup/relative;old.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(live,old)
 live.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile(dir=live.parent,delete=False) as f:
  f.write((source/relative).read_bytes());tmp=pathlib.Path(f.name)
 os.chmod(tmp,live.stat().st_mode & 0o777 if live.exists() else 0o644)
 os.replace(tmp,live)
 if sha(live)!=r['after']:raise ValueError('Read-back mismatch')
(backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'skills':len(set(r['skill'] for r in manifest)),'files':len(manifest),'verified':True}))
