"""Reconcile a project status comment before any retry after an uncertain reply."""
import hashlib


def post_once(call, task_id, text):
    marker = '[recovery-report:' + hashlib.sha256((task_id + '\n' + text).encode()).hexdigest()[:24] + ']'

    def find():
        result = call('asana_get_task_stories', {'task_id': task_id, 'opt_fields': 'gid,text'})
        rows = result if isinstance(result, list) else result.get('data', [])
        matches = [row for row in rows if marker in row.get('text', '')]
        if len(matches) > 1:
            raise RuntimeError('Duplicate report marker requires reconciliation: ' + marker)
        return matches[0] if matches else None

    existing = find()
    if existing:
        return existing
    try:
        return call('asana_create_task_story', {'task_id': task_id, 'text': text + '\n' + marker})
    except Exception as original:
        # Only a read is allowed after uncertain execution; never retry the write.
        try:
            existing = find()
        except Exception:
            raise RuntimeError('Asana comment outcome unconfirmed; reconcile ' + marker) from original
        if existing:
            return existing
        raise RuntimeError('Asana comment not confirmed; no automatic retry: ' + marker) from original
