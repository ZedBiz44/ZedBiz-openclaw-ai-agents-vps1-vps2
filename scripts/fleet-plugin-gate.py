"""Require compatible loaded plugins before gateway activation."""
import json
from pathlib import Path
import subprocess
import sys

name, mode, image = sys.argv[1:]
assert name in {'wilma', 'vivian', 'grogar', 'inga', 'maggie', 'gohzed', 'edith', 'terry', 'marsha'}
assert mode in {'rehearsal', 'live'}
scripts = Path('/home/jackadmin/fleet-10.4-20261018/scripts')
subprocess.run(['python3', str(scripts/'fleet-10-4-cli.py'), name, mode, image, 'plugins', 'list', '--json'], check=True)
text = (Path('/opt/openclaw/backups/fleet-20261018')/name/(mode+'-plugins.log')).read_text()
decoder = json.JSONDecoder()
obj = None
for index, char in enumerate(text):
    if char != '{':
        continue
    try:
        candidate, _ = decoder.raw_decode(text[index:])
    except ValueError:
        continue
    if isinstance(candidate, dict) and isinstance(candidate.get('plugins'), list):
        obj = candidate
        break
assert obj is not None, 'plugin inventory unavailable'
errors = [p['id'] for p in obj['plugins'] if p.get('enabled') and p.get('status') in {'error', 'failed', 'blocked'}]
assert not errors, 'plugin failures: '+','.join(errors)
stale = [p['id'] for p in obj['plugins'] if p.get('enabled') and p.get('status') == 'loaded' and str(p.get('version', '')).startswith('2026.') and p.get('version') != '2026.10.4']
assert not stale, 'stale official plugins: '+','.join(stale)
summary = [{k: p.get(k) for k in ['id', 'version', 'status', 'origin']} for p in obj['plugins'] if p.get('enabled')]
print(json.dumps(dict(agent=name, mode=mode, pluginGatePassed=True, plugins=summary)), flush=True)

