import json,pathlib,subprocess
work=pathlib.Path('/home/jackadmin/amanda-10.4-20261017')
p=subprocess.run(['docker','exec','amanda','openclaw','health','--json'],capture_output=True,text=True)
(work/'live-health.json').write_text(p.stdout)
(work/'live-health.stderr').write_text(p.stderr)
j=json.loads(p.stdout)
def safe(v):
    return {k:v[k] for k in ['configured','enabled','running','connected','ok','status'] if k in v}|({'probeOk':v['probe'].get('ok')} if isinstance(v.get('probe'),dict) else {})
print(json.dumps({'exit':p.returncode,'ok':j.get('ok'),'channels':{k:safe(v)|{'accounts':{a:safe(b) for a,b in v.get('accounts',{}).items()}} for k,v in j.get('channels',{}).items()}},indent=2))
raise SystemExit(p.returncode)

