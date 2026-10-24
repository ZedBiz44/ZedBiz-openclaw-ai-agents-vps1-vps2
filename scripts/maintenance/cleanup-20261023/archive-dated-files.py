"""Retire dated loose config/instruction backups; preserve exact recoverable bytes."""
import hashlib,json,os,pathlib,re,subprocess,sys,tarfile,io,time
BASE=pathlib.Path('/opt/openclaw/agents')
OUT=pathlib.Path('/opt/openclaw/backups/cleanup-20261023/loose-files')
NAMES=['amanda','edith','gohzed','grogar','inga','maggie','marsha','terry','victor','vivian','wilma']
def sha(b):return hashlib.sha256(b).hexdigest()
def candidates(a):
    base=BASE/a
    allfiles=[p for d in [base,base/'config',base/'workspace'] for p in d.iterdir() if p.is_file() and not p.is_symlink()]
    selected=[p for p in allfiles if re.search(r'(?:\.bak[-.]|\.backup[-.]|\.before-|\.pre-|\.20\d{6}[-.])',p.name)
              and re.search(r'20\d{2}[-]?\d{2}[-]?\d{2}',p.name)
              and p.stat().st_size<4*1024**2 and p.stat().st_mtime<time.time()-7*86400]
    # Hold files named by current top-level configs, scripts or instructions.
    active=[p for p in allfiles if p not in selected and p.stat().st_size<2*1024**2
            and (p.suffix in ['.py','.sh','.md','.json','.yml'] or p.name.startswith('op-start'))]
    texts=[p.read_bytes() for p in active]
    held=[p for p in selected if any(p.name.encode() in b for b in texts)]
    return [p for p in selected if p not in held],held
def process(a,apply):
    selected,held=candidates(a)
    if not apply:
        print(json.dumps({'agent':a,'count':len(selected),'bytes':sum(p.stat().st_size for p in selected),'held':[str(p) for p in held]}),flush=True);return
    OUT.mkdir(mode=0o700,parents=True,exist_ok=True);os.umask(0o077)
    archive=OUT/(a+'.tar.gz'); receipt=OUT/(a+'.json')
    assert not archive.exists() and not receipt.exists()
    # Exact selected files must not be open in any host process.
    targets={str(p) for p in selected}
    for fd in pathlib.Path('/proc').glob('[0-9]*/fd/*'):
        try: assert os.readlink(fd) not in targets,'Selected backup is open'
        except (FileNotFoundError,PermissionError,OSError):pass
    rows=[]
    for p in selected:
        s=p.stat(); rows.append({'path':str(p),'member':str(p.relative_to(BASE/a)),'sha256':sha(p.read_bytes()),'size':s.st_size,'mode':s.st_mode&0o7777,'uid':s.st_uid,'gid':s.st_gid,'mtime_ns':s.st_mtime_ns,'inode':s.st_ino})
    with tarfile.open(archive,'x:gz') as tf:
        for row in rows:tf.add(row['path'],arcname=row['member'],recursive=False)
    with tarfile.open(archive,'r:gz') as tf:
        assert len(tf.getmembers())==len(rows)
        for row in rows:
            m=tf.getmember(row['member'])
            assert m.isfile() and sha(tf.extractfile(m).read())==row['sha256']
            assert (m.mode,m.uid,m.gid)==(row['mode'],row['uid'],row['gid'])
    for row in rows:
        p=pathlib.Path(row['path']);s=p.stat()
        assert (s.st_ino,s.st_mtime_ns,s.st_size)==(row['inode'],row['mtime_ns'],row['size']) and sha(p.read_bytes())==row['sha256']
    result={'agent':a,'archive':str(archive),'archiveSHA256':sha(archive.read_bytes()),'files':rows,'held':[str(p) for p in held],
            'restore':'Review manifest; extract tar.gz into a private staging directory, then restore the required exact relative path under '+str(BASE/a),
            'status':'verified-before-unlink'}
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    for row in rows:pathlib.Path(row['path']).unlink()
    result['status']='complete';receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'agent':a,'archivedFiles':len(rows),'archive':str(archive),'verifiedEveryFile':True,'held':len(held)}),flush=True)
mode=sys.argv[1]
for a in (NAMES if mode=='plan' else NAMES[:1] if mode=='pilot' else NAMES[1:]):process(a,mode!='plan')

