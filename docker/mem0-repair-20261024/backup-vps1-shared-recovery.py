"""Encrypt proven memory snapshots and scoped host/shared recovery inputs; never include the private age key."""
import pathlib,json,subprocess,hashlib,os,tarfile,sqlite3,shutil
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/private-recovery-20261024');A=W/'shared-recovery';assert not A.exists();A.mkdir(mode=0o700)
assert json.loads((W/'hindsight-fresh-proof/proof.json').read_text())['passed'];assert json.loads((W/'qdrant-current-proof/proof.json').read_text())['passed']
key=json.loads((W/'key-receipt.json').read_text());assert key['keyReadbackVerified'];stage=A/'inputs';stage.mkdir()
def run(args,label,timeout=1800):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
names=['hindsight','hindsight-db','mem0-dev-qdrant-1','1password-connect-api','1password-connect-sync','caddy','z-code-allocator','z-code-admin','z-code-notion-mirror','zedbiz-restart-api','rocky-restart-bridge','rocky-tunnel-bridge']
containers=json.loads(subprocess.check_output(['docker','inspect',*names]));(stage/'runtime-inspect.private.json').write_text(json.dumps(containers))
(stage/'networks.private.json').write_bytes(subprocess.check_output(['docker','network','inspect',*subprocess.check_output(['docker','network','ls','-q'],text=True).split()]))
(stage/'installed-packages.txt').write_bytes(subprocess.check_output(['dpkg-query','-W']))
sources=[P(p) for p in ['/etc/systemd/system','/etc/docker','/etc/ssh','/etc/apt','/opt/caddy/Caddyfile','/opt/caddy/docker-compose.yml','/opt/openclaw/shared','/opt/openclaw/1password-connect','/opt/openclaw/services/hindsight/build','/opt/openclaw/services/hindsight/upgrade-0100','/opt/openclaw/services/mem0/server','/opt/zedbiz-services/z-code-allocator','/opt/openclaw/recovery'] if P(p).exists()]
excluded={'backups','node_modules','.git','__pycache__','.cache','history','external-memory'};files={}
def include(p):
 if any(part in excluded for part in p.parts):return False
 if p.name.endswith(('.tar','.tar.gz','.tgz','.age','.dump','.zip','.sqlite-wal','.sqlite-shm','.db-wal','.db-shm')):return False
 if p.is_symlink():return True
 # Live SQLite/Bolt stores are deliberately not copied as ordinary files.
 if p.is_file():
  with p.open('rb') as f:magic=f.read(16)
  if magic.startswith(b'SQLite format 3'):
   target=stage/'sqlite-snapshots'/str(p).lstrip('/');target.parent.mkdir(parents=True,exist_ok=True)
   with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as db,sqlite3.connect(target) as dest:db.backup(dest)
   with sqlite3.connect(target) as db:assert db.execute('pragma quick_check').fetchall()==[('ok',)]
   return False
  return True
 return False
for source in sources:
 for p in source.rglob('*') if source.is_dir() else [source]:
  if include(p):files[str(p).lstrip('/')]=p
for rel in ['hindsight-fresh-proof/before.dump','hindsight-fresh-proof/proof.json','qdrant-current-proof/storage.snapshot','qdrant-current-proof/proof.json','key-receipt.json']:
 files['private-recovery/'+rel]=W/rel
for p in stage.rglob('*'):
 if p.is_file():files['private-recovery/inputs/'+str(p.relative_to(stage))]=p
assert all('age-identity' not in name and 'z-backups-service-account-token' not in name for name in files)
archive=A/'shared-recovery.tar.gz'
with tarfile.open(archive,'w:gz',compresslevel=2) as tar:
 for name,p in files.items():tar.add(p,arcname=name,recursive=False)
with tarfile.open(archive,'r:gz') as tar:
 entries=tar.getmembers();assert len(entries)==len(files)
 for entry in entries:
  if entry.issym():assert entry.linkname==os.readlink(files[entry.name]);continue
  with tar.extractfile(entry) as f,files[entry.name].open('rb') as src:
   assert hashlib.file_digest(f,'sha256').hexdigest()==hashlib.file_digest(src,'sha256').hexdigest()
name='VPS1-2026-10-24-10.6-shared-memory-and-recovery.tar.gz.age';cipher=A/name
with cipher.open('xb') as out,(A/'encrypt.private.err').open('w') as err:r=subprocess.run(['age','-r',key['publicRecipient'],str(archive)],stdout=out,stderr=err,timeout=900)
assert r.returncode==0
with archive.open('rb') as f:plainSha=hashlib.file_digest(f,'sha256').hexdigest()
with (A/'decrypt.private.err').open('w') as err:
 p=subprocess.Popen(['age','-d','-i',str(W/'age-identity.txt'),str(cipher)],stdout=subprocess.PIPE,stderr=err);roundtrip=hashlib.file_digest(p.stdout,'sha256').hexdigest();assert p.wait(timeout=60)==0 and roundtrip==plainSha
uploadStage=P('/opt/openclaw/agents/terry/config/.cody-shared-backup-upload');assert not uploadStage.exists();uploadStage.mkdir(mode=0o700);os.chown(uploadStage,1000,1000);link=uploadStage/name;os.link(cipher,link);os.chown(cipher,1000,1000)
gog=['docker','exec','terry','gog','--account','jack@zbiz.work','--no-input','--json'];folder='19RU1qtUM-w0k2c66Cpj1im3OPOV3llaZ'
try:
 uploaded=json.loads(run(gog+['drive','upload','/home/node/.openclaw/.cody-shared-backup-upload/'+name,'--parent',folder,'--name',name,'--mime-type','application/octet-stream'],'drive-upload',3600));uploaded=uploaded.get('file',uploaded)
 cloud=json.loads(run(gog+['--readonly','drive','get',uploaded['id'],'--fields=id,name,size,md5Checksum,parents,webViewLink'],'drive-readback',180));cloud=cloud.get('file',cloud)
 with cipher.open('rb') as f:md5=hashlib.file_digest(f,'md5').hexdigest()
 with cipher.open('rb') as f:cipherSha=hashlib.file_digest(f,'sha256').hexdigest()
 assert cloud['md5Checksum']==md5 and int(cloud['size'])==cipher.stat().st_size and folder in cloud['parents']
 proof={'passed':True,'fileId':cloud['id'],'url':cloud.get('webViewLink'),'name':name,'bytes':cipher.stat().st_size,'cipherSha256':cipherSha,'cipherMd5':md5,'plaintextSha256':plainSha,'allArchivedFileBytesVerified':len(files),'decryptionRoundtripVerified':True,'cloudMd5AndSizeVerified':True,'hindsightFreshRestoreVerified':True,'qdrantSnapshotRestoreVerified':True,'scope':'shared memory snapshots, runtime credentials/configuration, shared tools and recovery controls; excludes dashboard databases, image archives and private age identity'}
 (A/'offsite.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
finally:
 if link.exists():link.unlink()
 if not any(uploadStage.iterdir()):uploadStage.rmdir()
assert archive.resolve()==A/'shared-recovery.tar.gz';archive.unlink()
