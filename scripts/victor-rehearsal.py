"""Run a CLI against a disposable restored Victor tree, without network or Docker socket."""
import json, os, pathlib, subprocess, sys
live = pathlib.Path('/opt/openclaw/agents/victor')
work = pathlib.Path('/home/jackadmin/victor-10.4-20261017')
stage = work/'rehearsal'
env = os.environ.copy()
env['OP_SERVICE_ACCOUNT_TOKEN'] = (live/'.op.token').read_text().strip()
p = subprocess.run(['op','run','--env-file',str(live/'.env'),'--','docker','compose','-f',str(live/'docker-compose.yml'),'config','--format','json'], env=env, capture_output=True, text=True)
if p.returncode: raise SystemExit('Secret/Compose resolution failed; no values printed')
cfg = json.loads(p.stdout)['services']['victor']
args = ['docker','run','--rm','--network','none','--memory','4g','--memory-swap','5g','--cpus','2','--user','1000:1000','--entrypoint','openclaw']
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
