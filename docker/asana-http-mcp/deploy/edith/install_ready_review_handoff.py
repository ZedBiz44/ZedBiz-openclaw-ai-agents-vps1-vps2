from pathlib import Path
import py_compile
p=Path('/home/node/.openclaw/workspace/scripts/edith-project-dispatch.py')
s=p.read_text()
old=" connect();t=get_task(gid)\n if not t['completed']:comment"
new=" connect();t=get_task(gid)\n try:\n  from ready_review_handoff import edith_release\n  record['ready_review_handoff']=edith_release();save(gid,record)\n except Exception as e:\n  record['ready_review_handoff']={'status':'unconfirmed','error_type':type(e).__name__};save(gid,record)\n if not t['completed']:comment"
if new not in s:
 assert s.count(old)==1
 backup=p.with_name('edith-project-dispatch.before-ready-handoff-20260917.py')
 if not backup.exists():backup.write_text(s)
 p.write_text(s.replace(old,new))
py_compile.compile(str(p),doraise=True)
print('Ready-review release installed at production worker completion')
