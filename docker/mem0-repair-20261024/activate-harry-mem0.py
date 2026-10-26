"""Backed-up native Harry Mem0 project cutover; preserve HTTPS and all agent settings."""
import pathlib,json,subprocess,os,time,shutil,sqlite3,hashlib
P=pathlib.Path;os.umask(0o077);W=P('/root/cody-mem0-repair-20261024');state=P('/root/.openclaw-harry');app=P('/opt/openclaw-harry');A=W/'activation';assert not A.exists();A.mkdir(mode=0o700)
assert json.loads((W/'sdk-memory-proof.json').read_text())['passed'];stage=json.loads((W/'stage.json').read_text());assert stage['staged']
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def run(args,label,**kw):
 p=subprocess.run(args,capture_output=True,text=True,**kw);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
env=None
for proc in P('/proc').glob('[0-9]*'):
 try:
  if (proc/'comm').read_text().strip()!='openclaw-gatewa':continue
  e=dict(v.split('=',1) for v in (proc/'environ').read_text().split('\0') if '=' in v)
  if e.get('OPENCLAW_STATE_DIR')==str(state):env=e;break
 except (OSError,UnicodeError):pass
assert env
def rpc(method,params=None):
 e=env.copy();e['CODY_RPC_REQUEST']=json.dumps({'method':method,'params':params or {}});return json.loads(run(['node',str(W/'rpc.mjs')],method,env=e,timeout=90))
start=time.monotonic()
while True:
 active=rpc('status').get('shutdownBudget',{}).get('activeWork');assert active
 cron=rpc('cron.list',{'includeDisabled':True})
 if all(v==0 for v in active.values()) and not any(j.get('state',{}).get('runningAtMs') for j in cron['jobs']):break
 assert time.monotonic()-start<1200,'Agent remained busy';time.sleep(20)
(A/'cron-before.json').write_text(json.dumps(cron))
cfg=state/'openclaw.json';configHash=sha(cfg);guard=app/'ensure-mem0-110-compat.sh';starter=app/'start-harry.sh'
projects=list((state/'npm/projects').glob('mem0-*/node_modules/@mem0/openclaw-mem0/package.json'));assert len(projects)==1;project=projects[0].parents[3]
assert sha(project/'node_modules/@mem0/openclaw-mem0/dist/index.js')=='0e7205db54c8790c1aff7b09786ec0b7578db08181b5394a7137df4e530297c2'
assert shutil.disk_usage(state).free>10*1024**3+int(subprocess.check_output(['du','-sb',str(state)],text=True).split()[0])
shutil.copy2(guard,A/'compat-before.sh');shutil.copy2(starter,A/'starter-before.private.sh');before={'configSha256':configHash,'starterSha256':sha(starter),'project':str(project),'guardSha256':sha(guard)};(A/'before.json').write_text(json.dumps(before))
print(json.dumps({'agent':'harry','phase':'managed-stop'}),flush=True);run(['systemctl','stop','openclaw-harry'],'stop',timeout=120)
assert subprocess.run(['systemctl','is-active','openclaw-harry'],capture_output=True,text=True).stdout.strip()=='inactive'
print(json.dumps({'agent':'harry','phase':'offline-backup'}),flush=True);archive=A/'state-before.tar.gz'
run(['tar','-czf',str(archive),'-C',str(state),'.'],'backup',timeout=2400)
restore=A/'restore-check';restore.mkdir();run(['tar','-xf',str(archive),'-C',str(restore),'./state','./agents'],'restore-check',timeout=600)
checked=[]
for p in restore.rglob('*.sqlite'):
 with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as db:
  db.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True);assert db.execute('pragma quick_check').fetchall()==[('ok',)]
 checked.append(str(p.relative_to(restore)))
assert checked
(A/'checkpoint.json').write_text(json.dumps({'archive':str(archive),'sha256':sha(archive),'sqliteChecks':checked}))
project.rename(A/'old-project');shutil.copytree(W/'project',project,symlinks=True)
peer=app/'node_modules/openclaw/dist/plugin-peer-link-Cq6_4lfP.mjs';assert sha(peer)==stage['peerModuleSha256']
code="import fs from 'node:fs'; const {a:link}=await import('"+str(peer)+"');const host='"+str(app/'node_modules/openclaw')+"';const root=process.argv[1];const r=await link({installedDir:root,peerDependencies:{openclaw:'2026.10.6'},hostRoot:host,logger:console});if(r.skipped||fs.realpathSync(root+'/node_modules/openclaw')!==host)throw Error('Native peer link failed');"
run(['node','--input-type=module','-e',code,str(project)],'native-peer-link',timeout=90)
sdkGuard=app/'verify-mem0-sdk331.cjs';shutil.copy2(W/'mem0-sdk-guard.cjs',sdkGuard)
patches=json.loads((W/'https-patches.json').read_text());httpsGuard=app/'verify-mem0-https.cjs'
httpsGuard.write_text("const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');const root=process.argv[2];for(const p of "+json.dumps(patches)+"){assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p.file))).digest('hex'),p.after)}console.log('Harry HTTPS port fix verified.');\n")
guard.write_text('#!/usr/bin/env bash\nset -euo pipefail\nif [[ "${1:-}" == "--auto" ]]; then\n project_dir="'+str(project)+'"\nelse\n project_dir="$1"\nfi\nnode '+str(sdkGuard)+' "$project_dir"\nnode '+str(httpsGuard)+' "$project_dir"\n')
os.chmod(guard,0o755);run([str(guard),'--auto',str(state)],'new-startup-guard',timeout=60)
assert sha(cfg)==configHash and sha(starter)==before['starterSha256']
print(json.dumps({'agent':'harry','phase':'managed-start'}),flush=True);run(['systemctl','start','openclaw-harry'],'start',timeout=120)
(A/'activated.json').write_text(json.dumps({'activated':True,'awaitingAcceptance':True,'project':str(project),'sdk':'3.3.1','httpsFixPreserved':True,'configurationUnchanged':True}));print(json.dumps({'harryActivated':True,'awaitingAcceptance':True}),flush=True)

