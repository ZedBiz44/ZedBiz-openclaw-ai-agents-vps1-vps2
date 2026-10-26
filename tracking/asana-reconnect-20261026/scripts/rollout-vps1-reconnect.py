import json,subprocess,time
from pathlib import Path

GATE=Path('/home/ubuntu/asana-inactivity-results.json')
RESULT=Path('/home/ubuntu/vps1-reconnect-rollout-results.json')
MANIFEST=json.loads(Path('/home/ubuntu/reconnect-private-proof.json').read_text())['patch-manifest.json']
IDLE=Path('/home/ubuntu/reconnect-idle-read.mjs').read_text()
AGENTS=['victor','terry','marsha','edith','vivian','gohzed','grogar','inga','maggie']
GIDS={'victor':'1214049698028551','terry':'1214469570857381','marsha':'1214051396458813','edith':'1215564984542462','vivian':'1214470244795396','gohzed':'1214045726549148','grogar':'1214049698045940','inga':'1214056417378023','maggie':'1214056417379216'}

def remote(code,timeout=600):
 p=subprocess.Popen(['vps-access','-ssh','access','vps1'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 p.stdin.write("python3 - <<'PY'\n"+code+'\nPY\nexit\n');p.stdin.close();lines=[]
 for line in p.stdout:print(line,end='',flush=True);lines.append(line)
 rc=p.wait(timeout=timeout);out=''.join(lines)
 if rc:raise RuntimeError('Remote step stopped; output saved: '+out[-1600:])
 return out

def deploy(a):
 code=r'''
import json,pathlib,subprocess,time,os,stat,hashlib,datetime
os.umask(0o077);a=AGENT;manifest=MANIFEST;idle=IDLE
root=pathlib.Path('/home/jackadmin/victor-mcp-reconnect-20261026/v2') if a=='victor' else pathlib.Path('/home/jackadmin/manus-asana-reconnect-20261026')/a
record=json.loads((root/'candidate-acceptance.json').read_text());assert record['allThreeCandidateImageHashesVerified']
parent=record['parentImage'];parentId=record['parentImageId'];candidate=record['candidateImage'];candidateId=record['candidateImageId']
def inspect(n):return json.loads(subprocess.check_output(['docker','inspect',n],text=True))[0]
def node(s):
 r=subprocess.run(['docker','exec',a,'node','--input-type=module','-e',s],capture_output=True,text=True,timeout=35)
 if r.returncode:raise RuntimeError('Read-only gateway query failed: '+r.stderr[-350:])
 return json.loads(r.stdout)
def settings():
 s="const fs=require('fs'),c=require('crypto');const p=process.env.OPENCLAW_CONFIG_PATH||(process.env.OPENCLAW_STATE_DIR||'/home/node/.openclaw')+'/openclaw.json';const x=JSON.parse(fs.readFileSync(p,'utf8'));const keys=['agents','auth','plugins','mcp','tools','gateway','channels','skills','cron'];console.log(JSON.stringify(Object.fromEntries(keys.map(k=>[k,c.createHash('sha256').update(JSON.stringify(x[k]??null)).digest('hex')]))));"
 r=subprocess.run(['docker','exec',a,'node','-e',s],capture_output=True,text=True,timeout=20);assert r.returncode==0;return json.loads(r.stdout)
def envhash(x):return hashlib.sha256(json.dumps(sorted(x['Config'].get('Env',[]))).encode()).hexdigest()
def safe(d):
 return d.get('activeOnlyQuery') is True and d.get('listReportedTotal')==0 and d.get('listHasMore') is False and d.get('sessions')==[] and not any(x.get('runningAtMs') for x in d.get('jobs',[])) and not any(x.get('busy') or x.get('activeRuns',0) for x in d.get('channels',[])) and all(x.get('running') and x.get('connected') for x in d.get('channels',[]) if x.get('configured') is not False and x.get('enabled') is not False)
before=inspect(a);assert inspect(candidate)['Id']==candidateId,'Candidate changed; stop'
assert before['Image'] in [parentId,candidateId],'Running source image changed; stop'
if before['Image']==candidateId:
 original=root/'manus-deployment.json';assert original.exists(),'Deployed image lacks original receipt; inspect without changes'
 result=json.loads(original.read_text());assert result.get('beforeSettingsHashes') and result.get('beforeEnvironmentHash'),'Original preservation proof missing; stop'
 result['afterSettingsHashes']=settings();result['configurationGroupsUnchanged']=result['beforeSettingsHashes']==result['afterSettingsHashes'];result['afterEnvironmentHash']=envhash(before);result['runtimeEnvironmentUnchanged']=result['beforeEnvironmentHash']==result['afterEnvironmentHash'];result['crashRestarts']=before['RestartCount'];result['readOnlyRecoveryNoNewRestart']=True
 assert result['configurationGroupsUnchanged'] and result['runtimeEnvironmentUnchanged'] and before['RestartCount']==0,'Current preservation differs; stop'
 result['state']='already_deployed_needs_current_acceptance'
else:
 deadline=time.monotonic()+300
 while True:
  d=node(idle)
  if safe(d):break
  if time.monotonic()>deadline:
   print('DEPLOY_BEGIN');print(json.dumps({'agent':a,'state':'busy_or_preexisting_failure_no_change','activeCount':d.get('listReportedTotal'),'root':str(root)}));print('DEPLOY_END');raise SystemExit(0)
  print(a+': waiting for safe idle; no restart yet',flush=True);time.sleep(30)
 (root/'manus-predeployment-idle.json').write_text(json.dumps(d,indent=2)+'\n')
 compose=pathlib.Path('/opt/openclaw/agents/'+a+'/docker-compose.yml');old=compose.read_bytes();backup=root/'docker-compose.before.yml';assert backup.read_bytes()==old,'Compose changed since original backup; stop'
 text=old.decode();assert text.count(parent)==1,'Original image occurrence differs; stop'
 beforeSettings=settings();beforeEnv=envhash(before)
 script=pathlib.Path('/opt/openclaw/agents/'+a+'/op-start-'+a+'.sh').read_text();marker='case "$ACTION" in';assert marker in script and 'op run --env-file .env -- docker compose up -d' in script,'Owning secret-loader format differs; stop'
 prefix=script.split(marker,1)[0];cmd=prefix+'\nop run --env-file .env -- docker compose up -d --no-deps '+a+'\n'
 d=node(idle);assert safe(d),'Agent became active immediately before change; stop'
 assert inspect(a)['Id']==before['Id'] and compose.read_bytes()==old,'Live source changed immediately before deployment; stop'
 updated=text.replace(parent,candidate,1);tmp=compose.with_name(compose.name+'.manus-reconnect');tmp.write_text(updated);tmp.chmod(stat.S_IMODE(compose.stat().st_mode));os.replace(tmp,compose)
 print(a+': installing its tested fix at safe idle',flush=True)
 with (root/'manus-deployment-private.log').open('w') as f:p=subprocess.run(['bash','-c',cmd],stdout=f,stderr=subprocess.STDOUT,timeout=120)
 after=inspect(a);result={'agent':a,'state':'deployed_awaiting_readiness','commandExit':p.returncode,'oldImage':before['Image'],'newImage':after['Image'],'oldContainerId':before['Id'],'newContainerId':after['Id'],'startedUTC':after['State']['StartedAt'],'running':after['State']['Running'],'oom':after['State']['OOMKilled'],'literalOpRefEnvCount':sum('op://' in v for v in after['Config'].get('Env',[])),'composeImageOnlyChange':compose.read_text()==updated,'root':str(root),'backup':str(backup),'beforeSettingsHashes':beforeSettings,'beforeEnvironmentHash':beforeEnv}
 (root/'manus-deployment.json').write_text(json.dumps(result,indent=2)+'\n')
 assert p.returncode==0 and after['Image']==candidateId and after['State']['Running'] and not result['literalOpRefEnvCount'],'Deployment failed; inspect state before controlled rollback'
 deadline=time.monotonic()+360
 while True:
  x=inspect(a);assert x['State']['Running'] and not x['State']['OOMKilled'],'Agent stopped or OOM; stop'
  logs=subprocess.run(['docker','logs','--since',x['State']['StartedAt'],a],capture_output=True,text=True);ready='[gateway] ready' in (logs.stdout+logs.stderr)
  if x['State'].get('Health',{}).get('Status')=='healthy' and ready:break
  if time.monotonic()>deadline:raise RuntimeError('Gateway readiness not established; stop')
  print(a+': waiting for its normal startup',flush=True);time.sleep(15)
 result['afterSettingsHashes']=settings();result['configurationGroupsUnchanged']=result['beforeSettingsHashes']==result['afterSettingsHashes'];result['afterEnvironmentHash']=envhash(x);result['runtimeEnvironmentUnchanged']=beforeEnv==result['afterEnvironmentHash'];result['crashRestarts']=x['RestartCount']
 assert result['configurationGroupsUnchanged'] and result['runtimeEnvironmentUnchanged'],'Settings or runtime environment changed; stop and diagnose'
 assert x['RestartCount']==0,'Unexpected crash restart; stop'
 result['state']='deployed_ready_settings_preserved'
# Read back all loaded files and current core without printing configuration.
s="const fs=require('fs'),c=require('crypto');const rows="+json.dumps(manifest)+";console.log(JSON.stringify({version:JSON.parse(fs.readFileSync('/app/package.json')).version,node:process.version,files:rows.map(x=>({path:x.path,sha256:c.createHash('sha256').update(fs.readFileSync(x.path)).digest('hex')}))}));"
r=subprocess.run(['docker','exec',a,'node','-e',s],capture_output=True,text=True,timeout=20);assert r.returncode==0;loaded=json.loads(r.stdout)
assert loaded['version']=='2026.10.6' and loaded['node']=='v24.22.1' and all(x['sha256']==m['patchedSha256'] for x,m in zip(loaded['files'],manifest)),'Loaded upgrade or patch differs; stop'
result['loaded']=loaded
healthCode=idle.replace("const sessions=await req('sessions.list'", "const currentHealth=await req('health',{});const sessions=await req('sessions.list'").replace("channels,jobs:","health:{ok:currentHealth.ok,eventLoop:currentHealth.eventLoop},channels,jobs:")
check=None
for attempt in range(4):
 try:check=node(healthCode);break
 except RuntimeError:
  if attempt==3:raise
  print(a+': startup settling; repeating only the read-only health query',flush=True);time.sleep(5)
if check.get('health',{}).get('ok') is not True or check.get('health',{}).get('eventLoop',{}).get('degraded'):
 (root/'initial-poststartup-health-warning.json').write_text(json.dumps(check,indent=2)+'\n')
 for attempt in range(3):
  print(a+': preserving initial startup warning; waiting without changes before another health sample',flush=True);time.sleep(15);check=node(healthCode)
  if check.get('health',{}).get('ok') is True and not check.get('health',{}).get('eventLoop',{}).get('degraded'):break
assert check.get('health',{}).get('ok') is True and not check.get('health',{}).get('eventLoop',{}).get('degraded'),'Current health failed; stop'
assert all(x.get('running') and x.get('connected') for x in check['channels'] if x.get('configured') is not False and x.get('enabled') is not False),'Current messaging connection failed; stop'
result['currentHealthAndConnections']=check;result['state']='deployed_static_health_pass_needs_native_reads';(root/'manus-deployment.json').write_text(json.dumps(result,indent=2)+'\n')
print('DEPLOY_BEGIN');print(json.dumps(result));print('DEPLOY_END')
'''.replace('AGENT',repr(a)).replace('MANIFEST',repr(MANIFEST)).replace('IDLE',repr(IDLE))
 out=remote(code);return json.loads(out.split('DEPLOY_BEGIN\n',1)[1].split('\nDEPLOY_END',1)[0])

# Separate helper module contains the read-only actual native feature test.
from reconnect_feature_acceptance import verify_agent

def main():
 gate=json.loads(GATE.read_text());assert {x['agent'] for x in gate}=={'amanda','wilma'} and all(x['state']=='passed_real_expiry_same_session_native_call' for x in gate),'Both actual inactivity passes required; no deployment allowed'
 results=[]
 if RESULT.exists():results=json.loads(RESULT.read_text())
 done={x['agent'] for x in results if x.get('state')=='deployment_and_current_features_pass'}
 for a in AGENTS:
  if a in done:print(a+': preserving saved completed acceptance',flush=True);continue
  r=deploy(a);results.append(r);RESULT.write_text(json.dumps(results,indent=2)+'\n')
  if r['state']=='busy_or_preexisting_failure_no_change':continue
  print(a+': checking actual Asana, Codex Notion and memory reads',flush=True)
  feature=verify_agent(a,GIDS[a]);r['features']=feature
  if feature['state']!='passed_current_features':r['state']='deployment_done_feature_issue_stop';RESULT.write_text(json.dumps(results,indent=2)+'\n');raise RuntimeError(a+': feature acceptance did not pass; stop further rollout')
  r['state']='deployment_and_current_features_pass';RESULT.write_text(json.dumps(results,indent=2)+'\n');print(a+': fix and current features verified',flush=True)
 print(json.dumps([{'agent':x['agent'],'state':x['state']} for x in results],indent=2))
if __name__=='__main__':main()
