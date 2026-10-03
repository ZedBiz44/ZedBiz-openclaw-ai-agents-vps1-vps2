import pathlib,json,subprocess,sys
n=sys.argv[1];w=pathlib.Path('/opt/openclaw/builds/2026.9.8-terry-20261003')/('fleet-'+n)
b=pathlib.Path('/opt/openclaw/backups')/(n+'-20261003-pre-9.8')
old=json.loads((b/'config-before.json').read_text())
def run(*args):
 p=subprocess.run(['docker','exec',n,'openclaw',*args],capture_output=True,text=True,timeout=180)
 if p.returncode:raise RuntimeError('OpenClaw check failed: '+str(args))
 return json.loads(p.stdout)
new=json.loads(subprocess.check_output(['docker','exec',n,'cat','/home/node/.openclaw/openclaw.json']))
jobs=run('cron','list','--json');(w/'cron-after.json').write_text(json.dumps(jobs,indent=2))
def normalized(j):
 return sorted([{k:x.get(k) for k in ['id','name','enabled','schedule']} for x in j.get('jobs',[])],key=lambda x:x['id'])
checks={'cronPreserved':normalized(json.loads((w/'cron-before.json').read_text()))==normalized(jobs),'fallbacksPreserved':old['agents']['defaults']['model'].get('fallbacks')==new['agents']['defaults']['model'].get('fallbacks'),'thinkingPreserved':old['agents']['defaults'].get('thinkingDefault')==new['agents']['defaults'].get('thinkingDefault'),'memorySlotPreserved':old.get('plugins',{}).get('slots')==new.get('plugins',{}).get('slots'),'skillSettingsPreserved':old.get('skills')==new.get('skills')}
skills=run('skills','check','--agent','main','--json');(w/'skills-after.json').write_text(json.dumps(skills,indent=2))
plugins=run('plugins','list','--json');(w/'plugins-after.json').write_text(json.dumps(plugins,indent=2))
result={'agent':n,'checks':checks,'skills':skills.get('summary'),'plugins':[{k:x.get(k) for k in ['id','version','status','error']} for x in plugins.get('plugins',[]) if x.get('origin')!='bundled']}
(w/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if not all(checks.values()):raise SystemExit(2)
