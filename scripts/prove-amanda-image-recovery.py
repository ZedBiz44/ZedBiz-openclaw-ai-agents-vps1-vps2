"""Run only against the separately provisioned empty proof Docker daemon."""
import importlib.util
import json
from pathlib import Path
import subprocess
import time

root = Path('/opt/openclaw/recovery/amanda-20261018')
endpoint = 'unix://' + str(root/'overlay-proof/docker.sock')
spec = importlib.util.spec_from_file_location('driver', Path(__file__).with_name('amanda-host-start.py'))
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
m = json.loads((root/'manifest.json').read_text())


def isolated(args, **kwargs):
    if args[0] == '/usr/bin/docker' and 'compose' not in args:
        args = [args[0], '-H', endpoint] + args[1:]
    return d.command(args, **kwargs)


rc, output = isolated(['/usr/bin/docker', 'image', 'ls', '-q'])
assert rc == 0 and not output.strip(), 'proof daemon must start empty'
start = time.monotonic()
d.recover(m, isolated)
for item in m['images']:
    rc, actual = isolated(['/usr/bin/docker', 'image', 'inspect', '--format', '{{.Id}}', item['ref']])
    assert rc == 0 and actual.strip() == item['id']
duration = round(time.monotonic() - start, 1)
print('Recovered in', duration, 'seconds', flush=True)
rc, version = isolated(['/usr/bin/docker', 'run', '--rm', '--network', 'none',
                       '--memory', '768m', '--entrypoint', 'node',
                       m['images'][0]['ref'], '/app/openclaw.mjs', '--version'], timeout=120)
assert rc == 0 and '2026.10.4' in version
result = dict(restoredAndVerified=True, seconds=duration, archiveSha256=m['sha256'],
              version=version.strip(), isolatedDriver='overlay2')
(root/'restore-proof.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result), flush=True)

