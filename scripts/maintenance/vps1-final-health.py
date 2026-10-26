import subprocess,json,concurrent.futures,pathlib
names=['amanda','edith','gohzed','grogar','inga','maggie','marsha','terry','victor','vivian','wilma']
def check(name):
 c=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 cfg=json.loads(subprocess.check_output(['docker','exec',name,'cat','/home/node/.openclaw/openclaw.json']))
 port=cfg['gateway']['port']
 p=subprocess.run(['docker','exec',name,'curl','-fsS','--max-time','10',f'http://127.0.0.1:{port}/healthz'],capture_output=True,text=True)
 return {'agent':name,'image':c['Config']['Image'],'dockerHealth':c['State'].get('Health',{}).get('Status'),'httpHealthy':p.returncode==0,'response':p.stdout[:500]}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:r=list(pool.map(check,names))
out={'agents':r,'rebootRequired':pathlib.Path('/var/run/reboot-required').exists(),'failedServices':subprocess.check_output(['systemctl','--failed','--no-legend'],text=True),'packageAudit':subprocess.check_output(['dpkg','--audit'],text=True)}
pathlib.Path('/opt/openclaw/builds/2026.9.8-terry-20261003/final-fleet-health.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
