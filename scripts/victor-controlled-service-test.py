"""Approved Victor-only lifecycle proof. Run as host root after activation."""
import hashlib
import json
from pathlib import Path
import subprocess
import sqlite3
import time

root = Path('/opt/openclaw/recovery/victor-20261018')


def rpc(method):
    p = subprocess.run(['docker', 'exec', '-u', 'node', 'victor', 'node',
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
assert subprocess.check_output(['systemctl', 'is-active', 'openclaw-victor.service'], text=True).strip() == 'active'
before = inspect('victor')['Id']
amanda_before = inspect('amanda')['Id']
print('Idle verified; stopping Victor through managed service', flush=True)
subprocess.run(['systemctl', 'stop', 'openclaw-victor.service'], check=True, timeout=180)
assert subprocess.run(['docker', 'inspect', 'victor'], capture_output=True).returncode != 0
for db in ['/opt/openclaw/agents/victor/config/state/openclaw.sqlite',
           '/opt/openclaw/agents/victor/agents/main/agent/openclaw-agent.sqlite']:
    with sqlite3.connect('file:'+db+'?mode=ro', uri=True) as connection:
        assert connection.execute('PRAGMA quick_check').fetchall() == [('ok',)]
print('Managed stop removed Victor container; taking offline state backup', flush=True)
archive = root/'victor-offline-state-before-cycle.tar'
assert not archive.exists()
subprocess.run(['tar', '-C', '/opt/openclaw', '--exclude=agents/victor/.op.token',
                '--exclude=agents/victor/.env.resolved', '-cf', str(archive),
                'agents/victor', 'shared/external-memory/lancedb/victor'], check=True, timeout=600)
archive.chmod(0o600)
with archive.open('rb') as stream:
    archive_hash = hashlib.file_digest(stream, 'sha256').hexdigest()
subprocess.run(['tar', '-tf', str(archive)], stdout=subprocess.DEVNULL, check=True, timeout=120)
print('Offline archive verified; starting Victor through repaired service', flush=True)
start = time.monotonic()
subprocess.run(['systemctl', 'start', 'openclaw-victor.service'], check=True, timeout=1510)
after = inspect('victor')['Id']
assert before != after
assert inspect('amanda')['Id'] == amanda_before
result = dict(before=before, after=after, changed=True, amandaUnchanged=True,
              offlineArchive=str(archive), offlineArchiveSha256=archive_hash,
              startupCommandSeconds=round(time.monotonic()-start, 1))
(root/'service-cycle-proof.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result), flush=True)
