"""Run a CLI against restored Amanda state; optional package-download network, never Docker socket."""
import json, os, pathlib, subprocess, sys
live = pathlib.Path('/opt/openclaw/agents/amanda')
work = pathlib.Path('/home/jackadmin/amanda-10.4-20261017')
stage = work/'rehearsal'
env = os.environ.copy()
env['OP_SERVICE_ACCOUNT_TOKEN'] = (live/'.op.token').read_text().strip()
p = subprocess.run(['op','run','--no-masking','--env-file',str(live/'.env'),'--','docker','compose','-f',str(live/'docker-compose.yml'),'config','--format','json'], env=env, capture_output=True, text=True)
if p.returncode: raise SystemExit('Secret/Compose resolution failed; no values printed')
cfg = json.loads(p.stdout)['services']['amanda']
assert not any('<concealed' in str(v).lower() for v in cfg.get('environment',{}).values()), 'Masked environment rejected'
network = os.environ.get('REHEARSAL_NETWORK', 'none')
assert network in ('none', 'bridge', 'openclaw')
entrypoint=os.environ.get('REHEARSAL_ENTRYPOINT','openclaw')
assert entrypoint in ('openclaw','node')
args = ['docker','run','--rm','--network',network,'--memory','4g','--memory-swap','5g','--cpus','2','--user','1000:1000','--entrypoint',entrypoint,'-v',str(work/'scripts')+':/checks:ro']
for volume in cfg['volumes']:
    source, target = volume['source'], volume['target']
    if source == '/var/run/docker.sock': continue
    if source.startswith(str(live)+'/'):
        source = str(stage/source.removeprefix(str(live)+'/'))
        suffix = ':ro' if volume.get('read_only') else ''
    else:
        suffix = ':ro'
    args += ['-v', source+':'+target+suffix]
for key, value in cfg.get('environment', {}).items():
    if value is not None:
        env[key] = str(value)
        args += ['-e', key]
args += [sys.argv[1]] + sys.argv[2:]
raise SystemExit(subprocess.run(args,env=env).returncode)

