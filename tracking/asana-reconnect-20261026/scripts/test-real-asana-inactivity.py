import json,subprocess,time
from pathlib import Path

RESULT=Path('/home/ubuntu/asana-inactivity-results.json')
KEY='agent:main:manus-reconnect-feature-check-20261026'
results=[]
def remote(cmd,timeout=60):
 p=subprocess.run(['vps-access','-ssh','access','vps1'],input=cmd+'\nexit\n',text=True,capture_output=True,timeout=timeout)
 if p.returncode:raise RuntimeError(p.stderr[-1000:])
 return p.stdout

def snapshot(a):
 code=r'''
import sqlite3,pathlib,json,ctypes,ctypes.util,os,time,urllib.request
root=pathlib.Path(os.environ.get('OPENCLAW_STATE_DIR','/home/node/.openclaw'))
c=sqlite3.connect('file:'+str(root/'agents/main/agent/openclaw-agent.sqlite')+'?mode=ro',uri=True)
row=c.execute('select current_session_id from session_nodes where session_key=?',(KEY,)).fetchone()
r={'capturedAtMs':int(time.time()*1000),'sessionId':row[0] if row else None,'events':[]}
if row:
 for seq,s,z,at in c.execute('select seq,event_json,event_zstd,created_at from transcript_events where session_id=? order by seq',(row[0],)):
  if not s and z:
   lib=ctypes.CDLL(ctypes.util.find_library('zstd'));lib.ZSTD_getFrameContentSize.restype=ctypes.c_ulonglong;lib.ZSTD_decompress.restype=ctypes.c_size_t;src=ctypes.create_string_buffer(z);size=lib.ZSTD_getFrameContentSize(src,len(z))
   if size>16*1024*1024:continue
   dest=ctypes.create_string_buffer(size);n=lib.ZSTD_decompress(dest,size,src,len(z));s=dest.raw[:n].decode()
  if not s:continue
  d=json.loads(s);m=d.get('message',d);content=m.get('content',[]);content=[{'text':content}] if isinstance(content,str) else content
  text='\n'.join(str(x.get('text','')) for x in content if isinstance(x,dict))
  calls=[x.get('name') for x in content if isinstance(x,dict) and x.get('type') in ['toolCall','tool_use']]
  name=m.get('toolName')
  if name or calls or (m.get('role')=='assistant' and text):
   item={'seq':seq,'at':at,'role':m.get('role'),'tool':name,'calls':calls,'isError':m.get('isError',False)}
   if name=='asana.asana_get_user':item.update(expectedGidMatched=GID in text,expectedWorkspaceMatched='11298561585567' in text)
   if m.get('role')=='assistant' and text and not calls:item['text']=text[-1200:]
   r['events'].append(item)
r['sidecarHealth']=json.load(urllib.request.urlopen('http://ASANA:8080/healthz',timeout=10))
print('SNAP_BEGIN');print(json.dumps(r));print('SNAP_END')
'''.replace('KEY',repr(KEY)).replace('GID',repr('1213974002925107' if a=='amanda' else '1214049698033540')).replace('ASANA',a+'-asana-mcp')
 out=remote('docker exec -i '+a+" python3 - <<'PY'\n"+code+'\nPY')
 return json.loads(out.split('SNAP_BEGIN\n',1)[1].split('\nSNAP_END',1)[0])
