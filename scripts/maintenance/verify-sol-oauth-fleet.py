import json,subprocess,pathlib,concurrent.futures
root=pathlib.Path('/opt/openclaw/builds/2026.9.8-terry-20261003')
names=['terry','amanda','edith','gohzed','grogar','inga','maggie','victor','vivian','wilma']
def check(n):
 def cfg(p):return json.loads(subprocess.check_output(['docker','exec',n,'cat',p]))
 c=cfg('/home/node/.openclaw/openclaw.json');old=cfg('/home/node/.openclaw/openclaw.json.before-sol-oauth-runtime-20261003')
 d=c['agents']['defaults'];od=old['agents']['defaults'];a=c['plugins']['entries']['codex']['config']['appServer']
 proof=json.loads((root/(n+'-oauth-sol-summary.json')).read_text())
 checks={'primaryOAuth':d['model']['primary']=='openai/gpt-6.1-sol@openai:jzedbiz@gmail.com','oauthOnlyOrder':c['auth']['order']['openai']==['openai:jzedbiz@gmail.com'],'executable':a['command']=='/usr/local/bin/codex','apiEnvironmentCleared':all(x in a['clearEnv'] for x in ['OPENAI_API_KEY','CODEX_API_KEY','OPENAI_AUTH_TOKEN']),'fallbacksPreserved':d['model']['fallbacks']==od['model']['fallbacks'],'thinkingPreserved':d.get('thinkingDefault')==od.get('thinkingDefault'),'skillsPreserved':c.get('skills')==old.get('skills'),'memorySlotPreserved':c['plugins'].get('slots')==old['plugins'].get('slots'),'exactSol':proof['trace']['winnerModel']=='gpt-6.1-sol','noFallback':proof['trace']['fallbackUsed'] is False,'toolsPassed':proof['tools']['calls']>=2 and proof['tools']['failures']==0}
 version=subprocess.check_output(['docker','exec',n,'/usr/local/bin/codex','--version'],text=True).strip();checks['codexVersion']=version=='codex-cli 0.160.0'
 p=subprocess.run(['docker','exec',n,'curl','-fsS','--max-time','10','http://127.0.0.1:'+str(c['gateway']['port'])+'/healthz'],capture_output=True);checks['httpHealthy']=p.returncode==0
 return {'agent':n,'primary':d['model']['primary'],'checks':checks,'runId':proof['runId'],'tools':proof['tools'],'codexVersion':version}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(check,names))
c=json.loads(subprocess.check_output(['docker','exec','marsha','cat','/home/node/.openclaw/openclaw.json']))
p=subprocess.run(['docker','exec','marsha','curl','-fsS','--max-time','10','http://127.0.0.1:'+str(c['gateway']['port'])+'/healthz'],capture_output=True)
out={'agents':results,'marsha':{'primary':c['agents']['defaults']['model']['primary'],'healthy':p.returncode==0},'rebootRequired':pathlib.Path('/var/run/reboot-required').exists(),'kernel':subprocess.check_output(['uname','-r'],text=True).strip()}
(root/'oauth-fleet-verified.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
assert all(all(r['checks'].values()) for r in results)
assert out['marsha']['primary']=='openai/gpt-6-astra' and out['marsha']['healthy']
