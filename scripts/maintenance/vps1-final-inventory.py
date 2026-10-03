import subprocess,json,pathlib,concurrent.futures,os
b=pathlib.Path('/opt/openclaw/builds/vps1-complete-20261003')
names=['terry','amanda','edith','gohzed','grogar','inga','maggie','marsha','victor','vivian','wilma']
def audit(n):
 c=json.loads(subprocess.check_output(['docker','inspect',n]))[0]
 raw=subprocess.check_output(['docker','exec',n,'cat','/home/node/.openclaw/openclaw.json']);cfg=json.loads(raw)
 p=subprocess.run(['docker','exec',n,'openclaw','plugins','update','--all','--dry-run'],capture_output=True,text=True,timeout=180)
 (b/(n+'-plugins-final-dry-run.log')).write_text(p.stdout+p.stderr)
 j=json.loads(subprocess.check_output(['docker','exec',n,'openclaw','plugins','list','--json'],timeout=120))
 skills=subprocess.run(['docker','exec',n,'openclaw','skills','check','--agent','main','--json'],capture_output=True,text=True,timeout=90)
 (b/(n+'-skills-final.json')).write_text(skills.stdout)
 r={'agent':n,'healthy':c['State'].get('Health',{}).get('Status'),'image':c['Config']['Image'],'model':cfg['agents']['defaults']['model']['primary'],'authOrder':cfg['auth']['order']['openai'],'codexCommand':cfg['plugins']['entries']['codex']['config']['appServer']['command'],'pluginUpdateExit':p.returncode,'pendingUpdates':[line for line in p.stdout.splitlines() if 'Would update' in line or 'registry latest resolves' in line],'plugins':[{'id':x['id'],'version':x.get('version'),'status':x.get('status')} for x in j['plugins'] if x.get('origin')!='bundled'],'skillCheckExit':skills.returncode}
 print(json.dumps({'agent':n,'healthy':r['healthy'],'pendingUpdates':r['pendingUpdates'],'skillCheckExit':r['skillCheckExit']}),flush=True);return r
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:r=list(pool.map(audit,names))
(b/'fleet-final-inventory.json').write_text(json.dumps(r,indent=2))
