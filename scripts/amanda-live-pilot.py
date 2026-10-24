"""Explicit Amanda-only activation, after the isolated migration gate has passed."""
import json, os, pathlib, subprocess, sys
root=pathlib.Path('/opt/openclaw/agents/amanda')
work=pathlib.Path('/home/jackadmin/amanda-10.4-20261017')
image='zedbiz/openclaw-amanda:2026.10.4-pilot-20261017'
expected='sha256:4e5f5b8536785b8307d44e4e5ec1d83449976e149c5cd18e515880ec7336665a'
assert subprocess.check_output(['docker','image','inspect',image,'--format','{{.Id}}'],text=True).strip()==expected
env=os.environ.copy()
env['OP_SERVICE_ACCOUNT_TOKEN']=(root/'.op.token').read_text().strip()
prefix=['op','run','--env-file',str(root/'.env'),'--']
cfg_run=subprocess.run(['op','run','--no-masking','--env-file',str(root/'.env'),'--','docker','compose','-f',str(root/'docker-compose.yml'),'config','--format','json'],env=env,capture_output=True,text=True)
if cfg_run.returncode:raise SystemExit('Secret resolution failed; no values printed')
cfg=json.loads(cfg_run.stdout)['services']['amanda']
assert not any('<concealed' in str(v).lower() for v in cfg.get('environment',{}).values()), 'Masked environment rejected'
action=sys.argv[1]
if action=='migrate':
    existing=subprocess.check_output(['docker','ps','-a','--filter','name=^/amanda$','--format','{{.Names}}'],text=True).strip()
    assert not existing, 'Amanda container appeared; recheck before migration'
    captures=work/'live-doctor-captures'
    captures.mkdir(mode=0o700,exist_ok=True)
    subprocess.run(['docker','run','--rm','--network','none','--user','root','--entrypoint','chown','-v',str(captures)+':/captures',image,'1000:1000','/captures'],check=True)
    args=['docker','run','--rm','--network','openclaw','--memory','5g','--memory-swap','6g','--cpus','2','--user','1000:1000','--entrypoint','openclaw','-v',str(captures)+':/home/node/.openclaw.update-captures']
    for vol in cfg['volumes']:
        source=vol['source']
        if source=='/var/run/docker.sock':continue
        readonly=vol.get('read_only') or not source.startswith(str(root)+'/')
        args+=['-v',source+':'+vol['target']+(':ro' if readonly else '')]
    for key,value in cfg.get('environment',{}).items():
        if value is not None:env[key]=str(value);args+=['-e',key]
    raise SystemExit(subprocess.run(args+[image,'doctor','--fix','--non-interactive'],env=env).returncode)
elif action=='sidecar':
    compose=root/'docker-compose.yml'
    source=compose.read_text()
    old='zedbiz/asana-http-mcp:2.0.0-amanda-native-headings-20260929'
    assert source.count(old)==1, 'Unexpected Asana image'
    backup=work/'amanda-compose-before-sidecar.yml'
    assert not backup.exists(), 'Sidecar change already attempted'
    backup.write_text(source);backup.chmod(0o600)
    compose.write_text(source.replace(old,'zedbiz/asana-http-mcp:2.0.0-amanda-recovery-20261017'))
    raise SystemExit(subprocess.run(prefix+['docker','compose','-f',str(root/'docker-compose.yml'),'up','-d','amanda-asana-mcp'],env=env).returncode)
elif action=='activate':
    compose=root/'docker-compose.yml'
    old='zedbiz-openclaw:amanda-memory-limit-20261012'
    source=compose.read_text()
    assert source.count(old)==1, 'Unexpected source image; review concurrent changes'
    backup=work/'amanda-compose-before-activation.yml'
    assert not backup.exists(), 'Activation already attempted; inspect existing record'
    backup.write_text(source);backup.chmod(0o600)
    compose.write_text(source.replace(old,image))
    subprocess.run(['docker','compose','-f',str(compose),'config','--quiet'],check=True)
    raise SystemExit(subprocess.run([str(root/'op-start-amanda.sh'),'up'],env=env).returncode)
else:raise SystemExit('Expected migrate, sidecar or activate')
