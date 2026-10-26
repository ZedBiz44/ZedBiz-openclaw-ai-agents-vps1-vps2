import json,subprocess,base64
from pathlib import Path

GATE=Path('/home/ubuntu/asana-inactivity-results.json')
RESULT=Path('/home/ubuntu/native-reconnect-rollout-results.json')
ROOTS={'frank':('vps2','/opt/openclaw-frank/node_modules/openclaw','/root/.openclaw-frank'),'harry':('vps2','/opt/openclaw-harry/node_modules/openclaw','/root/.openclaw-harry'),'suzy':('vps2','/opt/openclaw-suzy/node_modules/openclaw','/root/.openclaw-suzy'),'rocky':('vps4','/home/openclaw/.npm-global/lib/node_modules/openclaw','/home/openclaw/.openclaw')}

REMOTE=r'''
import subprocess,pathlib,json,os,time,hashlib,stat,shutil,datetime,sqlite3,ctypes,ctypes.util,re
os.umask(0o077);a=AGENT;root=pathlib.Path(ROOTPATH);state=pathlib.Path(STATEPATH);candidate=base64=__import__('base64').b64decode(CANDIDATE64)
expectedOld='1abddd912cab692e7e64105643f86f43d14b4fb0756bd1d3f32fe28b70dfc83d';expectedNew='bd6edaa247a62a902bd9c10e18e349580d3735d75f7ae8fd82597834ab5a5372';assert hashlib.sha256(candidate).hexdigest()==expectedNew
p=root/'dist/agents/agent-bundle-mcp-runtime.js';unit='openclaw-gateway.service' if a=='rocky' else 'openclaw-'+a+'.service'
prefix=['runuser','-u','openclaw','--','env','XDG_RUNTIME_DIR=/run/user/1000','DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus'] if a=='rocky' else []
sc=prefix+['systemctl']+(['--user'] if a=='rocky' else [])
proof=(state/'manus-reconnect-20261026');proof.mkdir(mode=0o700,exist_ok=True)
def sh(x):return hashlib.sha256(x).hexdigest()
def props():return dict(x.split('=',1) for x in subprocess.check_output(sc+['show',unit,'--property=MainPID,NRestarts,ActiveState,SubState,FragmentPath'],text=True).splitlines())
def env():
 pid=int(props()['MainPID']);assert pid>0,'Owning service has no PID'
 e=dict(x.split('=',1) for x in pathlib.Path('/proc/'+str(pid)+'/environ').read_bytes().decode().split('\0') if '=' in x);e['OPENCLAW_STATE_DIR']=str(state);e['OPENCLAW_CONFIG_PATH']=str(state/'openclaw.json');return e
def user():
 if a=='rocky':os.setgroups([]);os.setgid(1000);os.setuid(1000)
def rpc(method,param):
 x=subprocess.run(['node',str(root/'openclaw.mjs'),'gateway','call',method,'--params',json.dumps(param),'--json'],env=env(),preexec_fn=user,capture_output=True,text=True,timeout=45)
 if x.returncode:raise RuntimeError('Owning gateway read failed '+method+': '+x.stderr[-250:])
 start=x.stdout.find('{');assert start>=0,'Gateway JSON absent';return json.JSONDecoder().raw_decode(x.stdout[start:])[0]
def idle():
 s=rpc('sessions.list',{'activeOnly':True,'includeGlobal':True,'includeUnknown':True,'limit':100,'archived':'all'});c=rpc('channels.status',{'probe':False});j=rpc('cron.list',{'includeDisabled':True});channels=[]
 for name,rows in c.get('channelAccounts',{}).items():
  for x in rows:channels.append({'channel':name,'running':x.get('running'),'connected':x.get('connected'),'configured':x.get('configured'),'enabled':x.get('enabled'),'busy':x.get('busy'),'activeRuns':x.get('activeRuns')})
 return {'activeOnlyQuery':True,'totalCount':s.get('totalCount'),'hasMore':s.get('hasMore'),'sessions':[{'hasActiveRun':x.get('hasActiveRun'),'activeRunIds':x.get('activeRunIds')} for x in s.get('sessions',[])],'jobs':[{'id':x.get('id'),'runningAtMs':x.get('state',{}).get('runningAtMs')} for x in j.get('jobs',[])],'channels':channels}
def safe(d):return d['totalCount']==0 and d['hasMore'] is False and d['sessions']==[] and not any(x.get('runningAtMs') for x in d['jobs']) and not any(x.get('busy') or x.get('activeRuns') for x in d['channels']) and all(x.get('running') and x.get('connected') for x in d['channels'] if x.get('configured') is not False and x.get('enabled') is not False)
def settings():
 c=json.loads((state/'openclaw.json').read_text());return {k:sh(json.dumps(c.get(k),sort_keys=True).encode()) for k in ['agents','auth','plugins','mcp','tools','gateway','channels','skills','cron']}
def envhash():return sh(json.dumps({k:v for k,v in env().items() if k not in ['INVOCATION_ID','JOURNAL_STREAM','SYSTEMD_EXEC_PID','MAINPID','MANAGERPID']},sort_keys=True).encode())
old=p.read_bytes();assert sh(old) in [expectedOld,expectedNew],'Native runtime source changed; stop'
originalStats=p.stat();beforeProps=props();beforeSettings=settings();beforeEnv=envhash();unitHash=sh(pathlib.Path(beforeProps['FragmentPath']).read_bytes())
record={'agent':a,'root':str(root),'owningUnit':unit,'beforeProps':beforeProps,'beforeSettings':beforeSettings,'beforeEnvironmentHash':beforeEnv,'backup':str(proof/'agent-bundle-mcp-runtime.before.js'),'oldHash':sh(old),'newHash':expectedNew,'state':'not_deployed'}
if sh(old)==expectedOld:
 deadline=time.monotonic()+300
 while True:
  d=idle()
  if safe(d):break
  if time.monotonic()>deadline:record.update(state='busy_or_preexisting_failure_no_change',idle=d);print('NATIVE_BEGIN');print(json.dumps(record));print('NATIVE_END');raise SystemExit(0)
  print(a+': waiting for safe idle; no file change or restart',flush=True);time.sleep(30)
 (proof/'idle-before.json').write_text(json.dumps(d,indent=2)+'\n')
 backup=proof/'agent-bundle-mcp-runtime.before.js'
 if backup.exists():assert backup.read_bytes()==old,'Existing backup differs; stop'
 else:shutil.copy2(p,backup);os.chown(backup,originalStats.st_uid,originalStats.st_gid)
 assert safe(idle()),'Agent became active before change; stop'
 assert p.read_bytes()==old and props()['MainPID']==beforeProps['MainPID'],'Owning source changed before patch; stop'
 tmp=p.with_name(p.name+'.manus-reconnect.tmp');fd=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,stat.S_IMODE(originalStats.st_mode))
 with os.fdopen(fd,'wb') as f:f.write(candidate);f.flush();os.fsync(f.fileno())
 os.chown(tmp,originalStats.st_uid,originalStats.st_gid);os.chmod(tmp,stat.S_IMODE(originalStats.st_mode))
 x=subprocess.run(['node','--check','--input-type=module'],input=candidate.decode(),capture_output=True,text=True)
 assert x.returncode==0,'Candidate syntax failed; live file unchanged'
 os.replace(tmp,p);assert sh(p.read_bytes())==expectedNew and p.stat().st_uid==originalStats.st_uid and p.stat().st_gid==originalStats.st_gid and stat.S_IMODE(p.stat().st_mode)==stat.S_IMODE(originalStats.st_mode),'Installed file metadata differs; stop'
 record['state']='patched_awaiting_restart';(proof/'deployment.json').write_text(json.dumps(record,indent=2)+'\n')
 print(a+': applying the tested native fix and restarting only '+unit,flush=True)
 x=subprocess.run(sc+['restart',unit],capture_output=True,text=True,timeout=90);assert x.returncode==0,'Owning restart failed; inspect exact state before rollback'
 deadline=time.monotonic()+360
 while True:
  new=props()
  if new['ActiveState']=='failed':raise RuntimeError('Owning service failed; stop')
  if int(new['MainPID'])>0:
   try:
    h=rpc('health',{})
    if h.get('ok') is True and not h.get('eventLoop',{}).get('degraded'):break
   except Exception:pass
  if time.monotonic()>deadline:raise RuntimeError('Native readiness not established; stop')
  print(a+': waiting for its normal startup',flush=True);time.sleep(15)
else:
 print(a+': existing refined patch retained; verifying current acceptance',flush=True);new=props();h=rpc('health',{})
record['afterProps']=props();record['configurationGroupsUnchanged']=settings()==beforeSettings;record['runtimeEnvironmentUnchanged']=envhash()==beforeEnv;record['owningUnitUnchanged']=sh(pathlib.Path(record['afterProps']['FragmentPath']).read_bytes())==unitHash
assert record['configurationGroupsUnchanged'] and record['runtimeEnvironmentUnchanged'] and record['owningUnitUnchanged'],'Native settings/env/unit changed; stop'
assert int(record['afterProps']['NRestarts'])==int(beforeProps['NRestarts']),'New automatic crash restart; stop'
assert json.loads((root/'package.json').read_text())['version']=='2026.10.6' and sh(p.read_bytes())==expectedNew,'Native upgrade or patch differs; stop'
record['version']='2026.10.6';record['node']=subprocess.check_output(['node','--version'],text=True).strip();assert record['node']=='v24.22.1'
c=rpc('channels.status',{'probe':True});channels=[]
for name,rows in c.get('channelAccounts',{}).items():
 for x in rows:
  if x.get('configured') is False or x.get('enabled') is False:continue
  channels.append({'channel':name,'running':x.get('running'),'connected':x.get('connected'),'probeOk':x.get('probe',{}).get('ok'),'auditOk':x.get('audit',{}).get('ok')})
assert all(x['running'] and x['connected'] and x['probeOk'] and x['auditOk'] is not False for x in channels),'Native channel check failed; stop'
record['channels']=channels;record['currentHealthOk']=h.get('ok') is True
KEY='agent:main:manus-native-reconnect-rollout-acceptance-20261026'
def transcript():
 db=sqlite3.connect('file:'+str(state/'agents/main/agent/openclaw-agent.sqlite')+'?mode=ro',uri=True);row=db.execute('select current_session_id from session_nodes where session_key=?',(KEY,)).fetchone();result={'sessionId':row[0] if row else None,'tools':[],'final':None}
 if row:
  for seq,s,z in db.execute('select seq,event_json,event_zstd from transcript_events where session_id=? order by seq',(row[0],)):
   if not s and z:
    lib=ctypes.CDLL(ctypes.util.find_library('zstd'));lib.ZSTD_getFrameContentSize.restype=ctypes.c_ulonglong;lib.ZSTD_decompress.restype=ctypes.c_size_t;src=ctypes.create_string_buffer(z);size=lib.ZSTD_getFrameContentSize(src,len(z))
    if size>16*1024*1024:continue
    dest=ctypes.create_string_buffer(size);n=lib.ZSTD_decompress(dest,size,src,len(z));s=dest.raw[:n].decode()
   if not s:continue
   d=json.loads(s);m=d.get('message',d);content=m.get('content',[]);content=[{'text':content}] if isinstance(content,str) else content;text='\n'.join(str(x.get('text','')) for x in content if isinstance(x,dict));calls=[x.get('name') for x in content if isinstance(x,dict) and x.get('type') in ['toolCall','tool_use']]
   if m.get('toolName'):result['tools'].append({'seq':seq,'name':m['toolName'],'isError':m.get('isError',False),'workspaceMatched':'11298561585567' in text,'technicalDocumentationMatched':'Technical Documentation' in text,'resultChars':len(text)})
   if m.get('role')=='assistant' and text and not calls:result['final']=text[-1600:]
 db.close();return result
initial=transcript()
if not initial['final'] or 'NATIVE_ROLLOUT_FEATURE_CHECK_COMPLETE' not in initial['final']:
 msg=('Read-only post-reconnect-fix acceptance requested by Jack. Keep your existing model, Codex login, approved Asana credentials and identity. Use normal approved discovery. Perform one actual native Asana asana_get_user me call and verify your EXISTING approved identity according to your current instructions and workspace11298561585567. Do not substitute another identity, provider or a raw API call. Fetch Technical Documentation https://www.notion.so/7a1a3e33d58183e3ae0201de59538c3e through your existing Codex-connected Notion tool. Read existing ZedBiz memories through the installed memory_recall or equivalent approved memory read. Do not quote records. No edits, memory writes, task writes, journals, files, external messages, delegation, setting changes or replay of failed operations. Return ASANA_PASS/FAIL, NOTION_PASS/FAIL, MEMORY_READ_PASS/FAIL and sanitized failures only. Finish NATIVE_ROLLOUT_FEATURE_CHECK_COMPLETE.')
 accepted=rpc('agent',{'agentId':'main','message':msg,'sessionKey':KEY,'deliver':False,'timeout':0,'idempotencyKey':'manus-'+a+'-native-reconnect-rollout-acceptance-20261026'});record['requestStatus']=accepted.get('status');print(a+': actual native read-only checks accepted',flush=True)
 deadline=time.monotonic()+240
 while True:
  current=transcript()
  if current['final'] and 'NATIVE_ROLLOUT_FEATURE_CHECK_COMPLETE' in current['final']:break
  if time.monotonic()>deadline:raise RuntimeError('Native current feature result still pending; no replay; stop')
  print(a+': '+str(len(current['tools']))+' saved tool results',flush=True);time.sleep(10)
else:current=initial
record['features']=current;tools=current['tools'];final=current['final'] or ''
asana=[x for x in tools if x['name']=='asana.asana_get_user'];notion=[x for x in tools if x['name']=='codex_apps.notion.fetch'];memory=[x for x in tools if 'memory_recall' in x['name'] or ('memory' in x['name'] and any(s in x['name'] for s in ['search','recall','retrieve']))]
passed=len(asana)==1 and not asana[0]['isError'] and asana[0]['workspaceMatched'] and any(not x['isError'] and x['technicalDocumentationMatched'] for x in notion) and any(not x['isError'] for x in memory) and all(x in final for x in ['ASANA_PASS','NOTION_PASS','MEMORY_READ_PASS'])
record['state']='deployment_and_current_features_pass' if passed else 'deployment_done_feature_issue_stop';(proof/'deployment.json').write_text(json.dumps(record,indent=2)+'\n');print('NATIVE_BEGIN');print(json.dumps(record));print('NATIVE_END')
if not passed:raise SystemExit(4)
'''

