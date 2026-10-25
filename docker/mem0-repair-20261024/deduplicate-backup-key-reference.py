"""Trash only Cody's duplicate key-reference upload after exact cloud checksum comparison."""
import subprocess,json,pathlib,os
os.umask(0o077);base=['docker','exec','terry','gog','--account','jack@zbiz.work','--no-input','--json'];keep='17Xqakx1la2dy5Hnv1543SwBnGHasMhAB';duplicate='1AeZEnR-Petq9DuQdqfs4IWcNn2V8JXfl'
def get(i):
 p=subprocess.run(base+['--readonly','drive','get',i,'--fields=id,name,size,md5Checksum,parents,trashed'],capture_output=True,text=True,timeout=90);assert p.returncode==0;o=json.loads(p.stdout);return o.get('file',o)
a=get(keep);b=get(duplicate)
assert a['name']==b['name']=='VPS1-backup-key-reference.json' and a['parents']==b['parents']==['19RU1qtUM-w0k2c66Cpj1im3OPOV3llaZ'] and a['size']==b['size'] and a['md5Checksum']==b['md5Checksum']
p=subprocess.run(base+['--force','drive','delete',duplicate],capture_output=True,text=True,timeout=90);assert p.returncode==0
assert get(duplicate)['trashed'] and not get(keep).get('trashed',False)
proof={'kept':keep,'trashedDuplicate':duplicate,'identicalContentVerified':True,'originalDriveSyncFilePreserved':True};pathlib.Path('/opt/openclaw/backups/private-recovery-20261024/key-reference-deduplication.json').write_text(json.dumps(proof));print(json.dumps(proof))

