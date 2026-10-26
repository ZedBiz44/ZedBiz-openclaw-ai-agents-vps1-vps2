"""Consistent encrypted post-update agent recovery, actual restore checks and Drive read-back."""
import pathlib,json,subprocess,hashlib,os,sys,time,sqlite3,shutil,threading
P=pathlib.Path;os.umask(0o077);agent=sys.argv[1]
assert agent in ['terry','marsha','amanda','victor','wilma','gohzed','grogar','inga','maggie','edith','vivian']
W=P('/opt/openclaw/backups/private-recovery-20261024');A=W/('agent-'+agent);A.mkdir(mode=0o700,exist_ok=True)
assert not (A/'offsite.json').exists(),'Already backed up; inspect existing proof'
assert json.loads((W/'offsite-images.json').read_text())['passed']
F=P('/opt/openclaw/backups/fleet-10-6-20261024');live=P('/opt/openclaw/agents')/agent
if agent!='marsha':
 proof=json.loads((F/agent/'acceptance.json').read_text());assert proof['passed'] and proof['actualMemoryResultValidated']
key=json.loads((W/'key-receipt.json').read_text());assert key['keyReadbackVerified'];base=P('/opt/openclaw')
def run(args,label,timeout=1800,input=None):
 print(json.dumps({'agentBackup':agent,'phase':label}),flush=True)
 p=subprocess.run(args,capture_output=True,text=True,input=input,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
def obj(name):return json.loads(subprocess.check_output(['docker','inspect',name]))[0]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
d=obj(agent);assert d['State']['Health']['Status']=='healthy' and '2026.10.6-tools-full-' in d['Config']['Image']
cfg=json.loads((live/'config/openclaw.json').read_text());external=None
if cfg['plugins']['slots'].get('memory')=='memory-lancedb':
 external=P(cfg['plugins']['entries']['memory-lancedb']['config']['dbPath']);assert external.resolve()==base/'shared/external-memory/lancedb'/agent
rpcCode=P('/opt/openclaw/backups/mem0-repair-20261024-r2/rpc.mjs').read_text()
def rpc(method,params=None):
 return json.loads(run(['docker','exec','-i','-e','CODY_RPC_REQUEST='+json.dumps({'method':method,'params':params or {}}),agent,'node','--input-type=module'],'pre-'+method,120,input=rpcCode))
start=time.monotonic()
while True:
 active=rpc('status').get('shutdownBudget',{}).get('activeWork');assert active
 jobs=rpc('cron.list',{'includeDisabled':True})['jobs']
 if all(v==0 for v in active.values()) and not any(j.get('state',{}).get('runningAtMs') for j in jobs):break
 assert time.monotonic()-start<1200,'Active work; do not interrupt';time.sleep(20)
name='VPS1-2026-10-24-10.6-'+agent+'-state.tar.gz.age';cipher=A/name;assert not cipher.exists()
members=['agents/'+agent]
if external:members.append(str(external.relative_to(base)))
used=int(subprocess.check_output(['du','-sb',str(live)],text=True).split()[0]);assert shutil.disk_usage(W).free>used+8*1024**3,'Insufficient bounded backup headroom'
stopped=False;plaintextSha=None;checks=[];protected={};externalFiles={}
try:
 run(['systemctl','stop','openclaw-'+agent+'.service'],'managed-stop',650);stopped=True
 assert subprocess.run(['docker','inspect',agent],capture_output=True).returncode!=0
 for p in [live/'config/openclaw.json',live/'docker-compose.yml',*live.glob('workspace/*.md')]:
  if p.is_file():protected[str(p.relative_to(base))]=sha(p)
 if external:externalFiles={str(p.relative_to(base)):sha(p) for p in external.rglob('*') if p.is_file()}
 with (A/'tar.private.err').open('w') as te,(A/'age.private.err').open('w') as ae,cipher.open('xb') as out:
  tar=subprocess.Popen(['nice','-n','15','tar','-I','pigz -p 2 -3','-cf','-','-C',str(base),*members],stdout=subprocess.PIPE,stderr=te)
  enc=subprocess.Popen(['age','-r',key['publicRecipient']],stdin=subprocess.PIPE,stdout=out,stderr=ae)
  h=hashlib.sha256()
  try:
   while True:
    block=tar.stdout.read(1024*1024)
    if not block:break
    h.update(block);enc.stdin.write(block)
   enc.stdin.close();assert tar.wait(timeout=120)==0;assert enc.wait(timeout=120)==0;plaintextSha=h.hexdigest()
  finally:
   for proc in [tar,enc]:
    if proc.poll() is None:proc.kill();proc.wait()
 assert cipher.stat().st_size>1024
 (A/'snapshot-metadata.json').write_text(json.dumps({'plaintextSha256':plaintextSha,'protectedFiles':protected,'externalFiles':externalFiles},indent=2))
finally:
 if stopped:run(['systemctl','start','openclaw-'+agent+'.service'],'managed-start',1500)
readinessStart=time.monotonic()
while True:
 current=obj(agent);assert current['State']['Running'] and not current['State']['OOMKilled'] and current['Image']==d['Image'],'Gateway failed after backup restart'
 if current['State'].get('Health',{}).get('Status')=='healthy':break
 assert time.monotonic()-readinessStart<1000,'Gateway readiness deadline after backup';time.sleep(3)
(A/'post-backup-readiness.json').write_text(json.dumps({'healthy':True,'waitedSeconds':round(time.monotonic()-readinessStart,2)}))
restore=A/'restore-check';restore.mkdir();selected=['agents/'+agent+'/config/state','agents/'+agent+'/agents','agents/'+agent+'/config/openclaw.json','agents/'+agent+'/docker-compose.yml']
selected.extend(k for k in protected if '/workspace/' in k)
if external:selected.append(str(external.relative_to(base)))
with (A/'decrypt.private.err').open('w') as de,(A/'restore.private.err').open('w') as re:
 dec=subprocess.Popen(['age','-d','-i',str(W/'age-identity.txt'),str(cipher)],stdout=subprocess.PIPE,stderr=de)
 extract=subprocess.Popen(['tar','-xz','-f','-','-C',str(restore),*selected],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=re)
 h=hashlib.sha256()
 try:
  while True:
   block=dec.stdout.read(1024*1024)
   if not block:break
   h.update(block);extract.stdin.write(block)
  extract.stdin.close();assert dec.wait(timeout=120)==0;assert extract.wait(timeout=120)==0;assert h.hexdigest()==plaintextSha
 finally:
  for proc in [dec,extract]:
   if proc.poll() is None:proc.kill();proc.wait()
assert all(sha(restore/p)==digest for p,digest in protected.items())
for p in [restore/'agents'/agent/'config/state/openclaw.sqlite',*(restore/'agents'/agent/'agents').glob('*/agent/openclaw-agent.sqlite')]:
 if p.exists():
  with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as db:
   db.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True);assert db.execute('pragma quick_check').fetchall()==[('ok',)]
  checks.append(str(p.relative_to(restore)))
