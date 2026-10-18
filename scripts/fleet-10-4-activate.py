"""Activate one migrated agent with matching image-recovery metadata."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

name = sys.argv[1]
assert name in {'wilma', 'vivian', 'grogar', 'inga', 'maggie', 'gohzed', 'edith', 'terry', 'marsha'}
live = Path('/opt/openclaw/agents')/name
work = Path('/opt/openclaw/backups/fleet-20261018')/name
recovery = Path('/opt/openclaw/recovery/fleet-20261018')
artifact_root = recovery/'workshop' if name in {'marsha', 'grogar'} else recovery
catalog = json.loads((artifact_root/'catalog.json').read_text())
proof = json.loads((artifact_root/'archive-proof.json').read_text())
assert proof['allImageIdsVerified'] and proof['archiveSha256'] == catalog['sha256']
assert not subprocess.check_output(['docker', 'ps', '-q', '--filter', f'name=^/{name}$'], text=True).strip()
baseline = json.loads((work/'baseline.json').read_text())
image = ('zedbiz/'+name+':2026.10.4-workshop-20261018') if name in {'marsha', 'grogar'} else 'zedbiz/openclaw-base:2026.10.4-fleet-20261018'
compose = live/'docker-compose.yml'
source = compose.read_text()
assert source.count(baseline['ref']) == 1, 'unexpected current image declaration'
shutil.copy2(compose, work/'compose-before-activation.yml')
compose.write_text(source.replace(baseline['ref'], image))
p = subprocess.run(['docker', 'compose', '--env-file', '.env', 'config', '--images'], cwd=live, capture_output=True, text=True)
assert p.returncode == 0, 'Compose validation failed'
refs = set(p.stdout.split())
identities = {x['ref']: x['id'] for x in catalog['images']}
assert image in refs and refs <= identities.keys(), 'unarchived image selected'
for ref in refs:
    assert subprocess.check_output(['docker', 'image', 'inspect', '--format', '{{.Id}}', ref], text=True).strip() == identities[ref]
wrapper = live/('op-start-'+name+'.sh')
manifest = dict(wrapper=str(wrapper), wrapper_sha256=hashlib.sha256(wrapper.read_bytes()).hexdigest(),
                archive=catalog['archive'], sha256=catalog['sha256'],
                images=[dict(ref=ref, id=identities[ref], automatic=True) for ref in sorted(refs)])
agent_recovery = recovery/name
agent_recovery.mkdir(mode=0o700)
(agent_recovery/'manifest.json').write_text(json.dumps(manifest, indent=2))
(agent_recovery/'manifest.json').chmod(0o600)
driver = recovery/'fleet-host-start.py'
expected_driver = Path('/home/jackadmin/fleet-10.4-20261018/scripts/fleet-host-start.py')
if driver.exists():
    assert driver.read_bytes() == expected_driver.read_bytes(), 'unexpected existing driver'
else:
    shutil.copy2(expected_driver, driver); driver.chmod(0o700)
dropdir = Path('/etc/systemd/system/openclaw-'+name+'.service.d')
assert not dropdir.exists(), 'inspect existing overrides first'
shutil.copy2('/etc/systemd/system/openclaw-'+name+'.service', work/'original.service')
dropdir.mkdir(mode=0o755)
(dropdir/'recovery.conf').write_text('[Unit]\nWants=network-online.target\n[Service]\nExecStart=\nExecStart=/usr/bin/python3 '+str(driver)+' '+name+'\nTimeoutStartSec=1500\n')
(dropdir/'recovery.conf').chmod(0o644)
subprocess.run(['systemd-analyze', 'verify', 'openclaw-'+name+'.service'], check=True)
subprocess.run(['systemctl', 'daemon-reload'], check=True)
subprocess.run(['systemctl', 'start', 'openclaw-'+name+'.service'], check=True, timeout=1510)
print(json.dumps(dict(agent=name, activated=True, image=image, imageId=identities[image])), flush=True)

