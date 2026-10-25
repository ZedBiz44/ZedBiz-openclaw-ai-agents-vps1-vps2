"""Resume the completed first encrypted archive after correcting the too-early readiness assertion; never restart again."""
import pathlib,json,subprocess,hashlib,os,time,sqlite3,shutil
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/private-recovery-20261024');A=W/'agent-terry';live=P('/opt/openclaw/agents/terry');name='VPS1-2026-10-24-10.6-terry-state.tar.gz.age';cipher=A/name;assert cipher.is_file() and (A/'managed-start.private.log').exists() and not (A/'offsite.json').exists();assert json.loads(P('/opt/openclaw/backups/fleet-10-6-20261024/wave-complete.json').read_text())['completed']
assert not subprocess.check_output(['docker','ps','-q','--filter','label=cody.final-agent-backups=true'],text=True).strip(),'Do not race the old backup controller'
def obj(n):return json.loads(subprocess.check_output(['docker','inspect',n]))[0]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,label,timeout=1800):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
start=time.monotonic()
while True:
 d=obj('terry');assert d['State']['Running'] and not d['State']['OOMKilled']
 if d['State']['Health']['Status']=='healthy':break
 assert time.monotonic()-start<1000;time.sleep(3)
protected={str(p.relative_to(P('/opt/openclaw'))):sha(p) for p in [live/'config/openclaw.json',live/'docker-compose.yml',*live.glob('workspace/*.md')] if p.is_file()};restore=A/'restore-check';assert not restore.exists();restore.mkdir();selected=['agents/terry/config/state','agents/terry/agents',*protected]
with (A/'resume-decrypt.private.err').open('w') as de,(A/'resume-restore.private.err').open('w') as re:
 dec=subprocess.Popen(['age','-d','-i',str(W/'age-identity.txt'),str(cipher)],stdout=subprocess.PIPE,stderr=de);extract=subprocess.Popen(['tar','-xz','-f','-','-C',str(restore),*selected],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=re);h=hashlib.sha256()
 try:
  while True:
   block=dec.stdout.read(1024*1024)
   if not block:break
   h.update(block);extract.stdin.write(block)
  extract.stdin.close();assert dec.wait(timeout=120)==0 and extract.wait(timeout=120)==0;plainSha=h.hexdigest()
 finally:
  for proc in [dec,extract]:
   if proc.poll() is None:proc.kill();proc.wait()
assert all(sha(restore/p)==digest for p,digest in protected.items()),'Protected files changed since snapshot; inspect before proceeding'
checks=[]
for p in [restore/'agents/terry/config/state/openclaw.sqlite',*(restore/'agents/terry/agents').glob('*/agent/openclaw-agent.sqlite')]:
 if p.exists():
  with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as db:
   db.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True);assert db.execute('pragma quick_check').fetchall()==[('ok',)]
  checks.append(str(p.relative_to(restore)))
assert len(checks)==4
stage=live/'config/.cody-current-backup-upload';assert not stage.exists();stage.mkdir(mode=0o700);os.chown(stage,1000,1000);link=stage/name;os.link(cipher,link);os.chown(cipher,1000,1000);gog=['docker','exec','terry','gog','--account','jack@zbiz.work','--no-input','--json'];folder='19RU1qtUM-w0k2c66Cpj1im3OPOV3llaZ'
try:
 uploaded=json.loads(run(gog+['drive','upload','/home/node/.openclaw/.cody-current-backup-upload/'+name,'--parent',folder,'--name',name,'--mime-type','application/octet-stream'],'drive-upload',3600));uploaded=uploaded.get('file',uploaded)
 cloud=json.loads(run(gog+['--readonly','drive','get',uploaded['id'],'--fields=id,name,size,md5Checksum,parents,webViewLink'],'drive-readback',180));cloud=cloud.get('file',cloud)
 with cipher.open('rb') as f:md5=hashlib.file_digest(f,'md5').hexdigest()
 assert cloud['md5Checksum']==md5 and int(cloud['size'])==cipher.stat().st_size and folder in cloud['parents']
 proof={'passed':True,'agent':'terry','fileId':cloud['id'],'url':cloud.get('webViewLink'),'name':name,'bytes':cipher.stat().st_size,'cipherSha256':sha(cipher),'cipherMd5':md5,'plaintextSha256':plainSha,'decryptionRoundtripVerified':True,'selectedRestoreVerified':True,'sqliteChecks':checks,'protectedFilesMatched':len(protected),'externalMemoryFilesMatched':0,'cloudMd5AndSizeVerified':True,'postBackupHealthy':obj('terry')['State']['Health']['Status']=='healthy','image':d['Image'],'resumedAfterReadinessGate':True,'noAdditionalRestartForResume':True,'verification':'Age authentication, full gzip/tar traversal, restored SQLite integrity and unchanged protected live files'};(A/'offsite.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
finally:
 if link.exists():link.unlink()
 if not any(stage.iterdir()):stage.rmdir()
assert restore.resolve()==A/'restore-check';shutil.rmtree(restore)
