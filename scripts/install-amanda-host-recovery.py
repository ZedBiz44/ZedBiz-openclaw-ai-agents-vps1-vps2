"""Apply the approved Amanda-only integration after isolated restore proof."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

root = Path('/opt/openclaw/recovery/amanda-20261018')
stage = Path('/home/jackadmin/amanda-host-recovery-20261018')
proof = json.loads((root/'restore-proof.json').read_text())
assert proof['restoredAndVerified']
manifest = json.loads((root/'manifest.json').read_text())
assert proof['archiveSha256'] == manifest['sha256']
backup = root/'before-service-repair'
backup.mkdir(mode=0o700)
for source in ['/etc/systemd/system/openclaw-amanda.service',
               '/opt/openclaw/agents/amanda/op-start-amanda.sh',
               '/opt/openclaw/agents/amanda/docker-compose.yml',
               '/opt/openclaw/agents/amanda/config/openclaw.json']:
    target = backup/Path(source).name
    shutil.copy2(source, target)
    target.chmod(0o600)
dropdir = Path('/etc/systemd/system/openclaw-amanda.service.d')
assert not dropdir.exists(), 'unexpected existing drop-ins; inspect first'
shutil.copy2(stage/'amanda-host-start.py', root/'amanda-host-start.py')
(root/'amanda-host-start.py').chmod(0o700)
for name in ['images.tar', 'manifest.json', 'amanda-host-start.py']:
    os.chown(root/name, 0, 0)
os.chown(root, 0, 0)
root.chmod(0o700)
dropdir.mkdir(mode=0o755)
shutil.copy2(stage/'amanda-host-recovery.conf', dropdir/'recovery.conf')
(dropdir/'recovery.conf').chmod(0o644)
subprocess.run(['systemd-analyze', 'verify', 'openclaw-amanda.service'], check=True)
subprocess.run(['systemctl', 'daemon-reload'], check=True)
print(json.dumps({'installed': True, 'backup': str(backup), 'driverSha256':
                 hashlib.sha256((root/'amanda-host-start.py').read_bytes()).hexdigest()}))