for a in ['wilma','amanda']:
 print(a+': checking expired old connection',flush=True)
 before=snapshot(a)
 prior=[e for e in before['events'] if e['tool']=='asana.asana_get_user' and not e['isError']]
 if not prior:raise RuntimeError(a+': previous native Asana call missing')
 last=max(e['at'] for e in prior);ttl=before['sidecarHealth']['sessionTtlMs']
 deadline=time.monotonic()+ttl/1000+180
 observations=[]
 while before['sidecarHealth']['sessions']!=0 or before['capturedAtMs']-last<ttl+65000:
  observations.append({'atMs':before['capturedAtMs'],'sessions':before['sidecarHealth']['sessions']})
  if time.monotonic()>deadline:raise RuntimeError(a+': expiry not established; stop without rollout')
  print(a+': waiting for natural expiry; '+str(before['sidecarHealth']['sessions'])+' connections remain',flush=True)
  time.sleep(60);before=snapshot(a)
 r={'agent':a,'before':before,'expiryObservations':observations,'previousAsanaCallAtMs':last,'idleDurationMs':before['capturedAtMs']-last,'maximumPriorSeq':max(e['seq'] for e in before['events'])}
 msg=('Read-only inactivity test requested by Jack. Resume this SAME existing session after all old Asana connections expired naturally. '
      'Use your NORMAL required tool-discovery procedure to make your existing approved native asana.asana_get_user tool available, then immediately call it once with user_gid me. '
      'Normal read-only catalog discovery is allowed and expected; do not use a raw API, substitute provider, another identity or old result. '
      'Confirm your own expected identity from existing context and workspace11298561585567. Make exactly one native Asana call; no replay. '
      'Do not write tasks, memory, files or journals, send external messages, change any settings or delegate. '
      'Reply ASANA_INACTIVITY_PASS only if the current actual native call succeeds with your own identity; otherwise ASANA_INACTIVITY_FAIL with the sanitized error. Finish INACTIVITY_CHECK_COMPLETE_NORMAL_ROUTE.')
 params={'agentId':'main','message':msg,'sessionKey':KEY,'deliver':False,'timeout':0,'idempotencyKey':'manus-'+a+'-real-asana-inactivity-normal-route-20261026'}
 code="import subprocess,json\np=subprocess.run(['docker','exec',AGENT,'openclaw','gateway','call','agent','--params',PARAM,'--json'],capture_output=True,text=True);print('REQ_BEGIN');print(json.dumps({'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr[-400:]}));print('REQ_END')".replace('AGENT',repr(a)).replace('PARAM',repr(json.dumps(params)))
 out=remote("python3 - <<'PY'\n"+code+'\nPY');request=json.loads(out.split('REQ_BEGIN\n',1)[1].split('\nREQ_END',1)[0]);r['request']=request
 if request['exit']!=0:r['state']='request_failed';results.append(r);RESULT.write_text(json.dumps(results,indent=2)+'\n');break
 print(a+': normal-route same-session request accepted after confirmed expiry',flush=True)
 deadline=time.monotonic()+180
 while True:
  after=snapshot(a);new=[e for e in after['events'] if e['seq']>r['maximumPriorSeq']]
  r['after']=after;r['newEvents']=new
  final=next((e['text'] for e in reversed(new) if 'text' in e and 'INACTIVITY_CHECK_COMPLETE_NORMAL_ROUTE' in e['text']),None)
  if final:
   native=[e for e in new if e['tool']=='asana.asana_get_user']
   passed=after['sessionId']==before['sessionId'] and len(native)==1 and not native[0]['isError'] and native[0].get('expectedGidMatched') and native[0].get('expectedWorkspaceMatched') and after['sidecarHealth']['sessions']>0 and 'ASANA_INACTIVITY_PASS' in final
   r['state']='passed_real_expiry_same_session_native_call' if passed else 'acceptance_failed';print(a+': '+r['state'],flush=True);break
  if time.monotonic()>deadline:r['state']='awaiting_result_no_replay';break
  print(a+': waiting for current native result',flush=True);time.sleep(8)
 results.append(r);RESULT.write_text(json.dumps(results,indent=2)+'\n')
 if not r['state'].startswith('passed_'):break
print(json.dumps([{'agent':r['agent'],'state':r['state'],'idleDurationMs':r['idleDurationMs'],'beforeSessions':r['before']['sidecarHealth']['sessions'],'afterSessions':r.get('after',{}).get('sidecarHealth',{}).get('sessions')} for r in results],indent=2))
if len(results)!=2 or any(not r['state'].startswith('passed_') for r in results):raise SystemExit(3)
