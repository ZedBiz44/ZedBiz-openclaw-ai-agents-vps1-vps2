"""Continue the frozen backup after a separately verified cold import; do not repeat snapshots."""
import pathlib,subprocess,json,os,time,hashlib,shutil,sqlite3,tarfile,urllib.request,urllib.parse,datetime
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/shared-updates-20261026');A=W/'offsite';inputs=A/'inputs'
source=P('/home/jackadmin/vps1-10-6-20261023/backup-updated-services-20261026.py').read_bytes()
assert hashlib.sha256(source).hexdigest()=='6ce1735ad347b51a5b45893ae8a91685e8d52d2f405c5c96d6ab6f5fb0b2c653','Frozen backup source changed'
assert json.loads((inputs/'current-images/cold-restore-proof.json').read_text())['passed']
assert not (A/'offsite.json').exists() and not (A/'VPS1-2026-10-26-shared-services-and-current-images.tar.age').exists()
assert not P('/opt/openclaw/recovery/release-20261026-current-images').exists()
for p in P('/proc').glob('[0-9]*/cmdline'):
 try:args=p.read_bytes().split(b'\0')
 except OSError:continue
 assert not any(x==b'/home/jackadmin/vps1-10-6-20261023/backup-updated-services-20261026.py' for x in args),'Original backup still active'
agents=['terry','marsha','edith','vivian','amanda','victor','wilma','gohzed','grogar','inga','maggie']
containers=json.loads((inputs/'runtime-inspect.private.json').read_text());byName={d['Name'].lstrip('/'):d for d in containers}
current=json.loads(subprocess.check_output(['docker','inspect',*[d['Id'] for d in containers]]))
assert all(d['Id']==byName[d['Name'].lstrip('/')]['Id'] and d['Image']==byName[d['Name'].lstrip('/')]['Image'] for d in current),'Runtime changed after snapshot'
imgDir=inputs/'current-images';archive=imgDir/'images.tar.gz';catalog=json.loads((imgDir/'catalog.json').read_text());images={d['id']:d for d in catalog['images']}
def run(args,label,timeout=300):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);run(['cp','-a',str(src),str(dst)],'copy-'+str(len(list(inputs.iterdir()))))
assert sha(archive)==catalog['archiveSha256']
tail=source.decode().split("recovery=P('/opt/openclaw/recovery/release-20261026-current-images')",1)[1]
exec(compile("recovery=P('/opt/openclaw/recovery/release-20261026-current-images')"+tail,'frozen-backup-closeout','exec'))
