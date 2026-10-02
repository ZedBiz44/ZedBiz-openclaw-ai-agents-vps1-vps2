#!/usr/bin/env python3
"""Compress only generated, verified rollback archives; retain identical tar bytes."""
import pathlib,sys,gzip,shutil,hashlib,os,json
base=pathlib.Path('/home/jackadmin/openclaw-backups/fleet94-20260912')
allowed={'edith','amanda','marsha','maggie','inga','gohzed','grogar','wilma','wilma-attempt1','victor','vivian'}
for n in sys.argv[1:]:
 assert n in allowed
 b=base/n;src=b/'full-state.tar';dst=b/'full-state.tar.gz';tmp=b/'full-state.tar.gz.part'
 assert b.resolve().parent==base.resolve() and src.is_file() and not src.is_symlink()
 assert not dst.exists() and not tmp.exists()
 expected=(b/'backup.sha256').read_text().strip()
 before=src.stat().st_size
 with open(src,'rb') as inp,open(tmp,'xb') as out:
  os.chmod(tmp,0o600)
  with gzip.GzipFile(filename='',mode='wb',compresslevel=1,fileobj=out,mtime=0) as compressed:shutil.copyfileobj(inp,compressed,1024*1024)
 with gzip.open(tmp,'rb') as restored:actual=hashlib.file_digest(restored,'sha256').hexdigest()
 assert actual==expected,'Restored tar checksum mismatch; originals retained'
 tmp.rename(dst)
 compressed_hash=hashlib.file_digest(open(dst,'rb'),'sha256').hexdigest()
 (b/'compressed-backup.json').write_text(json.dumps({'archive':dst.name,'tarSha256':expected,'gzipSha256':compressed_hash,'originalBytes':before,'compressedBytes':dst.stat().st_size},indent=2)+'\n')
 src.unlink()
 print(json.dumps({'agent':n,'restoredTarChecksumVerified':True,'savedBytes':before-dst.stat().st_size}),flush=True)
