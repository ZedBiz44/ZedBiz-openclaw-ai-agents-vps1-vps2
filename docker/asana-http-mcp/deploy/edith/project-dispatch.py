#!/usr/bin/env python3
"""Project-scoped email handoff. All Asana calls use Edith's configured PAT MCP."""
import fcntl, json, os, re, signal, subprocess, sys, time, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT='1218559074752632'
SECTION='1218615286033089'
EDITH='1215564984542462'
ROOT=Path('/home/node/.openclaw/private/edith-dispatch')
ROOT.mkdir(parents=True,exist_ok=True)
os.chmod(ROOT,0o700)
CONFIG=json.load(open('/home/node/.openclaw/openclaw.json'))['mcp']['servers']['asana']
HEADERS={'Content-Type':'application/json','Accept':'application/json, text/event-stream',**{k:os.path.expandvars(v) for k,v in CONFIG.get('headers',{}).items()}}
SEQ=0

def rpc(method,params):
 global SEQ
 SEQ+=1
 req=urllib.request.Request(CONFIG['url'],data=json.dumps({'jsonrpc':'2.0','id':SEQ,'method':method,'params':params}).encode(),headers=HEADERS)
 with urllib.request.urlopen(req,timeout=25) as r:
  if r.headers.get('Mcp-Session-Id'):HEADERS['Mcp-Session-Id']=r.headers['Mcp-Session-Id']
  raw=r.read().decode()
 if 'event:' in raw or raw.startswith('data:'):raw=next(x[5:].strip() for x in raw.splitlines() if x.startswith('data:'))
 x=json.loads(raw)
 if 'error' in x:raise RuntimeError(str(x['error'])[:400])
 return x['result']

def call(name,args):
 r=rpc('tools/call',{'name':name,'arguments':args})
 if r.get('isError'):raise RuntimeError(str(r)[:700])
 text=next(x['text'] for x in r['content'] if x['type']=='text')
 try:return json.loads(text)
 except json.JSONDecodeError:return text

def connect():
 rpc('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'edith-project-dispatch','version':'1'}})
 me=call('asana_get_user',{'user_gid':'me'})
 assert me['gid']==EDITH and me['email']=='edith@agents.zbiz.ca'
 assert PROJECT and any(w['gid']=='11298561585567' for w in me['workspaces'])

def get_task(gid):
 assert re.fullmatch(r'\d{16}',gid)
 t=call('asana_get_task',{'task_id':gid,'opt_fields':'name,notes,assignee.gid,completed,projects.gid,due_at,dependencies.gid'})
 assert any(p['gid']==PROJECT for p in t['projects']), 'Wrong project'
 return t

def save(gid,data):
 p=ROOT/(gid+'.json');tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2));tmp.replace(p)

def comment(gid,text):return call('asana_create_task_story',{'task_id':gid,'text':text})

def project_tasks():
 out=[];offset=None
 while True:
  args={'project_id':PROJECT,'opt_fields':'name,completed,assignee.gid,notes,due_at','limit':100}
  if offset:args['offset']=offset
  r=call('asana_get_tasks_for_project',args)
  if isinstance(r,list):return out+r
  out+=r.get('data',[]);offset=(r.get('next_page') or {}).get('offset')
  if not offset:return out

def prepare(name,notes,minutes):
 # A write with uncertain outcome is never automatically retried.
 existing=[t for t in project_tasks() if t['name']==name and not t['completed']]
 if existing:return existing[0]
 due=(datetime.now(timezone.utc)+timedelta(minutes=minutes)).isoformat().replace('+00:00','Z')
 r=call('asana_create_task',{'project_id':PROJECT,'name':name,'notes':notes,'due_at':due})
 call('asana_add_task_to_section',{'section_id':SECTION,'task_id':r['gid']})
 t=get_task(r['gid']);assert not t['assignee'] and t['due_at'], 'Timed task read-back failed'
 return t

