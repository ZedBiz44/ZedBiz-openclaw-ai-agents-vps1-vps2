"""Encrypt, roundtrip-check, and upload verified recovery images directly through existing Drive OAuth."""
import pathlib,json,subprocess,hashlib,shutil,os
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/private-recovery-20261024');R=P('/opt/openclaw/recovery/release-20261024-fleet-tools');catalog=json.loads((R/'catalog.json').read_text());cold=json.loads((R/'archive-proof.json').read_text());key=json.loads((W/'key-receipt.json').read_text())
assert cold['allImageIdsVerified'] and cold['archiveSha256']==catalog['sha256'] and key['keyReadbackVerified']
source=P(catalog['archive']);assert source.is_file();folder='19RU1qtUM-w0k2c66Cpj1im3OPOV3llaZ';name='VPS1-2026-10-24-10.6-recovery-images.tar.gz.age'
stage=P('/opt/openclaw/agents/terry/config/.cody-recovery-upload-20261024');inside='/home/node/.openclaw/.cody-recovery-upload-20261024/'+name
d=json.loads(subprocess.check_output(['docker','inspect','terry']))[0];assert d['State']['Health']['Status']=='healthy'
assert any(m['Source']=='/opt/openclaw/agents/terry/config' and m['Destination']=='/home/node/.openclaw' for m in d['Mounts'])
assert not stage.exists() and not (W/'offsite-images.json').exists();assert shutil.disk_usage(W).free>26*1024**3+source.stat().st_size
def run(args,label,timeout=120):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(W/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
gog=['docker','exec','terry','gog','--account','jack@zbiz.work','--no-input','--json']
def metadata(fileId,label):
 o=json.loads(run(gog+['--readonly','drive','get',fileId,'--fields=id,name,size,md5Checksum,parents,webViewLink'],label));return o.get('file',o)
reference=metadata('1AeZEnR-Petq9DuQdqfs4IWcNn2V8JXfl','drive-key-reference-check');assert folder in reference['parents'] and reference['name']=='VPS1-backup-key-reference.json'
stage.mkdir(mode=0o700);os.chown(stage,1000,1000);encrypted=stage/name
print(json.dumps({'backupPhase':'encrypt-recovery-images','sourceBytes':source.stat().st_size}),flush=True)
with encrypted.open('xb') as out,(W/'encrypt-images.private.log').open('w') as err:r=subprocess.run(['age','-r',key['publicRecipient'],str(source)],stdout=out,stderr=err,timeout=600)
assert r.returncode==0 and encrypted.stat().st_size>source.stat().st_size;os.chown(encrypted,1000,1000)
with encrypted.open('rb') as f:cipherSha=hashlib.file_digest(f,'sha256').hexdigest()
with encrypted.open('rb') as f:cipherMd5=hashlib.file_digest(f,'md5').hexdigest()
with (W/'decrypt-images.private.log').open('w') as err:
 p=subprocess.Popen(['age','--decrypt','--identity',str(W/'age-identity.txt'),str(encrypted)],stdout=subprocess.PIPE,stderr=err)
 plaintextSha=hashlib.file_digest(p.stdout,'sha256').hexdigest();assert p.wait(timeout=60)==0 and plaintextSha==catalog['sha256'],'Decryption roundtrip failed'
print(json.dumps({'backupPhase':'upload-recovery-images','encryptedBytes':encrypted.stat().st_size,'decryptionRoundtripVerified':True}),flush=True)
uploaded=json.loads(run(gog+['drive','upload',inside,'--parent',folder,'--name',name,'--mime-type','application/octet-stream'],'drive-images-upload',3600));uploaded=uploaded.get('file',uploaded);fileId=uploaded['id']
cloud=metadata(fileId,'drive-images-readback');assert cloud['name']==name and folder in cloud['parents'] and cloud['md5Checksum']==cipherMd5 and int(cloud['size'])==encrypted.stat().st_size,'Cloud bytes differ'
proof={'passed':True,'type':'recovery-images','fileId':fileId,'name':name,'folderId':folder,'url':cloud.get('webViewLink'),'bytes':encrypted.stat().st_size,'cipherSha256':cipherSha,'cipherMd5':cipherMd5,'sourceSha256':plaintextSha,'decryptionRoundtripVerified':True,'cloudMd5AndSizeVerified':True,'isolatedDockerRestorePreviouslyVerified':True,'imageCount':len(catalog['images']),'images':catalog['images'],'vault':'z-backups','keyItemTitle':key['title']}
(W/'offsite-images.json').write_text(json.dumps(proof,indent=2));assert encrypted.resolve()==stage/name;encrypted.unlink();stage.rmdir();print(json.dumps({k:v for k,v in proof.items() if k!='images'}),flush=True)