def main():
 gate=json.loads(GATE.read_text());assert {x['agent'] for x in gate}=={'amanda','wilma'} and all(x['state']=='passed_real_expiry_same_session_native_call' for x in gate),'Two real inactivity passes required'
 results=json.loads(RESULT.read_text()) if RESULT.exists() else [];done={x['agent'] for x in results if x.get('state')=='deployment_and_current_features_pass'}
 for a,(server,root,state) in ROOTS.items():
  if a in done:continue
  candidate=Path('/home/ubuntu/reconnect-native-prep/candidate/'+server+'/'+a+'/dist/agents/agent-bundle-mcp-runtime.js').read_bytes()
  code=REMOTE.replace('AGENT',repr(a)).replace('ROOTPATH',repr(root)).replace('STATEPATH',repr(state)).replace('CANDIDATE64',repr(base64.b64encode(candidate).decode()))
  p=subprocess.Popen(['vps-access','-ssh','access',server],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);p.stdin.write("python3 - <<'PY'\n"+code+'\nPY\nexit\n');p.stdin.close();lines=[]
  for line in p.stdout:print(line,end='',flush=True);lines.append(line)
  rc=p.wait();text=''.join(lines);Path('/home/ubuntu/native-rollout-'+a+'-output.txt').write_text(text)
  if 'NATIVE_BEGIN\n' in text:
   r=json.loads(text.split('NATIVE_BEGIN\n',1)[1].split('\nNATIVE_END',1)[0]);results.append(r);RESULT.write_text(json.dumps(results,indent=2)+'\n')
  if rc:raise RuntimeError(a+': native rollout stopped; inspect saved output before any further change')
  if r['state'] not in ['deployment_and_current_features_pass','busy_or_preexisting_failure_no_change']:raise RuntimeError(a+': unresolved native acceptance; stop')
 print(json.dumps([{'agent':x['agent'],'state':x['state']} for x in results],indent=2))
if __name__=='__main__':main()
