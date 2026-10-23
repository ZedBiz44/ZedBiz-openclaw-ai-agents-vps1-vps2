"""Run on VPS1 as root. Change one agent, preserving exact rollback files."""
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path('/opt/openclaw/recovery/wiki-lock-20261023')
agent = sys.argv[1]
images = json.loads((ROOT / 'images.json').read_text())
if agent not in images:
    raise SystemExit('Unknown agent')
entry = images[agent]
base = pathlib.Path('/opt/openclaw/agents') / agent
manifest = pathlib.Path('/opt/openclaw/recovery') / (agent + '-20261018') / 'manifest.json'
if not manifest.exists():
    manifest = pathlib.Path('/opt/openclaw/recovery/fleet-20261018') / agent / 'manifest.json'
compose = base / 'docker-compose.yml'
poststart = base / 'workspace/post-start.sh'
backup = ROOT / 'rollback' / agent
backup.mkdir(parents=True, exist_ok=True)

if sys.argv[2] == 'stage':
    archive = json.loads((ROOT / 'archive.json').read_text())
    if not pathlib.Path(archive['archive']).is_file():
        raise SystemExit('Recovery archive missing')
    text = compose.read_text()
    if text.count(entry['before']) != 1:
        raise SystemExit('Unexpected Compose image; refusing edit')
    data = json.loads(manifest.read_text())
    selected = [i for i in data['images'] if i['ref'] == entry['before']]
    # These three saved manifests predate the verified workshop image changes.
    stale_refs = {
        'amanda': 'zedbiz/amanda:2026.10.4-components-20261018',
        'maggie': 'zedbiz/openclaw-base:2026.10.4-components-20261018',
        'wilma': 'zedbiz/openclaw-base:2026.10.4-components-20261018',
    }
    if not selected and agent in stale_refs:
        selected = [i for i in data['images'] if i['ref'] == stale_refs[agent]]
    if len(selected) != 1:
        raise SystemExit('Recovery manifest does not match live image; inspect before editing')
    for file, name in [(compose, 'docker-compose.yml'), (poststart, 'post-start.sh'), (manifest, 'manifest.json')]:
        if (backup / name).exists():
            raise SystemExit('Backup already exists; do not overwrite rollback')
        shutil.copy2(file, backup / name)
    image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', entry['after']]))[0]
    selected[0]['ref'] = entry['after']
    selected[0]['id'] = image['Id']
    data.update(archive)
    compose.write_text(text.replace(entry['before'], entry['after']))
    script = poststart.read_text()
    first, rest = script.split('\n', 1)
    guard = 'python3 /opt/zedbiz/wiki-lock/verify.py || exit $? # shared-wiki-upgrade-gate\n'
    poststart.write_text(first + '\n' + guard + rest)
    manifest.write_text(json.dumps(data, indent=2) + '\n')
    print(agent, 'staged; backups preserved', flush=True)
elif sys.argv[2] == 'activate':
    # Let existing work drain before image replacement. Never print startup
    # wrapper output: secret-resolution errors can contain sensitive values.
    stop = subprocess.run(['docker', 'stop', '--time', '330', agent], capture_output=True, timeout=350)
    if stop.returncode:
        raise SystemExit('Orderly stop failed')
    wrapper = json.loads(manifest.read_text())['wrapper']
    result = subprocess.run([wrapper, 'up'], capture_output=True, timeout=240)
    print(agent, 'startup wrapper exit', result.returncode, flush=True)
    if result.returncode:
        raise SystemExit('Startup failed; inspect privately before retrying')
elif sys.argv[2] == 'rollback':
    files = [(compose, 'docker-compose.yml'), (poststart, 'post-start.sh'), (manifest, 'manifest.json')]
    if not all((backup / name).is_file() for _, name in files):
        raise SystemExit('Complete rollback set missing')
    stop = subprocess.run(['docker', 'stop', '--time', '330', agent], capture_output=True, timeout=350)
    if stop.returncode:
        raise SystemExit('Orderly stop failed')
    for target, name in files:
        shutil.copy2(backup / name, target)
    wrapper = json.loads(manifest.read_text())['wrapper']
    result = subprocess.run([wrapper, 'up'], capture_output=True, timeout=240)
    print(agent, 'rollback startup exit', result.returncode, flush=True)
    sys.exit(result.returncode)
else:
    raise SystemExit('Expected stage, activate, or rollback')
