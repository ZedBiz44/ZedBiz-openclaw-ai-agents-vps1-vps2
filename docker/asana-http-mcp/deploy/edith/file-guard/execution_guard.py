"""Edith recovery: enforce saved decisions and never blindly repeat uncertain writes.

This is a structural gate, not a claim that a classification is semantically right.
The producer records the content review; Ruby independently accepts the result.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone

READS = {'get', 'ls', 'search', 'permissions', 'download', 'url'}
WRITES = {'copy', 'mkdir', 'move'}
PROTECTED = {'1d6ADvC5OVsNQ_I50K944htnQP1dj7StP',
             '1dfWDgUVIRks5_-hduse7LZhSM9fiMgdK',
             '1PobhHFSjRtCkiW3FjHENlxpQhulN8Qo0'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    tmp = path.with_suffix('.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(value, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def read(path):
    return json.loads(path.read_text())


def gate(base, root, args, check_plan):
    plan_path = base / 'prewrite-plan.json'
    plan = read(plan_path)
    before = read(base / 'initial-inventory.json')
    if not before.get('complete'):
        raise ValueError('Incomplete source inventory')
    issues = check_plan(plan, before)
    if issues:
        raise ValueError('Saved plan is incomplete or lacks successful own-file inspection')
    review = read(base / 'plan-review.json')
    if review.get('plan_sha256') != digest(plan_path) or review.get('inventory_sha256') != digest(base / 'initial-inventory.json'):
        raise ValueError('Plan or source inventory changed after content review')
    if not review.get('reviewer') or not review.get('reviewed_at') or review.get('representative_content_checked') is not True:
        raise ValueError('Representative content review is missing')
    evidence = review.get('evidence', {})
    rows = {r['source_id']: r for r in plan['file_plan']}
    for row in rows.values():
        destination = PurePosixPath(row['planned_path'])
        if destination.is_absolute() or '..' in destination.parts:
            raise ValueError('Destination escapes the approved folder')
    for fid, row in rows.items():
        if row.get('action') in ('protected', 'hold'):
            continue
        e = evidence.get(fid, {})
        if e.get('source_id') != fid or not e.get('path') or not e.get('sha256'):
            raise ValueError('Missing source-linked inspection evidence: ' + fid)
        p = Path(e['path']).resolve()
        if not p.is_relative_to(base.parent.resolve()) or not p.is_file() or digest(p) != e['sha256']:
            raise ValueError('Inspection evidence missing, changed, or outside private evidence area: ' + fid)
    state_path = base / 'execution-state.json'
    state = read(state_path) if state_path.exists() else {}
    folders = dict(state.get('folders', {}))
    folders[''] = root
    reverse = {v: k for k, v in folders.items()}
    if len(reverse) != len(folders):
        raise ValueError('Ambiguous folder mapping')
    originals = {x['id']: x for x in before['items']}
    protected = set(PROTECTED)
    while True:
        expanded = protected | {fid for fid, x in originals.items() if protected.intersection(x.get('parents', []))}
        if expanded == protected:
            break
        protected = expanded
    if any(str(a) in protected for a in args[1:]):
        raise ValueError('Protected item or subtree')
    if '--parent' not in args or args.count('--parent') != 1:
        raise ValueError('Exactly one known destination parent is required')
    parent = args[args.index('--parent') + 1]
    if parent not in reverse:
        raise ValueError('Destination parent is not in the saved execution state')
    parent_path = reverse[parent]
    action = args[0]
    expected_length = {'copy': 5, 'mkdir': 4, 'move': 4}[action]
    if len(args) != expected_length or args[-2:] != ('--parent', parent):
        raise ValueError('Unexpected mutation flags or arguments')
    if action == 'copy':
        row = rows.get(args[1])
        actual = str(PurePosixPath(parent_path) / args[2])
        if not row or row.get('action') != 'copy' or row['planned_path'] != actual:
            raise ValueError('Copy destination does not exactly match the reviewed decision')
        pilot = review.get('pilot_source_ids', [])
        if not pilot or any(fid not in rows or rows[fid].get('action') != 'copy' for fid in pilot):
            raise ValueError('A populated first-section pilot must be identified')
        if args[1] not in pilot:
            first = read(base / 'first-section-review.json')
            checked = {x.get('source_id') for x in first.get('files', [])}
            if first.get('passed') is not True or not set(pilot).issubset(checked):
                raise ValueError('First populated section has not passed its content self-check')
    elif action == 'mkdir':
        actual = str(PurePosixPath(parent_path) / args[1])
        permitted = set()
        for row in rows.values():
            if row.get('action') == 'copy':
                permitted.update(str(p) for p in PurePosixPath(row['planned_path']).parents if str(p) != '.')
        permitted.update(review.get('archive_paths', []))
        if actual not in permitted or '..' in PurePosixPath(actual).parts or PurePosixPath(actual).is_absolute():
            raise ValueError('Unplanned folder')
    elif action == 'move':
        fid = args[1]
        proof = state.get('copies', {}).get(fid, {})
        if fid not in rows or rows[fid].get('action') != 'copy' or parent_path not in review.get('archive_paths', []):
            raise ValueError('Only a planned original can be moved to its reviewed archive')
        if not proof.get('active_id') or proof.get('permissions_matched') is not True or not proof.get('content_read'):
            raise ValueError('Archive requires a verified active copy first')
        source = originals[fid]
        if any(proof.get(k) != source.get(k) for k in ('md5Checksum', 'size')):
            raise ValueError('Archive copy does not match original')
    return digest(plan_path)


def run(base, root, args, execute, check_plan):
    args = tuple(args)
    if args[0] in READS:
        return execute()
    if args[0] not in WRITES:
        raise ValueError('This recovery executor does not authorize this Drive operation')
    base = Path(base)
    # Held across the request and durable response commit. A killed process releases it.
    import fcntl
    with (base / 'mutation.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        plan_hash = gate(base, root, args, check_plan)
        key = hashlib.sha256(json.dumps([root, args]).encode()).hexdigest()
        journal = base / 'mutation-journal'
        journal.mkdir(mode=0o700, exist_ok=True)
        path = journal / (key + '.json')
        if path.exists():
            old = read(path)
            if old['status'] == 'confirmed':
                return old['result']
            raise RuntimeError('Uncertain prior write: reconcile this journal with live Drive before retry: ' + key)
        record = {'status': 'intent', 'args': args, 'root': root, 'plan_sha256': plan_hash,
                  'started_at': datetime.now(timezone.utc).isoformat()}
        save(path, record)
        try:
            result = execute()
        except BaseException:
            record['status'] = 'uncertain'
            save(path, record)
            raise
        record.update(status='confirmed', result=result)
        save(path, record)
        return result