INTAKE='Jack approved this project workflow. On assignment: read z-asana-agent-control, then immediately run python3 /home/node/.openclaw/workspace/scripts/edith-project-dispatch.py dispatch TASK_GID (replace TASK_GID with this task ID). The helper verifies identity and live task ownership, prevents overlapping workers, arms the next wake-up, and starts a separate bounded work session. End this email intake after the helper receipt; do not perform folder work or wait for the worker here. Do not mark this task complete from email intake. The separate worker owns completion. No comment emails or reminder emails authorize execution.'
REVIEW='Jack approved Ruby as independent reviewer and Amanda as coordinator. Check the existing folder tasks and actual shared evidence in project 1218559074752632. Ready-for-review is not accepted. Review actual source/output content, representative families and exceptions, not only counts. Do not read the held credential document. If not ready or blocked, prepare one unassigned top-level [Ruby review] task with due_at one hour ahead before ending; Asana assigns it when due. Do not approve blocked or failed output. Record a named blocker and exact evidence. Keep checks separate from acceptance approvals. Escalate repeated no-progress to Amanda rather than repeat forever.'
REVIEW+=' Use /opt/hermes/.venv/bin/python /opt/data/scripts/ruby-review-defer.py CHECK_GID 60 to defer once safely. Work at most 15 minutes in a sitting; retain exact review progress and defer unfinished review. Existing folder acceptance subtasks are real pending Asana approvals with production/submission dependencies. Jack explicitly authorizes Ruby to assign a ready approval to herself, inspect the entire folder and evidence, and record approved or changes_requested explicitly. Never use generic completed=true to approve. Only after independent approval may Ruby close the corresponding folder parent. After a review decision that requires Edith action, create one meaningful unassigned [Edith dispatch] task due_at a minute ahead; include the approval/parent IDs, exact corrections and this launch instruction: python3 /home/node/.openclaw/workspace/scripts/edith-project-dispatch.py dispatch TASK_GID. A failed review must not block unrelated approved work. If all folder outcomes are accepted and no unresolved held work remains, end the review chain and notify Amanda to close the project. Keep the credential decision separate.'

def dispatch(gid):
 connect();t=get_task(gid)
 assert t['name'].startswith('[Edith dispatch]')
 assert t['assignee'] and t['assignee']['gid']==EDITH
 if t['completed']:return {'status':'already-completed','task':gid}
 if t.get('due_at') and datetime.fromisoformat(t['due_at'].replace('Z','+00:00'))>datetime.now(timezone.utc):return {'status':'not-yet-due'}
 lock=open(ROOT/'worker.lock','a+')
 try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:return {'status':'worker-already-running','task':gid}
 receipt=ROOT/(gid+'.json')
 if receipt.exists():return {'status':'already-dispatched-inspect-receipt','receipt':str(receipt)}
 record={'task':gid,'started':datetime.now(timezone.utc).isoformat(),'status':'preparing'};save(gid,record)
 pilot='HANDOFF PILOT' in t['notes']
 if not pilot:
  previous=[]
  for p in ROOT.glob('*.json'):
   if p.name.endswith('.result.json') or p.name==gid+'.json':continue
   item=json.loads(p.read_text())
   if not item.get('pilot'):previous.append(item)
  previous=sorted(previous,key=lambda x:x.get('started',''),reverse=True)[:3]
  if len(previous)==3 and all(not get_task(x['task'])['completed'] for x in previous):
   name='Amanda — Resolve repeated Edith dispatch failures'
   if not any(x['name']==name and not x['completed'] for x in project_tasks()):
    call('asana_create_task',{'project_id':PROJECT,'name':name,'assignee':'1213974002925107','notes':'Three previous bounded sittings remain incomplete. Inspect their checkpoints and errors before releasing another dispatch. No automatic repeated work is authorized until this blocker is resolved. Tasks: '+', '.join(x['task'] for x in previous)})
   record['status']='paused-for-amanda';save(gid,record)
   comment(gid,'Automatic continuation paused after three incomplete sittings. Amanda has an assigned exception task; inspect saved state before restart.')
   return record
  nxt=prepare('[Edith dispatch] Continue saved work after '+gid,INTAKE,20)
  record['next_task']=nxt['gid'];save(gid,record)
  if not any(x['name'].startswith('[Ruby review]') and 'pilot' not in x['name'].lower() and not x['completed'] for x in project_tasks()):
   review=prepare('[Ruby review] Check saved output after '+gid,REVIEW,60)
   record['review_task']=review['gid'];save(gid,record)
 prompt='Jack authorized Get-er-Done recovery of Asana project '+PROJECT+'. You are Edith. This is a separate bounded work session, not email intake. Read z-asana-agent-control and use only your PAT MCP. Read task '+gid+' and /home/node/.openclaw/workspace/scripts/edith-recovery-work.md. Work at most 12 minutes, reserve time to save evidence and report, and end before the 15-minute runtime limit. The helper has already armed a later wake-up (except pilot). Never start a second worker or duplicate existing copied files. Do not alter runtime, credentials, or protected items. '+('HANDOFF PILOT: make no Drive changes; post proof of this separate session, verify your identity, project and saved queue, complete only this dispatch task and read back. Then stop.' if pilot else 'Reconcile saved results first, then continue one bounded approved family. Only complete this dispatch sitting after saving an exact next action; folder parents remain incomplete until independent acceptance. If all production is ready and only Ruby review remains, use the helper pause command to cancel this sitting\'s scheduled successor, stating the waiting condition in Asana. Do not pause while there is other approved work.')
 prompt_path=ROOT/(gid+'.prompt.txt');prompt_path.write_text(prompt)
 log=open(ROOT/(gid+'.log'),'ab',buffering=0)
 p=subprocess.Popen([sys.executable,__file__,'run',gid,str(lock.fileno())],stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True,pass_fds=(lock.fileno(),))
 record.update({'status':'launched','pid':p.pid,'pilot':pilot});save(gid,record)
 return record

