"""Preserve the reviewed Mem0 repair on 10.4 and prove it on the selected tree."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sqlite3
import shutil
import sys

name, mode, image = sys.argv[1:]
assert name in {'edith', 'terry'} and mode in {'rehearsal', 'live'}
work = Path('/opt/openclaw/backups/fleet-20261018')/name
if name == 'terry' and mode == 'live' and not (work/'rehearsal-mem0-consent.json').exists():
    subprocess.run(['python3', __file__, name, 'rehearsal', image], check=True)
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
manifests = list((root/'npm/projects').glob('mem0-*/node_modules/@mem0/openclaw-mem0/openclaw.plugin.json'))
assert len(manifests) == 1, 'ambiguous Mem0 package'
manifest = manifests[0]
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == 'b41def82737a590fe97633e2dbf1c95c1a4e2ad3019257bd16bd0e2b42122309', 'Mem0 capability declarations changed from original'
assert hashlib.sha256((manifest.parent/'dist/index.js').read_bytes()).hexdigest() == '0e7205db54c8790c1aff7b09786ec0b7578db08181b5394a7137df4e530297c2', 'Mem0 implementation changed from original'
before = json.loads((root/'config/openclaw.json').read_text())
assert before['plugins']['entries']['openclaw-mem0']['enabled'] is True
# 10.4 enforces consent for two read aliases already present in the approved
# 9.8 plugin. Accept only the byte-identical existing implementation/declarations.
subprocess.run(['python3', '/home/jackadmin/fleet-10.4-20261018/scripts/fleet-10-4-cli.py',
    name, mode, image, 'plugins', 'enable', 'openclaw-mem0', '--accept-capabilities'], check=True)
shutil.copy2(work/(mode+'-plugins.log'), work/(mode+'-mem0-consent-command.log'))
after = json.loads((root/'config/openclaw.json').read_text())
assert before.get('plugins') == after.get('plugins'), 'plugin policy changed unexpectedly'
with sqlite3.connect('file:'+str(root/'config/state/openclaw.sqlite')+'?mode=ro',uri=True) as db:
    index = json.loads(db.execute("SELECT value_json FROM config_machine_state WHERE state_key='plugins.installedIndex'").fetchone()[0])['index']
    accepted = index['installRecords']['openclaw-mem0']['acceptedSurface']
expected_tools = set(json.loads(manifest.read_text())['contracts']['tools'])
assert set(accepted['tools']) == expected_tools, 'accepted tool set differs from retained plugin'
assert not any(accepted.get(k) for k in ['channels','providers','hooks','mcpServers','cliCommands','cliBackends','dangerousConfigFlags']), 'unexpected additional capability'
result = dict(agent=name, mode=mode, mem0Compatibility=True, retainedCapabilityConsentVerified=True, acceptedTools=sorted(expected_tools))
receipt = work/(mode+'-mem0-consent.json')
receipt.write_text(json.dumps(result)); receipt.chmod(0o600)
print(json.dumps(result), flush=True)

