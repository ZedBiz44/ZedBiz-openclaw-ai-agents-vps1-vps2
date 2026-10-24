"""Lossless, sequential archive compaction. Never touches live agent state."""
import gzip, hashlib, json, os, pathlib, shutil, subprocess, sys, tarfile, time

ROOT = pathlib.Path('/opt/openclaw/backups/cleanup-20261023')
ROOT.mkdir(mode=0o700, exist_ok=True)
os.umask(0o077)
allowed = [pathlib.Path('/opt/openclaw/backups/fleet-20261018')/a/'before-10.4.tar' for a in
           ['wilma','gohzed','grogar','inga','maggie','marsha','terry','edith','vivian']]
if sys.argv[1]=='historical':
    allowed=[pathlib.Path('/opt/openclaw/backups')/(a+'-20261003-pre-9.8')/('terry-state.tar' if a=='terry' else 'state.tar')
             for a in ['gohzed','grogar','wilma','terry','marsha','inga','amanda','victor','maggie','edith','vivian']]
    allowed += [pathlib.Path('/opt/openclaw/backups')/(a+'-20261017-pre-10.4')/(a+'-offline-state.tar') for a in ['victor','amanda']]
def digest(stream):
    h=hashlib.sha256()
    while b:=stream.read(8*1024*1024): h.update(b)
    return h.hexdigest()
def compact(src):
    assert src in allowed and not src.is_symlink() and src.is_file()
    dst=src.with_suffix('.tar.gz'); tmp=src.with_suffix('.tar.gz.partial')
    assert not dst.exists() and not tmp.exists()
    before=src.stat()
    assert shutil.disk_usage(src.parent).free > before.st_size + 2*1024**3
    print(json.dumps({'phase':'compress','path':str(src),'bytes':before.st_size}),flush=True)
    with src.open('rb') as f: original=digest(f)
    with tmp.open('xb') as out:
        subprocess.run(['nice','-n','15','pigz','-p','2','-3','-c',str(src)],stdout=out,check=True)
        out.flush(); os.fsync(out.fileno())
    with gzip.open(tmp,'rb') as f: restored=digest(f)
    assert restored==original,'Decompressed archive mismatch'
    count=0; sample=None
    with tarfile.open(tmp,'r|gz') as tf:
        for member in tf:
            count+=1
            if sample is None and member.isfile() and 0<member.size<1024*1024:
                content=tf.extractfile(member).read()
                assert len(content)==member.size
                sample={'member':member.name,'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)}
    assert count and sample
    after=src.stat()
    assert (before.st_size,before.st_mtime_ns,before.st_ino)==(after.st_size,after.st_mtime_ns,after.st_ino)
    assert tmp.stat().st_size < before.st_size
    os.chmod(tmp,before.st_mode & 0o777); os.chown(tmp,before.st_uid,before.st_gid)
    tmp.rename(dst)
    with dst.open('rb') as f: compressed=digest(f)
    receipt={'original':str(src),'archive':str(dst),'originalBytes':before.st_size,'compressedBytes':dst.stat().st_size,
             'originalSHA256':original,'decompressedSHA256':restored,'compressedSHA256':compressed,
             'tarEntries':count,'extractionSample':sample,'verifiedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
             'restore':'Use tar -xzf ARCHIVE into a fresh private staging directory; gzip -dc ARCHIVE reconstructs the exact original tar.',
             'status':'verified-before-unlink'}
    receipt_path=src.parent/'archive-compaction-20261023.json'
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    shutil.copy2(receipt_path,ROOT/(src.parent.name+'-archive.json'))
    src.unlink()
    receipt['status']='complete'; receipt['reclaimedBytes']=before.st_size-dst.stat().st_size
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    shutil.copy2(receipt_path,ROOT/(src.parent.name+'-archive.json'))
    print(json.dumps(receipt),flush=True)

selected=allowed if sys.argv[1]=='historical' else allowed[:1] if sys.argv[1]=='pilot' else allowed[1:]
for path in selected:
    if not path.exists() and path.with_suffix('.tar.gz').exists():
        print(json.dumps({'alreadyCompacted':str(path)}),flush=True)
        continue
    compact(path)