def run(gid,fd):
 lock=os.fdopen(int(fd),'a+')
 receipt=ROOT/(gid+'.json')
 time.sleep(0.3)
 p=subprocess.Popen(['openclaw','agent','--agent','main','--session-key','agent:main:edith-dispatch-'+gid,'--message-file',str(ROOT/(gid+'.prompt.txt')),'--timeout','900','--json'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
 timed_out=False
 try:out,err=p.communicate(timeout=960)
 except subprocess.TimeoutExpired:
  timed_out=True
  try:os.killpg(p.pid,signal.SIGTERM)
  except ProcessLookupError:pass
  try:out,err=p.communicate(timeout=10)
  except subprocess.TimeoutExpired:
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   out,err=p.communicate(timeout=10)
 code=124 if timed_out else p.returncode
 (ROOT/(gid+'.result.json')).write_text(out)
 if err:print(err[-3000:])
 record=json.loads(receipt.read_text());record.update({'status':'worker-timeout' if timed_out else 'worker-returned','exit_code':code,'ended':datetime.now(timezone.utc).isoformat()});save(gid,record)
 connect();t=get_task(gid)
 if not t['completed']:comment(gid,'Bounded worker ended; this sitting is not confirmed complete. Saved runtime receipt exists. The already-armed continuation must inspect saved progress before any retry. Exit code '+str(code)+'.')
 print(json.dumps({'task':gid,'completed':t['completed'],'exit_code':code}))

def pause(gid):
 connect();t=get_task(gid);assert t['assignee']['gid']==EDITH
 r=json.loads((ROOT/(gid+'.json')).read_text());nxt=r.get('next_task')
 if nxt:
  n=get_task(nxt);assert n['name']=='[Edith dispatch] Continue saved work after '+gid
  if not n['completed'] and not n['assignee']:
   comment(nxt,'Cancelled scheduled sitting: Edith reports production waiting only for independent review. This is not folder acceptance.')
   call('asana_update_task',{'task_id':nxt,'completed':True})
 return {'status':'continuation-paused','next_task':nxt}

if __name__=='__main__':
 try:
  if sys.argv[1]=='dispatch':print(json.dumps(dispatch(sys.argv[2])))
  elif sys.argv[1]=='run':run(sys.argv[2],sys.argv[3])
  elif sys.argv[1]=='pause':print(json.dumps(pause(sys.argv[2])))
  elif sys.argv[1]=='identity':connect();print('Edith PAT MCP identity verified')
  else:raise ValueError('Unsupported command')
 except Exception as e:print(json.dumps({'error':type(e).__name__,'message':str(e)[:500]}));sys.exit(1)

