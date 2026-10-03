import subprocess,pathlib,json,hashlib,concurrent.futures
b=pathlib.Path('/opt/openclaw/builds/vps1-email-20261003');out=b/'public';out.mkdir(exist_ok=True)
names=['terry','amanda','edith','gohzed','grogar','inga','maggie','marsha','victor','vivian','wilma']
def audit(n):
 c=json.loads(subprocess.check_output(['docker','inspect',n]))[0];cfg=json.loads(subprocess.check_output(['docker','exec',n,'cat','/home/node/.openclaw/openclaw.json']));env=dict(x.split('=',1) for x in c['Config']['Env'])
 skill=subprocess.check_output(['docker','exec',n,'cat','/home/node/.openclaw/workspace/skills/himalaya/SKILL.md'])
 info=json.loads(subprocess.check_output(['docker','exec',n,'openclaw','skills','info','himalaya','--agent','main','--json'],timeout=60))
 version=subprocess.check_output(['docker','exec',n,'himalaya','--version'],text=True).splitlines()[0]
 p=subprocess.run(['docker','exec',n,'curl','-fsS','--max-time','5','http://127.0.0.1:'+str(cfg['gateway']['port'])+'/healthz'],capture_output=True)
 test=json.loads((b/n/'verification-live.json').read_text());proof=json.loads((b/n/'live-agent-proof-summary.json').read_text());proof.pop('reply',None)
 r={'agent':n,'version':version,'dockerHealth':c['State'].get('Health',{}).get('Status'),'gatewayHealthy':p.returncode==0,'image':c['Config']['Image'],'model':cfg['agents']['defaults']['model']['primary'],'authOrder':cfg['auth']['order']['openai'],'codexCommand':cfg['plugins']['entries']['codex']['config']['appServer']['command'],'apiKeysCleared':all(k in cfg['plugins']['entries']['codex']['config']['appServer']['clearEnv'] for k in ['OPENAI_API_KEY','CODEX_API_KEY','OPENAI_AUTH_TOKEN']),'emailCredentialsResolved':all(env.get(k) and not env[k].startswith(('op://','${')) for k in ['EMAIL_ADDRESS','EMAIL_PASSWORD']),'skillSha256':hashlib.sha256(skill).hexdigest(),'skillEligible':info.get('eligible'),'skillModelVisible':info.get('modelVisible'),'skillPath':info.get('filePath'),'emailTests':test,'agentProof':proof}
 assert r['gatewayHealthy'] and r['emailCredentialsResolved'] and r['apiKeysCleared'] and r['skillEligible'] and r['skillModelVisible'] and r['skillSha256']==hashlib.sha256((b/'himalaya/SKILL.md').read_bytes()).hexdigest()
 assert r['model']=='openai/'+('gpt-6-astra' if n=='marsha' else 'gpt-6.1-sol')+'@openai:jzedbiz@gmail.com' and r['authOrder']==['openai:jzedbiz@gmail.com']
 return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:r=list(pool.map(audit,names))
(out/'fleet-email-verification.json').write_text(json.dumps(r,indent=2))
for name in ['binary-provenance.json','mem0-client-review.json','staging.json']:(out/name).write_bytes((b/name).read_bytes())
host={'rebootRequired':pathlib.Path('/var/run/reboot-required').exists(),'failedServices':subprocess.check_output(['systemctl','--failed','--no-legend'],text=True),'hostHimalaya':subprocess.check_output(['/usr/local/bin/himalaya','--version'],text=True).splitlines()[0]};(out/'host.json').write_text(json.dumps(host,indent=2))
print(json.dumps({'agents':len(r),'allEmailTestsPassed':all(a['emailTests']['imapAuth'] and a['emailTests']['smtpAuth'] and a['emailTests']['draftCompose'] for a in r),'allDockerHealthy':all(a['dockerHealth']=='healthy' for a in r),'host':host}))
