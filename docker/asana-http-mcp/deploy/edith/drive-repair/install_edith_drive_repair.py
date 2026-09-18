from pathlib import Path
import shutil, subprocess, sys

ROOT=Path('/home/node/.openclaw')
S=ROOT/'workspace/scripts'
R=ROOT/'workspace/edith-drive-repair'
def replace(path, old, new):
    text=path.read_text()
    assert old in text, (str(path),old[:80])
    backup=path.with_name(path.name+'.before-drive-repair-20260918')
    if not backup.exists():shutil.copy2(path,backup)
    path.write_text(text.replace(old,new,1))

# Preserve the existing keyring and draft-only wrapper; only copy uses custom GOG.
wrapper=Path('/usr/local/bin/gog').read_text().replace('/opt/openclaw/shared/bin/gog-real',str(R/'gog-edith'))
(R/'gog-copy').write_text(wrapper);(R/'gog-copy').chmod(0o700)
work=ROOT/'private/folder-cleanup/albertawide/work.py'
replace(work," r=subprocess.run(['gog','drive',*args,'--account','jack@zbiz.work','--json','--no-input','--wrap-untrusted'],capture_output=True,text=True,timeout=90)",
''' started=now()
 binary='/home/node/.openclaw/workspace/edith-drive-repair/gog-copy' if args[0]=='copy' else 'gog'
 try:
  r=subprocess.run([binary,'drive',*args,'--account','jack@zbiz.work','--json','--no-input','--wrap-untrusted'],capture_output=True,text=True,timeout=180 if args[0]=='copy' else 90)
 except subprocess.TimeoutExpired:
  r=subprocess.CompletedProcess(args,124,'','Local process timeout; outcome uncertain')''')
replace(work," if r.returncode:raise RuntimeError(r.stderr)",
''' if r.returncode:
  transient=any(x in r.stderr.lower() for x in ('timeout','timed out','connection reset','unexpected eof','500','502','503','504'))
  if args[0]=='copy' and transient:
   from edith_drive_recovery import reconcile
   recovered=reconcile(args,started,_gog)
   if recovered:
    with (P/'operations.jsonl').open('a') as f:f.write(json.dumps({'timestamp':now(),'args':args,'returncode':0,'reconciled':True,'file_id':recovered['file']['id']})+'\\n')
    return recovered
  raise RuntimeError(r.stderr)''')
replace(work,"'--drive',DRIVE,'--max','100']", "'--drive',DRIVE,'--max','100','--fields','files('+FIELDS+'),nextPageToken']")
replace(work,"    m=get(x['id']);assert m.get('driveId')==DRIVE and i in m['parents'];", "    m=dict(x);assert m.get('driveId')==DRIVE and i in m['parents'];")

# Cache evidence bytes only while inode/size/mtime/ctime remain identical.
guard=S/'execution_guard.py'
replace(guard,"def digest(path):\n    return hashlib.sha256(Path(path).read_bytes()).hexdigest()",
'''_digest_cache = {}
def digest(path):
    path = Path(path)
    stat = path.stat()
    signature = (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
    cached = _digest_cache.get(str(path))
    import time
    stable = time.time_ns() - max(stat.st_mtime_ns, stat.st_ctime_ns) > 2_000_000_000
    if stable and cached and cached[0] == signature:
        return cached[1]
    value = hashlib.sha256(path.read_bytes()).hexdigest()
    after = path.stat()
    if signature != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
        raise ValueError('Evidence changed while hashing')
    _digest_cache[str(path)] = (signature, value)
    return value''')

# One paginated destination listing per parent per executor process, updated after
# every own copy. Revalidate existing saved outputs through their normal proof.
pilot=ROOT/'private/folder-cleanup/laughs-and-fun/execute-pilot.py'
replace(pilot,'def copyrow(r):',
'''_destination_names = {}
def destination_names(parent):
 if parent not in _destination_names:
  names=set();token=None
  while True:
   args=['ls','--parent',parent,'--max','100']
   if token:args += ['--page',token]
   listing=gog(*args);names.update(x['name'] for x in listing['files']);token=listing.get('nextPageToken')
   if not token:break
  _destination_names[parent]=names
 return _destination_names[parent]
def copyrow(r):''')
replace(pilot,"  listing=gog('ls','--parent',parent,'--max','100');assert not listing.get('nextPageToken');assert not any(x['name']==name for x in listing['files']), 'Destination collision: reconcile first'",
"  assert name not in destination_names(parent), 'Destination collision: reconcile first'")
replace(pilot,"result=mutate('copy',fid,name,'--parent',parent);did=result['file']['id'];state['pending'][fid]=did;persist()",
"result=mutate('copy',fid,name,'--parent',parent);did=result['file']['id'];_destination_names.setdefault(parent,set()).add(name);state['pending'][fid]=did;persist()")
replace(pilot,"def archive(fid,parent):\n if fid in state['archived']:return",'''def archive(fid,parent):
 if fid in state['archived']:return
 if fid not in state['copies']:
  row=next(r for r in plan['file_plan'] if r['source_id']==fid)
  cid=row.get('active_copy_source_id',fid)
  if cid!=fid and cid in state['copies']:
   from edith_duplicate_proof import make_proof
   canonical=state['copies'][cid];source=get(fid);active=get(canonical['active_id'])
   expected=state['folders'][str(pathlib.PurePosixPath(row['planned_path']).parent)]
   assert active.get('parents')==[expected] and active.get('driveId')==DRIVE
   proof=make_proof(row,orig[fid],source,active,canonical,sig(gog('permissions',fid)),sig(gog('permissions',active['id'])),now())
   save(fid+'-copy-proof.json',proof);state['copies'][fid]=proof;persist()''')
for path in [work,guard,pilot,S/'edith_drive_recovery.py']:
    compile(path.read_text(),str(path),'exec')
print('Installed scoped copy transport, recovery, evidence cache, and per-process destination inventory.')

