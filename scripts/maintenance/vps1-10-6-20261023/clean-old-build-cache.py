"""Reclaim unused build cache after builds finish; retain all images and volumes."""
import json,pathlib,shutil,subprocess
root=pathlib.Path('/opt/openclaw/backups/release-20261023')
assert len(json.loads((root/'cohort-builds/images.json').read_text()))==6
for p in pathlib.Path('/proc').glob('[0-9]*/cmdline'):
 try:a=p.read_bytes().decode(errors='replace').split('\0')
 except (FileNotFoundError,ProcessLookupError,PermissionError):continue
 assert not (a and pathlib.Path(a[0]).name=='docker' and len(a)>1 and a[1] in ['build','buildx']),'Build still active'
before=shutil.disk_usage('/opt').free
with (root/'old-build-cache-cleanup.log').open('w') as out:
 subprocess.run(['docker','builder','prune','--all','--force'],stdout=out,stderr=subprocess.STDOUT,check=True)
result={'scope':'unused build cache after completed cohort builds','imagesAndVolumesPruned':False,'freeBytesBefore':before,'freeBytesAfter':shutil.disk_usage('/opt').free}
(root/'old-build-cache-cleanup.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
