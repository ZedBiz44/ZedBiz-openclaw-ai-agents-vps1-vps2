"""Release one existing, ready approval; no timer, new task, or review time limit."""
import asyncio, importlib.util, json, os, sys
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
  await call('asana_update_task',{'task_id':t['gid'],'assignee':RUBY})
  check=await call('asana_get_task',{'task_id':t['gid'],'opt_fields':FIELDS})
  assert (check.get('assignee') or {}).get('gid')==RUBY,'Assignment unconfirmed; inspect before retry'
  return {'status':'assigned','approval':t['gid'],'folder':p['name']}
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
