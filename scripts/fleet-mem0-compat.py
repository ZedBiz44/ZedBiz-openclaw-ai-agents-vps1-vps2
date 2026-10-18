"""Preserve the reviewed Mem0 repair on 10.4 and prove it on the selected tree."""
import hashlib
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
source = Path('/home/jackadmin/fleet-10.4-20261018/scripts/repair-mem0-host-peer.mjs').read_text()
assert hashlib.sha256(target.read_bytes()).hexdigest() == '658c317f21846b4c37341af013f973b01de13c3cbad8b1de3a1ef8d8cebed978' or old == source, 'unreviewed host-peer helper'
for relative, expected in {
    'workspace/ensure-mem0-compat.sh': '924eb9cd29bb7650382f36f5d7543f29278f6312b906a43644a535fa98c8a327',
    'config/scripts/repair-mem0-explicit-retention.py': '7f45decfaef5c11f32ac2f8c6bf66d6c9e192c84e4f726db99c499849cc05a3f',
}.items():
    assert hashlib.sha256((root/relative).read_bytes()).hexdigest() == expected, 'unreviewed Mem0 compatibility source'
backup = work/(mode+'-mem0-host-peer-before.mjs')
if not backup.exists():
    backup.write_text(old); backup.chmod(0o600)
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

