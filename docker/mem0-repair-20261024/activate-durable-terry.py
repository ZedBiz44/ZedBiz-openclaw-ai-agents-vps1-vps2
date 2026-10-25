"""Idle-gated, backed-up Mem0 package-only Terry repair through managed startup."""
import pathlib,subprocess,json,os,time,shutil,hashlib,sqlite3
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/mem0-repair-20261024-r2');A=W/'terry-activation';live=P('/opt/openclaw/agents/terry');name='terry'
def run(args,label=None,**kw):
 p=subprocess.run(args,capture_output=True,text=True,**kw)
 if label:(A/(label+'.private.log')).write_text(p.stdout+p.stderr)
 return p
def obj(n):return json.loads(subprocess.check_output(['docker','inspect','--type','container',n]))[0]
def sha(p):
 with P(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert json.loads((W/'acceptance.json').read_text())['passed'],'Full plugin/tool acceptance required'
assert len(json.loads((W/'full-starts.json').read_text()))>=2,'Two actual startup-route passes required'
assert not A.exists(),'Inspect previous activation before reuse';A.mkdir(mode=0o700)
def rpc(method,params=None):
 req={'method':method,'params':params or {}}
 r=run(['docker','exec','-i','-e','CODY_RPC_REQUEST='+json.dumps(req),name,'node','--input-type=module'],method,input=(W/'rpc.mjs').read_text(),timeout=75)
 assert r.returncode==0,'RPC gate failed; no stop'
 return json.loads(r.stdout)
d=obj(name);assert d['State']['Health']['Status']=='healthy' and d['RestartCount']==0
active=rpc('status').get('shutdownBudget',{}).get('activeWork');assert active and all(v==0 for v in active.values()),'Active work; retry later without interruption'
cron=rpc('cron.list',{'includeDisabled':True});assert not any(j.get('state',{}).get('runningAtMs') for j in cron['jobs']),'Scheduled work active'
assert shutil.disk_usage(live).free>30*1024**3
projectName=json.loads((W/'clone-project.json').read_text())['projectName'];project=live/'npm/projects'/projectName
assert sha(project/'node_modules/@mem0/openclaw-mem0/dist/index.js')==json.loads((W/'build.json').read_text())['customPluginCodeSha256']
ensure=live/'workspace/ensure-mem0-compat.sh';original=ensure.read_bytes();assert b'verify-mem0-sdk331' not in original
configHash=sha(live/'config/openclaw.json');postHash=sha(live/'workspace/post-start.sh');manifest=P('/opt/openclaw/recovery/fleet-20261018/terry/manifest.json');manifestHash=sha(manifest)
(A/'ensure-before.sh').write_bytes(original);(A/'before.json').write_text(json.dumps({'image':d['Image'],'ref':d['Config']['Image'],'configSha256':configHash,'postStartSha256':postHash,'manifestSha256':manifestHash,'project':str(project),'cron':cron}))
archive=A/'state-before.tar.gz';moved=False;checkpoint=False;activated=False
try:
 assert run(['systemctl','stop','openclaw-terry.service'],'managed-stop',timeout=650).returncode==0
 assert run(['docker','inspect','--type','container',name]).returncode!=0
 assert run(['nice','-n','15','tar','-I','pigz -p 2 -3','-cf',str(archive),'-C',str(live),'.'],'backup',timeout=1800).returncode==0
 assert run(['tar','-tf',str(archive)],'archive-list',timeout=180).returncode==0
 restored=A/'restore-check';restored.mkdir();assert run(['tar','-xf',str(archive),'-C',str(restored),'./config/state','./agents'],'restore-check',timeout=300).returncode==0
 checked=[]
 for p in [restored/'config/state/openclaw.sqlite',*(restored/'agents').glob('*/agent/openclaw-agent.sqlite')]:
  if not p.exists():continue
  with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as db:
   db.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True);assert db.execute('pragma quick_check').fetchall()==[('ok',)]
  checked.append(str(p.relative_to(restored)))
 assert len(checked)==4
 (A/'checkpoint.json').write_text(json.dumps({'archive':str(archive),'sha256':sha(archive),'restoredSqliteChecks':checked}));checkpoint=True
 project.rename(A/'old-project');moved=True;shutil.copytree(W/'project',project,symlinks=True)
 for root,dirs,files in os.walk(project):
  os.chown(root,1000,1000)
  for f in files:os.chown(P(root)/f,1000,1000)
 guard=live/'config/scripts/verify-mem0-sdk331.cjs';assert not guard.exists();guard.write_bytes((W/'mem0-sdk-guard.cjs').read_bytes());os.chown(guard,1000,1000)
 text=original.decode();needle="echo '[mem0-compat]";assert text.count(needle)==1
 text=text.replace(needle,'node /home/node/.openclaw/scripts/verify-mem0-sdk331.cjs "$project_dir"\n'+needle);st=ensure.stat();ensure.write_text(text);os.chown(ensure,st.st_uid,st.st_gid);os.chmod(ensure,st.st_mode&0o777)
 assert sha(live/'config/openclaw.json')==configHash and sha(live/'workspace/post-start.sh')==postHash and sha(manifest)==manifestHash
 assert run(['systemctl','start','openclaw-terry.service'],'managed-start',timeout=1200).returncode==0;activated=True
 (A/'activated.json').write_text(json.dumps({'activated':True,'awaitingLiveAcceptance':True,'imageUnchanged':d['Image'],'configUnchanged':True,'postStartUnchanged':True,'newSdk':'3.3.1','backup':str(archive)}));print(json.dumps({'activated':'terry','sdk':'3.3.1','awaitingLiveAcceptance':True,'verifiedBackup':True}),flush=True)
except BaseException:
 if moved:
  run(['systemctl','stop','openclaw-terry.service'],'rollback-stop',timeout=650)
  if project.exists():project.rename(A/'failed-new-project')
  (A/'old-project').rename(project);ensure.write_bytes(original);os.chown(ensure,1000,1000)
  guard=live/'config/scripts/verify-mem0-sdk331.cjs'
  if guard.exists():guard.rename(A/'failed-sdk-guard.cjs')
 assert run(['systemctl','start','openclaw-terry.service'],'recovery-start',timeout=1200).returncode==0
 raise

