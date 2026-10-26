"""Approved Amanda-only lifecycle proof. Run as host root after activation."""
import hashlib
import json
from pathlib import Path
import subprocess
import sqlite3
import time

root = Path('/opt/openclaw/recovery/amanda-20261018')


def rpc(method):
    p = subprocess.run(['docker', 'exec', '-u', 'node', 'amanda', 'node',
                        '/app/openclaw.mjs', 'gateway', 'call', method, '--json'],
                       capture_output=True, text=True, timeout=60, check=True)
    return json.loads(p.stdout[p.stdout.index('{'):])


def inspect(name):
    return json.loads(subprocess.check_output(['docker', 'inspect', name], text=True))[0]


status = rpc('status')
work = status['shutdownBudget']['activeWork']
assert all(v == 0 for v in work.values()), 'active work; do not stop'
# Informational system notices are not running requests. Preserve their receipt.
receipt = root/'status-before-cycle.json'
receipt.write_text(json.dumps(status)+'\n')
receipt.chmod(0o600)
assert subprocess.check_output(['systemctl', 'is-active', 'openclaw-amanda.service'], text=True).strip() == 'active'
before = inspect('amanda')['Id']
victor_before = inspect('victor')['Id']
print('Idle verified; stopping Amanda through managed service', flush=True)
subprocess.run(['systemctl', 'stop', 'openclaw-amanda.service'], check=True, timeout=180)
assert subprocess.run(['docker', 'inspect', 'amanda'], capture_output=True).returncode != 0
for db in ['/opt/openclaw/agents/amanda/config/state/openclaw.sqlite',
           '/opt/openclaw/agents/amanda/agents/main/agent/openclaw-agent.sqlite']:
    with sqlite3.connect('file:'+db+'?mode=ro', uri=True) as connection:
        assert connection.execute('PRAGMA quick_check').fetchall() == [('ok',)]
print('Managed stop removed Amanda container; taking offline state backup', flush=True)
archive = root/'amanda-offline-state-before-cycle.tar'
assert not archive.exists()
subprocess.run(['tar', '-C', '/opt/openclaw', '--exclude=agents/amanda/.op.token',
                '--exclude=agents/amanda/.env.resolved', '-cf', str(archive),
                'agents/amanda', 'shared/external-memory/lancedb/amanda'], check=True, timeout=600)
archive.chmod(0o600)
with archive.open('rb') as stream:
    archive_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
subprocess.run(['tar', '-tf', str(archive)], stdout=subprocess.DEVNULL, check=True, timeout=120)
print('Offline archive verified; starting Amanda through repaired service', flush=True)
start = time.monotonic()
subprocess.run(['systemctl', 'start', 'openclaw-amanda.service'], check=True, timeout=1510)
after = inspect('amanda')['Id']
assert before != after
assert inspect('victor')['Id'] == victor_before
result = dict(before=before, after=after, changed=True, victorUnchanged=True,
              offlineArchive=str(archive), offlineArchiveSha256=archive_hash,
              startupCommandSeconds=round(time.monotonic()-start, 1))
(root/'service-cycle-proof.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result), flush=True)

