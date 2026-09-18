from datetime import datetime, timezone
def expedite_successor(record, current, read_task, update_task, now=None):
    """Advance the existing backup only after a successful, completed worker."""
    if record.get('pilot') or record.get('exit_code') != 0 or not current.get('completed'):
        return {'status':'backup-preserved'}
    gid=record.get('next_task')
    if not gid:return {'status':'no-successor'}
    nxt=read_task(gid)
    if nxt.get('completed') or nxt.get('assignee'):return {'status':'successor-already-handled','task':gid}
    if nxt.get('name') != '[Edith dispatch] Continue saved work after '+record['task']:
        raise ValueError('Unexpected successor')
    due=(now or datetime.now(timezone.utc)).isoformat().replace('+00:00','Z')
    update_task(gid,due)
    check=read_task(gid)
    if check.get('due_at') != due and datetime.fromisoformat(check['due_at'].replace('Z','+00:00')) != datetime.fromisoformat(due.replace('Z','+00:00')):
        raise ValueError('Successor release not confirmed')
    return {'status':'successor-expedited','task':gid,'due_at':check['due_at']}
