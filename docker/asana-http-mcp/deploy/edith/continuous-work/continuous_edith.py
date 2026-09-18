"""Keep one assigned task and OpenClaw session across useful work turns.

Called only after the existing dispatcher has verified identity, assignment,
dependencies and acquired the inherited exclusive writer lock.
"""
import hashlib
import json
import os
import signal
import subprocess
import time
from datetime import datetime, timedelta, timezone

TURN_SECONDS = 2700
RECOVERY_MINUTES = 55

def progress_fingerprint(root):
    """Evidence changes, not a refreshed timestamp in a queue status message."""
    h = hashlib.sha256()
    for p in sorted(root.rglob('*')):
        if p.is_file() and any(s in p.name for s in ('execution-state', 'journal', 'plan-review', 'inspection', 'inventory')):
            h.update(str(p).encode())
            h.update(p.read_bytes())
    return h.hexdigest()

def renew_backup(d, gid, record):
    nxt = record['next_task']
    task = d.get_task(nxt)
    assert task['name'] == '[Edith dispatch] Continue saved work after ' + gid
    assert not task['completed'] and not task['assignee'], 'Backup already released; inspect before continuing'
    due = (datetime.now(timezone.utc) + timedelta(minutes=RECOVERY_MINUTES)).replace(microsecond=0)
    d.call('asana_update_task', {'task_id': nxt, 'due_at': due.isoformat()})
    check = d.get_task(nxt)
    assert datetime.fromisoformat(check['due_at'].replace('Z', '+00:00')) == due
    assert not check['completed'] and not check['assignee']
    return due.isoformat()

def run_continuous(d, gid, fd):
    # Keep the inherited exclusive writer lock through every turn and API check.
    with os.fdopen(int(fd), 'a+'):
        try:
            return _run_continuous(d, gid)
        except Exception as exc:
            record = json.loads((d.ROOT / (gid + '.json')).read_text())
            record.update(status='continuous-controller-error', error_type=type(exc).__name__, ended=datetime.now(timezone.utc).isoformat())
            d.save(gid, record)
            raise

def _run_continuous(d, gid):
    time.sleep(.3)
    record = json.loads((d.ROOT / (gid + '.json')).read_text())
    session = 'agent:main:edith-project-continuous-' + gid
    record.update(mode='continuous-v1', session_key=session, turns=[])
    d.save(gid, record)
    no_progress = 0
    turn = 0
    while True:
        d.connect()
        current = d.get_task(gid)
        if current['completed']:
            record['status'] = 'continuous-finished'
            d.save(gid, record)
            d.pause(gid)
            return
        assert current['assignee']['gid'] == d.EDITH
        record['backup_due'] = renew_backup(d, gid, record)
        turn += 1
        record.update(status='continuous-running', turn=turn)
        d.save(gid, record)
        before = progress_fingerprint(d.ROOT.parent / 'folder-cleanup')
        prompt = (d.ROOT / (gid + '.prompt.txt')).read_text() if turn == 1 else (
            'Continue the SAME authorized work and current Asana task ' + gid +
            ' from your existing context and last checkpoint. The supervisor retained the writer lock and renewed the SAME crash-recovery ticket. '
            'Do not reload the project, completed reviews, memory bank or full skills. Read changed inputs only. '
            'Do not create another dispatch. Work through ready groups; checkpoint after each. '
            'Keep this task open while ready work remains. Complete it only when all production is submitted or no authorized work can proceed; state exact blockers. '
            'You have up to 40 minutes of useful work before the 45-minute safety timeout, not a target to consume. '
            'Preserve all existing file, credential, uncertainty and independent-review safeguards.')
        message = d.ROOT / (gid + '.continuous-prompt.txt')
        message.write_text(prompt)
        p = subprocess.Popen(['openclaw', 'agent', '--agent', 'main', '--session-key', session,
            '--message-file', str(message), '--timeout', str(TURN_SECONDS), '--json'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
        timed_out = False
        try:
            out, err = p.communicate(timeout=TURN_SECONDS + 60)
        except subprocess.TimeoutExpired:
            timed_out = True
            try: os.killpg(p.pid, signal.SIGTERM)
            except ProcessLookupError: pass
            try: out, err = p.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                try: os.killpg(p.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                out, err = p.communicate(timeout=10)
        code = 124 if timed_out else p.returncode
        if code == 0:
            try:
                response = json.loads(out)
                result = response.get('result', response)
                if response.get('status') in ('error', 'aborted', 'timeout') or result.get('meta', {}).get('aborted'):
                    code = 124
            except (ValueError, AttributeError):
                code = 125  # An unreadable result is not proven successful work.
        (d.ROOT / (gid + '.turn-' + str(turn) + '.result.json')).write_text(out)
        if err: print(err[-2000:])
        record['turns'].append({'turn': turn, 'exit_code': code, 'ended': datetime.now(timezone.utc).isoformat()})
        record['exit_code'] = code
        d.save(gid, record)
        # A failure may leave an uncertain write. Never automatically replay it here.
        if code:
            record.update(status='continuous-failed-recovery-armed', ended=datetime.now(timezone.utc).isoformat())
            d.save(gid, record)
            return
        d.connect()
        from ready_review_handoff import edith_release
        record['ready_review_handoff'] = edith_release()
        current = d.get_task(gid)
        if current['completed']:
            d.pause(gid)
            record.update(status='continuous-finished', ended=datetime.now(timezone.utc).isoformat())
            d.save(gid, record)
            return
        after = progress_fingerprint(d.ROOT.parent / 'folder-cleanup')
        no_progress = no_progress + 1 if before == after else 0
        if no_progress >= 2:
            d.pause(gid)
            record.update(status='continuous-paused-no-production-progress', ended=datetime.now(timezone.utc).isoformat())
            d.save(gid, record)
            d.comment(gid, 'Continuous worker paused after two turns without changed production journals. No further automatic LLM retries. Inspect saved evidence and exact blocker before restarting. This is not folder acceptance.')
            return
        # No email, fresh session, new Asana task or full intake between turns.

