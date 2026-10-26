import json,subprocess,time,re
from pathlib import Path

KEY='agent:main:manus-asana-reconnect-rollout-acceptance-20261026'

def remote(code,server='vps1',timeout=60):
 p=subprocess.run(['vps-access','-ssh','access',server],input="python3 - <<'PY'\n"+code+'\nPY\nexit\n',text=True,capture_output=True,timeout=timeout)
 if p.returncode:raise RuntimeError('Read-only acceptance query failed: '+p.stderr[-400:])
 return p.stdout

def verify_agent(agent,gid):
 def snapshot():
  code=r'''
import sqlite3,pathlib,json,ctypes,ctypes.util,os,re
root=pathlib.Path(os.environ.get('OPENCLAW_STATE_DIR','/home/node/.openclaw'))
c=sqlite3.connect('file:'+str(root/'agents/main/agent/openclaw-agent.sqlite')+'?mode=ro',uri=True)
row=c.execute('select current_session_id from session_nodes where session_key=?',(KEY,)).fetchone()
r={'sessionId':row[0] if row else None,'tools':[],'final':None,'maxSeq':0,'models':[]}
if row:
 for seq,s,z in c.execute('select seq,event_json,event_zstd from transcript_events where session_id=? order by seq',(row[0],)):
  r['maxSeq']=max(r['maxSeq'],seq)
  if not s and z:
   lib=ctypes.CDLL(ctypes.util.find_library('zstd'));lib.ZSTD_getFrameContentSize.restype=ctypes.c_ulonglong;lib.ZSTD_decompress.restype=ctypes.c_size_t;src=ctypes.create_string_buffer(z);size=lib.ZSTD_getFrameContentSize(src,len(z))
   if size>16*1024*1024:continue
   dest=ctypes.create_string_buffer(size);n=lib.ZSTD_decompress(dest,size,src,len(z));s=dest.raw[:n].decode()
  if not s:continue
  d=json.loads(s);m=d.get('message',d);content=m.get('content',[]);content=[{'text':content}] if isinstance(content,str) else content
  text='\n'.join(str(x.get('text','')) for x in content if isinstance(x,dict));calls=[x.get('name') for x in content if isinstance(x,dict) and x.get('type') in ['toolCall','tool_use']]
  name=m.get('toolName')
  if name:r['tools'].append({'seq':seq,'name':name,'isError':m.get('isError',False),'expectedGidMatched':GID in text,'expectedWorkspaceMatched':'11298561585567' in text,'technicalDocumentationMatched':'Technical Documentation' in text,'resultChars':len(text)})
  if m.get('role')=='assistant':
   if m.get('model'):r['models'].append({'provider':m.get('provider'),'model':m.get('model')})
   if text and not calls:r['final']=text[-1600:]
print('FEATURE_BEGIN');print(json.dumps(r));print('FEATURE_END')
'''.replace('KEY',repr(KEY)).replace('GID',repr(gid))
  wrapper="import subprocess\np=subprocess.run(['docker','exec',AGENT,'python3','-c',CODE],capture_output=True,text=True);assert p.returncode==0,p.stderr[-500:];print(p.stdout)".replace('AGENT',repr(agent)).replace('CODE',repr(code))
  out=remote(wrapper);return json.loads(out.split('FEATURE_BEGIN\n',1)[1].split('\nFEATURE_END',1)[0])
 initial=snapshot()
 if initial['final'] and 'ROLLOUT_FEATURE_CHECK_COMPLETE' in initial['final']:
  events=initial;request={'alreadyCompleted':True}
 else:
  msg=('Read-only post-reconnect-fix acceptance requested by Jack. Keep existing model, Codex login, provider settings and identity. Use normal approved tool discovery and perform actual current reads: '
       'native Asana asana_get_user me exactly once, confirm OWN user GID '+gid+' and workspace11298561585567; '
       'Codex-connected Notion fetch Technical Documentation https://www.notion.so/7a1a3e33d58183e3ae0201de59538c3e; '
       'read existing ZedBiz memories with the installed memory_recall tool or your approved equivalent memory read. Empty memory search may be noted but is not permission to create memories. '
       'No task/Notion/file/memory writes, external messages, delegation, credential/config/model changes, raw Asana API substitute or failed-operation replay. '
       'Return ASANA_PASS or ASANA_FAIL, NOTION_PASS or NOTION_FAIL, MEMORY_READ_PASS or MEMORY_READ_FAIL. Do not quote memory or page content. Explain only sanitized failures. Finish ROLLOUT_FEATURE_CHECK_COMPLETE.')
  params={'agentId':'main','message':msg,'sessionKey':KEY,'deliver':False,'timeout':0,'idempotencyKey':'manus-'+agent+'-reconnect-rollout-acceptance-20261026'}
  code="import subprocess,json\np=subprocess.run(['docker','exec',AGENT,'openclaw','gateway','call','agent','--params',PARAM,'--json'],capture_output=True,text=True);print('REQUEST_BEGIN');print(json.dumps({'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr[-400:]}));print('REQUEST_END')".replace('AGENT',repr(agent)).replace('PARAM',repr(json.dumps(params)))
  out=remote(code);request=json.loads(out.split('REQUEST_BEGIN\n',1)[1].split('\nREQUEST_END',1)[0])
  if request['exit']!=0:return {'state':'request_failed_no_retry','request':request}
  print(agent+': current read-only checks accepted',flush=True);deadline=time.monotonic()+240
  while True:
   events=snapshot();final=events['final'] or ''
   if 'ROLLOUT_FEATURE_CHECK_COMPLETE' in final:break
   if time.monotonic()>deadline:return {'state':'awaiting_completion_no_replay','request':request,'events':events}
   print(agent+': '+str(len(events['tools']))+' tool results saved',flush=True);time.sleep(10)
 final=events['final'] or '';tools=events['tools']
 asana=[x for x in tools if x['name']=='asana.asana_get_user']
 notion=[x for x in tools if x['name']=='codex_apps.notion.fetch']
 memory=[x for x in tools if 'memory_recall' in x['name'] or ('memory' in x['name'] and any(y in x['name'] for y in ['search','recall','retrieve']))]
 passed=len(asana)==1 and not asana[0]['isError'] and asana[0]['expectedGidMatched'] and asana[0]['expectedWorkspaceMatched'] and any(not x['isError'] and x['technicalDocumentationMatched'] for x in notion) and any(not x['isError'] for x in memory) and all(x in final for x in ['ASANA_PASS','NOTION_PASS','MEMORY_READ_PASS'])
 result={'state':'passed_current_features' if passed else 'feature_acceptance_failed','request':request,'events':events}
 path=Path('/home/ubuntu/reconnect-current-feature-'+agent+'.json');path.write_text(json.dumps(result,indent=2)+'\n')
 return result
