"""Import fleet archive into an empty independent production-format image store."""
import hashlib
import json
from pathlib import Path
import subprocess
import time

root = Path('/opt/openclaw/recovery/fleet-20261018')
p = root/'native-proof'
p.mkdir(mode=0o700)
(p/'daemon.json').write_text('{}')
(p/'containerd.toml').write_text('version = 3\ndisabled_plugins = ["io.containerd.cri.v1.images", "io.containerd.cri.v1.runtime", "io.containerd.grpc.v1.cri"]\n')
catalog = json.loads((root/'catalog.json').read_text())
with Path(catalog['archive']).open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest() == catalog['sha256']
base = ['docker', 'run', '-d', '--privileged', '--pid=host', '--network', 'none']
ns = ['alpine', 'nsenter', '-t', '1', '-m', '-u', '-i', '-n', '-p', '--']
subprocess.run(base+['--name', 'fleet-containerd-proof']+ns+['/usr/bin/containerd', '--config', str(p/'containerd.toml'), '--root', str(p/'containerd-data'), '--state', str(p/'containerd-state'), '--address', str(p/'containerd.sock')], check=True)
for _ in range(30):
    if (p/'containerd.sock').exists():
        break
    time.sleep(1)
subprocess.run(base+['--name', 'fleet-image-restore-proof']+ns+['/usr/bin/dockerd', '--config-file='+str(p/'daemon.json'), '--data-root='+str(p/'data'), '--exec-root='+str(p/'exec'), '--pidfile='+str(p/'docker.pid'), '--host=unix://'+str(p/'docker.sock'), '--containerd='+str(p/'containerd.sock'), '--feature=containerd-snapshotter=true', '--storage-driver=overlayfs', '--bridge=none', '--iptables=false', '--ip6tables=false', '--ip-forward=false', '--ip-masq=false', '--containerd-namespace=fleet-native-proof', '--containerd-plugins-namespace=fleet-native-proof-plugins'], check=True)
docker = ['docker', '-H', 'unix://'+str(p/'docker.sock')]
for _ in range(30):
    if subprocess.run(docker+['info'], capture_output=True).returncode == 0:
        break
    time.sleep(1)
else:
    raise RuntimeError('isolated daemon unavailable')
assert not subprocess.check_output(docker+['image', 'ls', '-q'], text=True).strip()
start = time.monotonic()
subprocess.run(docker+['image', 'load', '-i', catalog['archive']], check=True, stdout=subprocess.DEVNULL, timeout=600)
for item in catalog['images']:
    assert subprocess.check_output(docker+['image', 'inspect', '--format', '{{.Id}}', item['ref']], text=True).strip() == item['id']
for image in ['zedbiz/openclaw-base:2026.10.4-fleet-20261018', 'zedbiz/marsha:2026.10.4-fleet-20261018']:
    version = subprocess.check_output(docker+['run', '--rm', '--network', 'none', '--memory', '768m', '--entrypoint', 'node', image, '/app/openclaw.mjs', '--version'], text=True, timeout=120)
    assert '2026.10.4' in version
result = dict(allImageIdsVerified=True, imageCount=len(catalog['images']), archiveSha256=catalog['sha256'], seconds=round(time.monotonic()-start, 1), versionsVerified=True)
(root/'archive-proof.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result), flush=True)

