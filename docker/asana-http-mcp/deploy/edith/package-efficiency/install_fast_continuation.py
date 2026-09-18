from pathlib import Path
import py_compile
p=Path('/home/node/.openclaw/workspace/scripts/edith-project-dispatch.py')
s=p.read_text()
old=" connect();t=get_task(gid)\n try:\n  from ready_review_handoff"
new=" connect();t=get_task(gid)\n try:\n  from fast_continuation import expedite_successor\n  record['fast_continuation']=expedite_successor(record,t,get_task,lambda task,due:call('asana_update_task',{'task_id':task,'due_at':due}));save(gid,record)\n except Exception as e:\n  record['fast_continuation']={'status':'unconfirmed','error_type':type(e).__name__};save(gid,record)\n try:\n  from ready_review_handoff"
if 'from fast_continuation import expedite_successor' not in s:
 assert s.count(old)==1
 backup=p.with_name('edith-project-dispatch.before-fast-continuation-20260917.py')
 if not backup.exists():backup.write_text(s)
 p.write_text(s.replace(old,new))
py_compile.compile(str(p),doraise=True)
print('Successor timing hook installed; existing worker admission and connections preserved')
