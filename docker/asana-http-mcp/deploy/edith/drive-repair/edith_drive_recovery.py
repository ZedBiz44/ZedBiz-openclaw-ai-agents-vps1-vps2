"""Reconcile uncertain binary copies; never retry a write or infer failure from absence."""
from datetime import datetime, timezone
from pathlib import Path
import json
import time

FIELDS = 'id,name,parents,driveId,md5Checksum,size,createdTime,trashed,mimeType'

def stamp(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).timestamp()

def candidate(source, files, args, started):
    matches = [x for x in files if x.get('name') == args[2] and not x.get('trashed')]
    if len(matches) != 1 or not source.get('md5Checksum') or not source.get('size'):
        return None
    item = matches[0]
    if (item.get('parents') != [args[-1]] or
        any(item.get(k) != source.get(k) for k in ('md5Checksum', 'size', 'driveId')) or
        not item.get('createdTime') or stamp(item['createdTime']) < stamp(started) - 5):
        return None
    return item

def reconcile(args, started, read, attempts=3, sleep=time.sleep):
    """Only reads. Return an exact recent binary match, otherwise retain the hold."""
    source = read('get', args[1], '--fields', FIELDS)['file']
    for attempt in range(attempts):
        files, token = [], None
        while True:
            query = ['ls', '--parent', args[-1], '--max', '100',
                     '--fields', 'files(' + FIELDS + '),nextPageToken']
            if token:
                query += ['--page', token]
            page = read(*query)
            files.extend(page.get('files', []))
            token = page.get('nextPageToken')
            if not token:
                break
        found = candidate(source, files, args, started)
        if found:
            # Re-read by stable ID; caller still performs normal access/content proof.
            live = read('get', found['id'], '--fields', FIELDS)['file']
            if candidate(source, [live], args, started):
                return {'file': live, 'reconciled_after_timeout': True}
        if attempt + 1 < attempts:
            sleep(5 * (attempt + 1))
    return None

def recover_journal(path, read):
    from execution_guard import save
    path = Path(path)
    record = json.loads(path.read_text())
    if record['status'] == 'confirmed':
        return record['result']
    if record['args'][0] != 'copy':
        raise ValueError('Only binary copy reconciliation is supported')
    result = reconcile(record['args'], record['started_at'], read)
    if result is None:
        raise RuntimeError('Copy outcome remains uncertain; no write was retried')
    record.update(status='confirmed', result=result, previous_status=record['status'],
                  reconciled_at=datetime.now(timezone.utc).isoformat())
    save(path, record)
    return result

