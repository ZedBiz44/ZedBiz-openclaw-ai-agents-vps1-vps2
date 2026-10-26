import json,pathlib,subprocess,os,hashlib
root=pathlib.Path('/opt/openclaw/agents/amanda')
env=os.environ.copy();env['OP_SERVICE_ACCOUNT_TOKEN']=(root/'.op.token').read_text().strip()
p=subprocess.run(['op','run','--no-masking','--env-file',str(root/'.env'),'--','docker','compose','-f',str(root/'docker-compose.yml'),'config','--format','json'],env=env,capture_output=True,text=True)
if p.returncode:raise SystemExit('Compose resolution failed; values not printed')
cfg=json.loads(p.stdout)
for name,c in cfg['services'].items():
 print(json.dumps({'service':name,'image':c.get('image'),'command':c.get('command'),'user':c.get('user'),'memory':c.get('mem_limit'),'swap':c.get('memswap_limit'),'ports':c.get('ports'),'volumes':c.get('volumes'),'envKeys':list(c.get('environment',{}))}))
