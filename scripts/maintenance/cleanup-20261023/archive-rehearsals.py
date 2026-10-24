"""Archive two obsolete rehearsal trees without discarding their evidence."""
import hashlib,json,os,pathlib,shutil,stat,subprocess,tarfile,time
ROOT=pathlib.Path('/opt/openclaw/backups/cleanup-20261023/rehearsals')
ROOT.mkdir(parents=True,exist_ok=True,mode=0o700);os.umask(0o077)
def digest(f):
 h=hashlib.sha256()
 while b:=f.read(4*1024**2):h.update(b)
 return h.hexdigest()
def no_users(src):
 for p in pathlib.Path('/proc').glob('[0-9]*'):
  for fd in [p/'cwd',p/'root',*p.joinpath('fd').glob('*')]:
   try:target=os.readlink(fd)
   except OSError:continue
   assert target!=str(src) and not target.startswith(str(src)+'/'), 'Active process uses rehearsal'
 ids=subprocess.check_output(['docker','ps','-aq'],text=True).split()
 for d in json.loads(subprocess.check_output(['docker','inspect',*ids])):
  for m in d['Mounts']:
   s=m.get('Source','')
   assert s!=str(src) and not s.startswith(str(src)+'/'), 'Container mounts rehearsal'
for a in ['victor','amanda']:
 src=pathlib.Path('/home/jackadmin')/(a+'-10.4-20261017')/'rehearsal'
 assert src.resolve()==src and src.is_dir() and not src.is_symlink()
 no_users(src)
 dst=ROOT/(a+'.tar.gz');manifest=ROOT/(a+'.json');assert not dst.exists()
 print(json.dumps({'phase':'archivingRehearsal','agent':a}),flush=True)
 rows={}
 for base,dirs,files in os.walk(src,followlinks=False):
  for name in dirs+files:
   p=pathlib.Path(base)/name;s=p.lstat();r={'mode':stat.S_IMODE(s.st_mode),'uid':s.st_uid,'gid':s.st_gid,'mtime_ns':s.st_mtime_ns,'size':s.st_size}
   if p.is_symlink():r.update(type='symlink',target=os.readlink(p))
   elif p.is_file():
    with p.open('rb') as f:r.update(type='file',sha256=digest(f))
   elif p.is_dir():r.update(type='dir')
   else:raise RuntimeError('Unexpected special file')
   rows[str(p.relative_to(src))]=r
 assert shutil.disk_usage(ROOT).free>sum(r['size'] for r in rows.values())+2*1024**3
 with dst.open('xb') as out:
  tar=subprocess.Popen(['nice','-n','15','tar','--hard-dereference','--acls','--xattrs','-cf','-','-C',str(src),'.'],stdout=subprocess.PIPE)
  gzip=subprocess.run(['nice','-n','15','pigz','-p','2','-3'],stdin=tar.stdout,stdout=out)
  tar.stdout.close();assert tar.wait()==0 and gzip.returncode==0
  out.flush();os.fsync(out.fileno())
 seen=set()
 with tarfile.open(dst,'r|gz') as tf:
  for m in tf:
   rel=m.name.removeprefix('./').rstrip('/')
   if rel in ['','.']:continue
   r=rows[rel];seen.add(rel)
   assert (m.mode,m.uid,m.gid)==(r['mode'],r['uid'],r['gid'])
   if r['type']=='file':assert m.isfile() and digest(tf.extractfile(m))==r['sha256']
   elif r['type']=='symlink':assert m.issym() and m.linkname==r['target']
   else:assert m.isdir()
 assert seen==set(rows)
 for rel,r in rows.items():
  p=src/rel;s=p.lstat()
  assert s.st_mtime_ns==r['mtime_ns'] and s.st_size==r['size'],'Rehearsal changed'
 no_users(src)
 with dst.open('rb') as f:archive_sha=digest(f)
 receipt={'source':str(src),'archive':str(dst),'archiveSHA256':archive_sha,'entries':rows,'status':'verified-before-removal',
          'restore':'Extract archive with tar --acls --xattrs -xzf into original empty rehearsal directory; do not overlay production state.'}
 manifest.write_text(json.dumps(receipt,indent=2)+'\n')
 assert src.resolve()==pathlib.Path('/home/jackadmin')/(a+'-10.4-20261017')/'rehearsal'
 shutil.rmtree(src)
 receipt['status']='complete';manifest.write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({'agent':a,'archivedEntries':len(rows),'archiveBytes':dst.stat().st_size,'allContentsVerified':True,'source':str(src)}),flush=True)