assert checks
assert all(sha(restore/p)==digest for p,digest in externalFiles.items())
folder='19RU1qtUM-w0k2c66Cpj1im3OPOV3llaZ';stage=P('/opt/openclaw/agents/terry/config/.cody-current-backup-upload');stage.mkdir(mode=0o700,exist_ok=True);os.chown(stage,1000,1000);link=stage/name;assert not link.exists();os.link(cipher,link);os.chown(cipher,1000,1000)
gog=['docker','exec','terry','gog','--account','jack@zbiz.work','--no-input','--json']
try:
 uploaded=json.loads(run(gog+['drive','upload','/home/node/.openclaw/.cody-current-backup-upload/'+name,'--parent',folder,'--name',name,'--mime-type','application/octet-stream'],'drive-upload',3600));uploaded=uploaded.get('file',uploaded)
 cloud=json.loads(run(gog+['--readonly','drive','get',uploaded['id'],'--fields=id,name,size,md5Checksum,parents,webViewLink'],'drive-readback',180));cloud=cloud.get('file',cloud)
 with cipher.open('rb') as f:md5=hashlib.file_digest(f,'md5').hexdigest()
 assert cloud['md5Checksum']==md5 and int(cloud['size'])==cipher.stat().st_size and folder in cloud['parents']
 proof={'passed':True,'agent':agent,'fileId':cloud['id'],'url':cloud.get('webViewLink'),'name':name,'bytes':cipher.stat().st_size,'cipherSha256':sha(cipher),'cipherMd5':md5,'plaintextSha256':plaintextSha,'decryptionRoundtripVerified':True,'selectedRestoreVerified':True,'sqliteChecks':checks,'protectedFilesMatched':len(protected),'externalMemoryFilesMatched':len(externalFiles),'cloudMd5AndSizeVerified':True,'postBackupHealthy':obj(agent)['State']['Health']['Status']=='healthy','image':d['Image']}
 (A/'offsite.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
finally:
 if link.exists():link.unlink()
 if not any(stage.iterdir()):stage.rmdir()
assert restore.resolve()==A/'restore-check' and not restore.is_symlink();shutil.rmtree(restore)
