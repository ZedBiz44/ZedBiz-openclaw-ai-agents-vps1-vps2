"""Stop one idle gateway, verify offline recovery, and prepare its isolated copy."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

name = sys.argv[1]
assert name in {'wilma', 'vivian', 'grogar', 'inga', 'maggie', 'gohzed', 'edith', 'terry', 'marsha'}
live = Path('/opt/openclaw/agents')/name
work = Path('/opt/openclaw/backups/fleet-20261018')/name
work.mkdir(mode=0o700, parents=True, exist_ok=True)
archive = work/'before-10.4.tar'
assert not archive.exists(), 'existing recovery point; inspect before continuing'

def rpc(method, params=None):
    args = ['docker', 'exec', '-u', 'node', name, 'node', '/app/openclaw.mjs', 'gateway', 'call', method, '--json']
    if params:
        args += ['--params', json.dumps(params)]
    p = subprocess.run(args, capture_output=True, text=True, timeout=90)
    assert p.returncode == 0, 'baseline RPC failed; output withheld'
    value = json.loads(p.stdout[p.stdout.index('{'):])
    out = work/(method+'-before.json')
    out.write_text(json.dumps(value)); out.chmod(0o600)
    return value

status = rpc('status')
work_state = status.get('shutdownBudget', {}).get('activeWork')
assert work_state is not None and all(v == 0 for v in work_state.values()), 'active or unknown work; wait before stopping'
jobs = rpc('cron.list', {'includeDisabled': True})
assert not any(j.get('state', {}).get('runningAtMs') for j in jobs['jobs']), 'scheduled work active'
rpc('health')
inspect = json.loads(subprocess.check_output(['docker', 'inspect', name], text=True))[0]
baseline = dict(image=inspect['Image'], ref=inspect['Config']['Image'], containerId=inspect['Id'], cronCount=len(jobs['jobs']))
subprocess.run(['systemctl', 'stop', 'openclaw-'+name+'.service'], check=True, timeout=180)
assert subprocess.run(['docker', 'inspect', name], capture_output=True).returncode != 0, 'managed stop did not remove gateway'
print(name, 'stopped; creating verified offline archive', flush=True)
paths = ['agents/'+name]
external = Path('/opt/openclaw/shared/external-memory/lancedb')/name
if external.exists():
    paths.append('shared/external-memory/lancedb/'+name)
subprocess.run(['tar', '-C', '/opt/openclaw', '--exclude=agents/'+name+'/.op.token',
                '--exclude=agents/'+name+'/.env.resolved', '-cf', str(archive)]+paths, check=True, timeout=600)
archive.chmod(0o600)
with archive.open('rb') as stream:
    baseline['archiveSha256'] = hashlib.file_digest(stream, 'sha256').hexdigest()
subprocess.run(['tar', '-tf', str(archive)], stdout=subprocess.DEVNULL, check=True, timeout=120)
restore = work/'extracted'
restore.mkdir(mode=0o700)
subprocess.run(['tar', '-xf', str(archive), '-C', str(restore)], check=True, timeout=600)
(restore/'agents'/name).rename(work/'rehearsal')
for root in [live, work/'rehearsal']:
    db = root/'config/state/openclaw.sqlite'
    with sqlite3.connect('file:'+str(db)+'?mode=ro', uri=True) as conn:
        conn.create_function('octet_length', 1, lambda x: len(x.encode() if isinstance(x, str) else x), deterministic=True)
        assert conn.execute('PRAGMA quick_check').fetchall() == [('ok',)]
    backup = root/'config/backups/tools-md-migration'
    backup.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chown(backup, 1000, 1000); backup.chmod(0o700)
out = work/'baseline.json'
out.write_text(json.dumps(baseline, indent=2)); out.chmod(0o600)
print(json.dumps(dict(agent=name, archive=str(archive), **baseline)), flush=True)

