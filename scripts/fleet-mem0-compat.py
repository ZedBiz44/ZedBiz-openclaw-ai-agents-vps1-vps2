"""Preserve the reviewed Mem0 repair on 10.4 and prove it on the selected tree."""
import json
import os
from pathlib import Path
import subprocess
import sys

name, mode, image = sys.argv[1:]
assert name in {'edith', 'terry'} and mode in {'rehearsal', 'live'}
work = Path('/opt/openclaw/backups/fleet-20261018')/name
root = work/'rehearsal' if mode == 'rehearsal' else Path('/opt/openclaw/agents')/name
if mode == 'live':
    assert not subprocess.check_output(['docker', 'ps', '-q', '--filter', f'name=^/{name}$'], text=True).strip()
target = root/'config/scripts/repair-mem0-host-peer.mjs'
old = target.read_text()
assert 'Review host-link compatibility for this OpenClaw version' in old and '1.2.1' in old
backup = work/(mode+'-mem0-host-peer-before.mjs')
if not backup.exists():
    backup.write_text(old); backup.chmod(0o600)
source = Path('/home/jackadmin/fleet-10.4-20261018/scripts/repair-mem0-host-peer.mjs').read_text()
target.write_text(source); os.chown(target, 1000, 1000)
log = work/(mode+'-mem0-compat.log')
with log.open('w') as stream:
    log.chmod(0o600)
    p = subprocess.run(['docker', 'run', '--rm', '--network', 'none', '--user', '1000:1000',
        '-v', str(root/'config')+':/home/node/.openclaw',
        '-v', str(root/'npm')+':/home/node/.openclaw/npm',
        '-v', str(root/'workspace')+':/home/node/.openclaw/workspace',
        '--entrypoint', 'sh', image, '/home/node/.openclaw/workspace/ensure-mem0-compat.sh'],
        stdout=stream, stderr=subprocess.STDOUT, timeout=120)
assert p.returncode == 0, 'Mem0 compatibility gate failed; inspect protected log'
print(json.dumps(dict(agent=name, mode=mode, mem0Compatibility=True)), flush=True)

