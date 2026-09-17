import asyncio,unittest
from ready_review_handoff import release,APPROVALS,MARKER,PROJECT,READY,RUBY
class Tests(unittest.TestCase):
 def run_case(self,mode):
  writes=[];dispatches=[]
  rows={g:dict(gid=g,resource_subtype='approval',approval_status='approved',completed=True) for g in APPROVALS}
  a=rows[APPROVALS[0]]=dict(gid=APPROVALS[0],resource_subtype='approval',approval_status='pending',completed=False,assignee=None,parent={'gid':'parent'},dependencies=[{'gid':'submit'}],notes=MARKER)
  if mode=='busy':a['assignee']={'gid':RUBY}
  async def call(n,p):
   if n=='asana_get_tasks_for_project':return {'data':dispatches,'next_page':None}
   if n=='asana_create_task':
    writes.append(p);new=dict(p,gid='new',completed=False,assignee=None);dispatches.append(new);return new
   g=p['task_id']
   if g=='new':return dispatches[0]
   if g=='parent':return dict(name='AlbertaWide',completed=False,memberships=[dict(project={'gid':PROJECT},section={'gid':READY if mode!='notready' else 'other'})])
   if g=='submit':return dict(completed=mode!='blocked')
   return rows[g].copy()
  first=asyncio.run(release(call))
  second=asyncio.run(release(call))
  return first,second,writes
 def test_release_once(self):
  a,b,w=self.run_case('ready');self.assertEqual(a['status'],'released-to-asana-rule');self.assertEqual(b['status'],'review-already-released');self.assertEqual(len(w),1)
 def test_busy(self):self.assertEqual(self.run_case('busy')[2],[])
 def test_blocked(self):self.assertEqual(self.run_case('blocked')[2],[])
 def test_not_ready(self):self.assertEqual(self.run_case('notready')[2],[])
if __name__=='__main__':unittest.main()
