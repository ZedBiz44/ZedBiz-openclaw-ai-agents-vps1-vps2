"""Release one ready folder through the proven native assignment-email Rule."""
import asyncio, importlib.util, json, os, sys
from datetime import datetime, timezone
from pathlib import Path
PROJECT='1218559074752632'
RUBY='1215900603267704'
READY='1218559365904785'
APPROVALS=["1218559788703782","1218559622039883","1218559452275700","1218574348329943","1218559789137828","1218559452593223","1218559622201055","1218559452895543","1218559622386305","1218559789594246"]
FIELDS='name,notes,completed,approval_status,assignee.gid,parent.gid,dependencies.gid,resource_subtype'
MARKER='READY REVIEW HANDOFF v1'

def pending(t):
 return t.get('approval_status')=='pending' and not t.get('completed')

async def release(call, dry=False):
 rows=[];offset=None
 while True:
  args={'project_id':PROJECT,'opt_fields':'name,notes,completed,assignee.gid','limit':100}
  if offset:args['offset']=offset
  page=await call('asana_get_tasks_for_project',args)
  if isinstance(page,list):rows+=page;break
  rows+=page.get('data',[]);offset=(page.get('next_page') or {}).get('offset')
  if not offset:break
 active_dispatch=[x for x in rows if x['name'].startswith('[Ruby review] Ready folder ') and not x.get('completed')]
 if active_dispatch:return {'status':'review-already-released','tasks':[x['gid'] for x in active_dispatch]}
 approvals=[await call('asana_get_task',{'task_id':g,'opt_fields':FIELDS}) for g in APPROVALS]
 active=[t for t in approvals if pending(t) and t.get('assignee')]
 if active:return {'status':'review-already-assigned','tasks':[t['gid'] for t in active]}
 for t in approvals:
  if not pending(t):continue
  assert t.get('resource_subtype')=='approval'
  p=await call('asana_get_task',{'task_id':t['parent']['gid'],'opt_fields':'name,completed,memberships.project.gid,memberships.section.gid'})
  if p.get('completed') or not any(m.get('project',{}).get('gid')==PROJECT and (m.get('section') or {}).get('gid')==READY for m in p.get('memberships',[])):continue
  deps=t.get('dependencies',[])
  if not deps:continue
  checks=[await call('asana_get_task',{'task_id':d['gid'],'opt_fields':'completed,resource_subtype,approval_status'}) for d in deps]
  if not all(d.get('approval_status')=='approved' if d.get('resource_subtype')=='approval' else d.get('completed') for d in checks):continue
  assert MARKER in t.get('notes',''),'Ready task lacks current handoff brief'
  if dry:return {'status':'ready','approval':t['gid'],'folder':p['name']}
  # Reconcile assignment before a write; repeated same assignee is idempotent.
  fresh=await call('asana_get_task',{'task_id':t['gid'],'opt_fields':FIELDS})
  if not pending(fresh) or fresh.get('assignee'):return {'status':'state-changed','approval':t['gid']}
  name='[Ruby review] Ready folder '+t['gid']
  if any(x['name']==name for x in rows):return {'status':'prior-review-exists-inspect','approval':t['gid']}
  notes=("Jack authorized this ready folder review. Read z-asana-agent-control and use your own PAT MCP. "
   "On assignment, read approval "+t['gid']+" and parent "+t['parent']['gid']+". Verify completed submission dependencies, claim that approval as Ruby, and conduct its full current revised scope. "
   "Post the report and explicit approval_status on the approval and parent. Complete this dispatch only after posting that decision. "
   "Then run /opt/hermes/.venv/bin/python /opt/data/scripts/ready_review_handoff.py to release the next ready folder. "
   "Do not call the helper until THIS dispatch is complete, or it will correctly detect an outstanding review. "
   "No review time limit, no ruby-review-defer.py, no repeated check tasks. "
   "If genuinely blocked, report the exact blocker to Amanda with a prepared exception assignment and preserve your checkpoint. "
   "Never open the held credential document, change file formats, delete files or modify protected areas. "
   "READY_APPROVAL:"+t['gid']+"\n\n"+t['notes'])
  due=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
  made=await call('asana_create_task',{'project_id':PROJECT,'name':name,'notes':notes,'due_at':due})
  check=await call('asana_get_task',{'task_id':made['gid'],'opt_fields':'name,notes,assignee.gid,completed,due_at'})
  assert check['name']==name and check['notes']==notes and check.get('due_at') and not check.get('assignee'),'Prepared review readback failed'
  return {'status':'released-to-asana-rule','approval':t['gid'],'task':made['gid'],'folder':p['name']}

 return {'status':'no-ready-review'}

async def ruby_main(dry):
 import yaml
 from mcp import ClientSession,StdioServerParameters
 from mcp.client.stdio import stdio_client
 c=yaml.safe_load(Path('/opt/data/config.yaml').read_text())['mcp_servers']['asana']
 env=os.environ.copy();env.update({k:os.path.expandvars(str(v)) for k,v in c['env'].items()})
 async with stdio_client(StdioServerParameters(command=c['command'],args=c['args'],env=env)) as (r,w):
  async with ClientSession(r,w) as session:
   await session.initialize()
   async def call(n,a):
    result=await session.call_tool(n,a)
    if result.is_error:raise RuntimeError('Asana MCP failed: '+n)
    return json.loads(next(x.text for x in result.content if x.type=='text'))
   me=await call('asana_get_user',{'user_gid':'me'})
   assert me['gid']==RUBY and me['email']=='ruby@agents.zbiz.ca' and any(w['gid']=='11298561585567' for w in me['workspaces'])
   return await release(call,dry)

def edith_release(dry=False):
 spec=importlib.util.spec_from_file_location('edith_ready_transport',str(Path(__file__).with_name('edith-project-dispatch.py')))
 d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d);d.connect()
 async def call(n,a):return d.call(n,a)
 return asyncio.run(release(call,dry))

if __name__=='__main__':
 dry='--dry-run' in sys.argv
 result=asyncio.run(ruby_main(dry)) if Path('/opt/data/config.yaml').exists() else edith_release(dry)
 print(json.dumps(result))
