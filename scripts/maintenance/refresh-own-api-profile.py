import os,sqlite3,pathlib,subprocess,json,urllib.request,urllib.error
key=os.environ.get('OPENAI_API_KEY','')
config_path=pathlib.Path('/home/node/.openclaw/openclaw.json')
original_order=json.loads(config_path.read_text()).get('auth',{}).get('order')
if len(key)<16 or key.startswith('op://'):raise SystemExit('Resolved OpenAI API credential unavailable')
request=urllib.request.Request('https://api.openai.com/v1/models/gpt-6.1-sol',headers={'Authorization':'Bearer '+key})
try:
 with urllib.request.urlopen(request,timeout=30) as response:
  data=json.load(response)
  assert data.get('id')=='gpt-6.1-sol'
except urllib.error.HTTPError as e:raise SystemExit('Existing protected API credential model access returned HTTP '+str(e.code))
b=pathlib.Path('/home/node/.openclaw/workspace/.cody-model-auth-refresh-backup-20261003');b.mkdir(mode=0o700,exist_ok=False)
for name,source in [('state','/home/node/.openclaw/state/openclaw.sqlite'),('main','/home/node/.openclaw/agents/main/agent/openclaw-agent.sqlite')]:
 with sqlite3.connect('file:'+source+'?mode=ro',uri=True) as old,sqlite3.connect(b/(name+'.sqlite')) as new:old.backup(new)
 os.chmod(b/(name+'.sqlite'),0o600)
p=subprocess.run(['openclaw','models','auth','paste-api-key','--provider','openai','--profile-id','openai:api-key-backup','--agent','main'],input=key+'\n',capture_output=True,text=True,timeout=90)
if p.returncode:raise SystemExit('API profile import failed; secret output withheld')
config=json.loads(config_path.read_text())
if original_order is None:config.get('auth',{}).pop('order',None)
else:config.setdefault('auth',{})['order']=original_order
config_path.write_text(json.dumps(config,indent=2)+'\n')
print('Own protected API credential has Sol access; profile refreshed through supported CLI after database backup. No secret values printed.')
