#!/usr/bin/env python3
"""Forced SSH command: fixed read-only fleet evidence, no arbitrary shell."""
import datetime as dt
import json
import os
from pathlib import Path
import shlex
import pwd
import sqlite3
import subprocess
import sys

CONFIG = Path('/etc/zedbiz-fleet-diagnostics.json')

def command(argv):
    r = subprocess.run(argv, capture_output=True, text=True)
    return {'exitCode': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr}

def main():
    allowed = json.loads(CONFIG.read_text())
    request = shlex.split(os.environ.get('SSH_ORIGINAL_COMMAND', ''))
    if len(request) != 2 or request[0] not in ('inspect', 'check') or request[1] not in allowed:
        print('Only inspect/check <approved-agent> is allowed', file=sys.stderr)
        return 2
    agent = request[1]
    profile = allowed[agent]
    if request[0] == 'check':
        print(json.dumps(fresh_check(profile, agent)))
        return 0
    result = {'agent': agent, 'collectedAtUtc': dt.datetime.now(dt.UTC).isoformat(), 'host': os.uname().nodename}
    result['hostMemory'] = Path('/proc/meminfo').read_text()
    result['processMemory'] = command(['ps', '-eo', 'pid,ppid,user,comm,rss,pcpu,etime', '--sort=-rss'])
    if profile.get('container'):
        result['service'] = command(['docker','inspect','--format','{{json .State}}',profile['container']])
        result['resources'] = command(['docker','stats','--no-stream','--format','{{json .}}',profile['container']])
    else:
        prefix = ['systemctl']
        if profile.get('user'):
            uid = pwd.getpwnam(profile['user']).pw_uid
            prefix = ['runuser','-u',profile['user'],'--','env','XDG_RUNTIME_DIR=/run/user/'+str(uid),'systemctl','--user']
        result['service'] = command(prefix+['show',profile['service'],'--property=LoadState,ActiveState,SubState,NRestarts,ExecMainStartTimestamp,MemoryCurrent,MemoryMax,MainPID'])
    root = Path(profile['root']).resolve()
    result['jobDetails'] = job_details(root)
    db = root/'state/openclaw.sqlite'
    if db.is_file() and db.resolve().is_relative_to(root):
        c = sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True)
        c.row_factory = sqlite3.Row
        result['database'] = str(db)
        # Receipts are evidence only; do not load configuration or credentials.
        result['healthJobs'] = [dict(r) for r in c.execute("select job_id,name,state_json from cron_jobs where name like '%health%'")]
        columns = {r[1] for r in c.execute('pragma table_info(cron_run_receipts)')}
        safe = [v for v in ['job_id','status','started_at_ms','finished_at_ms'] if v in columns]
        if safe:
            result['recentRuns'] = [dict(r) for r in c.execute('select '+','.join(safe)+' from cron_run_receipts order by started_at_ms desc limit 40')]
        c.close()
    artifacts = sorted((p for p in (root/'workspace/artifacts/health-checks').glob('*.json') if p.resolve().is_relative_to(root)),reverse=True)
    result['latestHealthArtifacts'] = [{'path':str(p),'result':json.loads(p.read_text())} for p in artifacts[:2]]
    result['limitations'] = ['This route cannot run repairs, read arbitrary files or provide an interactive shell.', 'Artifacts may contain private operational detail; keep them in private evidence storage.']
    print(json.dumps(result))
    return 0

"""Fixed read-only additions inserted into the existing endpoint; no shell input."""

def fresh_check(profile, agent):
    import fcntl
    root = Path(profile['root']).resolve()
    if agent not in ('frank', 'harry', 'suzy') or profile.get('service') != 'openclaw-' + agent:
        return {'execution': 'not_checked', 'reason': 'Fresh checks are enabled only for the three named VPS2 services'}
    values = dict(line.split(':', 1) for line in Path('/proc/meminfo').read_text().splitlines())
    if int(values['MemAvailable'].split()[0]) < 256 * 1024:
        return {'execution': 'not_checked', 'reason': 'Host has less than 256 MiB available for the lightweight reader'}
    lock = (root/'state/health-report.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return {'execution': 'already_running', 'reason': 'The existing health-report lock is held; wait for that check'}
    try:
        r = subprocess.run(['node', '/usr/local/lib/zedbiz-fleet/light-health.mjs', str(root)], capture_output=True, text=True)
        result = {'agent': agent, 'collectedAtUtc': dt.datetime.now(dt.UTC).isoformat(),
                  'execution': 'completed' if r.returncode == 0 else 'check_failed', 'exitCode': r.returncode,
                  'method': 'Host-side read-only gateway RPC; no additional OpenClaw CLI; existing report lock retained'}
        if r.returncode == 0:
            result['result'] = json.loads(r.stdout)
        else:
            result['reason'] = r.stderr.strip()[:1200]
        dest = root/'workspace/artifacts/health-checks'
        dest.mkdir(parents=True, exist_ok=True)
        path = dest/('host-rpc-'+dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')+'.json')
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, 'w') as f: json.dump(result, f)
        result['artifact'] = str(path)
        return result
    finally:
        lock.close()


def job_details(root):
    import re
    db = root/'state/openclaw.sqlite'
    result = []
    if not db.is_file(): return result
    with sqlite3.connect('file:'+str(db)+'?mode=ro', uri=True) as c:
        for ident, name, raw in c.execute('SELECT job_id,name,state_json FROM cron_jobs'):
            state = json.loads(raw or '{}')
            error = str(state.get('lastError', ''))[:2000]
            error = re.sub(r'(?i)(bearer\s+|(?:token|password|secret|api_key)=)\S+', r'\1[redacted]', error)
            result.append({'jobId':ident,'name':name,'lastRunAtMs':state.get('lastRunAtMs'),
                           'status':state.get('lastRunStatus'),'error':error,'lastDelivered':state.get('lastDelivered')})
    return result

if __name__ == '__main__':
    raise SystemExit(main())
