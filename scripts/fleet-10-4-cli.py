"""Explicit one-agent CLI runner for the approved 10.4 migration.

All captured output is private. A rehearsal maps agent mounts to a restored tree;
shared mounts are read-only and the Docker socket is never exposed.
"""
import json
import os
from pathlib import Path
import subprocess
import sys

name, mode, image, *command = sys.argv[1:]
assert name in {'wilma', 'vivian', 'grogar', 'inga', 'maggie', 'gohzed', 'edith', 'terry', 'marsha'}
assert mode in {'rehearsal', 'live'} and command
live = Path('/opt/openclaw/agents') / name
work = Path('/opt/openclaw/backups/fleet-20261018') / name
target = work/'rehearsal' if mode == 'rehearsal' else live
if mode == 'live':
    assert not subprocess.check_output(['docker', 'ps', '-q', '--filter', f'name=^/{name}$'], text=True).strip(), 'stop gateway before live migration'
env = os.environ.copy()
env['OP_SERVICE_ACCOUNT_TOKEN'] = (live/'.op.token').read_text().strip()
p = subprocess.run(['op', 'run', '--no-masking', '--env-file', str(live/'.env'), '--',
                    'docker', 'compose', '-f', str(live/'docker-compose.yml'), 'config', '--format', 'json'],
                   env=env, capture_output=True, text=True, timeout=60)
assert p.returncode == 0, 'secret resolution failed; output withheld'
cfg = json.loads(p.stdout)['services'][name]
assert not any('<concealed' in str(v).lower() for v in cfg.get('environment', {}).values())
captures = work/(mode+'-captures')
captures.mkdir(mode=0o700, exist_ok=True)
os.chown(captures, 1000, 1000)
args = ['docker', 'run', '--rm', '--name', name+'-migration-check', '--network', 'openclaw',
        '--memory', '5g', '--memory-swap', '6g', '--cpus', '2', '--user', '1000:1000',
        '--entrypoint', 'openclaw', '-v', str(captures)+':/home/node/.openclaw.update-captures']
for v in cfg['volumes']:
    source = v['source']
    if source in {'/var/run/docker.sock', '/dev/shm'}:
        continue
    if source.startswith(str(live)+'/'):
        source = str(target/source.removeprefix(str(live)+'/'))
        readonly = v.get('read_only', False)
    else:
        readonly = True
    args += ['-v', source+':'+v['target']+(':ro' if readonly else '')]
for key, value in cfg.get('environment', {}).items():
    if value is not None:
        env[key] = str(value)
        args += ['-e', key]
out = work/(mode+'-'+command[0]+'.log')
with out.open('w') as stream:
    out.chmod(0o600)
    result = subprocess.run(args+[image]+command, env=env, stdout=stream, stderr=subprocess.STDOUT)
print(json.dumps(dict(agent=name, mode=mode, command=command, exit=result.returncode, privateLog=str(out))), flush=True)
raise SystemExit(result.returncode)

