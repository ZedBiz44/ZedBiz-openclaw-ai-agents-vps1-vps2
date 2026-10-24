import json, pathlib, subprocess
base=pathlib.Path('/root/cody-vps2-20261023')
def run(args):
 r=subprocess.run(args,text=True,capture_output=True)
 return {'code':r.returncode,'output':r.stdout+r.stderr}
out={'node':run(['node','--version']),'kernel':run(['uname','-r']),'rebootRequired':pathlib.Path('/var/run/reboot-required').exists(),'failedUnits':run(['systemctl','--failed','--no-legend']),'disk':run(['df','-h','/']),'packages':run(['apt-get','-s','upgrade']),'restartReview':run(['needrestart','-b','-r','l'])}
out['services']=run(['systemctl','show','openclaw-frank','openclaw-harry','openclaw-suzy','zedbiz-asana-mcp@frank','zedbiz-asana-mcp@harry','zedbiz-asana-mcp@suzy','caddy','-p','Id','-p','ActiveState','-p','NRestarts','-p','Result'])
out['agents']={n:json.loads((base/n/'final.json').read_text()) for n in ['frank','harry','suzy']}
(base/'postflight.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out))
