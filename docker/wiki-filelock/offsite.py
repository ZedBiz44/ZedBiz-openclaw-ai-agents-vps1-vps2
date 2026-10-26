"""Publish encrypted Wiki rollout overlay using the existing recovery recipient."""
import datetime,hashlib,json,os,pathlib,shutil,subprocess
P=pathlib.Path;ROOT=P('/opt/openclaw/recovery/wiki-filelock-20261026');W=ROOT/'offsite';W.mkdir(mode=0o700);os.umask(0o077)
inventory=json.loads((ROOT/'inventory.json').read_text())
assert all(json.loads((ROOT/(r['agent']+'-acceptance.json')).read_text())['passed'] for r in inventory)
assert json.loads((ROOT/'cold-restore-proof.json').read_text())['passed']
key=json.loads(P('/opt/openclaw/backups/shared-updates-20261026/offsite/key-reference.json').read_text());assert key['passed']
inputs=W/'inputs';inputs.mkdir();images=inputs/'current-images';images.mkdir();os.link(ROOT/'images.tar.gz',images/'images.tar.gz')
for name in ['catalog.json','archive.json','cold-restore-proof.json']:shutil.copy2(ROOT/name,images/name)
for row in inventory:
 base=P('/opt/openclaw/agents')/row['agent']
 for src in [base/'docker-compose.yml',base/'workspace/post-start.sh',base/'config/openclaw.json',P(row['wrapper']),P(row['manifest'])]:
  dest=inputs/'original-paths'/str(src).lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
def sha(p,kind='sha256'):
 with p.open('rb') as f:return hashlib.file_digest(f,kind).hexdigest()
expected={str(p.relative_to(inputs)):sha(p) for p in inputs.rglob('*') if p.is_file()}
(inputs/'content-sha256.json').write_text(json.dumps(expected,indent=2))
name='VPS1-2026-10-26-wiki-filelock-overlay.tar.age';cipher=W/name
with cipher.open('xb') as out,(W/'encrypt.private.log').open('w') as log:
 tar=subprocess.Popen(['tar','-cf','-','-C',str(inputs),'.'],stdout=subprocess.PIPE,stderr=log)
 enc=subprocess.Popen(['age','-r',key['publicRecipient']],stdin=tar.stdout,stdout=out,stderr=log);tar.stdout.close()
 assert enc.wait(timeout=1800)==0 and tar.wait(timeout=60)==0
stage=P('/opt/openclaw/agents/terry/config/.cody-wiki-backup-upload');stage.mkdir(mode=0o700);os.chown(stage,1000,1000);os.link(cipher,stage/name);os.chown(cipher,1000,1000)
gog=['docker','exec','terry','gog','--account','jack@zbiz.work','--no-input','--json'];folder='19RU1qtUM-w0k2c66Cpj1im3OPOV3llaZ'
def call(args,label,timeout=300):
 p=subprocess.run(gog+args,capture_output=True,text=True,timeout=timeout);(W/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';r=json.loads(p.stdout);return r.get('file',r)
try:
 print(json.dumps({'phase':'upload-encrypted-wiki-recovery','bytes':cipher.stat().st_size}),flush=True)
 cloud=call(['drive','upload','/home/node/.openclaw/.cody-wiki-backup-upload/'+name,'--parent',folder,'--name',name,'--mime-type','application/octet-stream'],'upload',3600)
 meta=call(['--readonly','drive','get',cloud['id'],'--fields=id,name,size,md5Checksum,parents,webViewLink'],'readback')
 assert meta['md5Checksum']==sha(cipher,'md5') and int(meta['size'])==cipher.stat().st_size and folder in meta['parents']
 proof={'passed':True,'fileId':meta['id'],'name':name,'url':meta.get('webViewLink'),'bytes':cipher.stat().st_size,'cipherSha256':sha(cipher),'cipherMd5':meta['md5Checksum'],'cloudMd5AndSizeVerified':True,'plaintextImagesColdRestored':13,'encryptedWithExistingVerifiedRecipient':True,'newDecryptionRoundtripPerformed':False,'scope':'Wiki image/configuration overlay only. Apply after the October26 shared-services overlay; existing agent-state and service backups remain required.'}
 (ROOT/'offsite-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
finally:
 (stage/name).unlink();stage.rmdir()
