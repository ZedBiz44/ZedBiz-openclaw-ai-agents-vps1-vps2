import json,pathlib,subprocess
w=pathlib.Path('/opt/openclaw/builds/2026.9.8-terry-20261003')
names=['amanda','edith','gohzed','grogar','inga','maggie','terry','victor','vivian','wilma']
result={'date':'2026-10-03','scope':'VPS1 only; Marsha remains Astra','agents':[]}
for n in names:
 proof=json.loads((w/(n+'-sol-summary.json')).read_text())
 c=json.loads(subprocess.check_output(['docker','exec',n,'cat','/home/node/.openclaw/openclaw.json']))
 item={'agent':n,'primary':c['agents']['defaults']['model']['primary'],'thinking':c['agents']['defaults'].get('thinkingDefault'),'fallbacks':c['agents']['defaults']['model'].get('fallbacks'),'proof':proof}
 if n!='terry':
  item['preservation']=json.loads((w/('fleet-'+n)/'verification.json').read_text())
  before=json.loads((pathlib.Path('/opt/openclaw/backups')/(n+'-20261003-pre-9.8')/'config-before.json').read_text())
  item['preservation']['checks']['authOrderPreserved']=before.get('auth',{}).get('order')==c.get('auth',{}).get('order')
  assert all(item['preservation']['checks'].values())
 assert proof['trace']['winnerModel']=='gpt-6.1-sol' and proof['trace']['fallbackUsed'] is False
 assert proof['tools']['failures']==0
 result['agents'].append(item)
result['health']=json.loads((w/'final-fleet-health.json').read_text())
assert all(a['dockerHealth']=='healthy' and a['httpHealthy'] for a in result['health']['agents'])
marsha=json.loads(subprocess.check_output(['docker','exec','marsha','cat','/home/node/.openclaw/openclaw.json']))
result['marsha']={'model':marsha['agents']['defaults']['model'],'thinking':marsha['agents']['defaults'].get('thinkingDefault')}
assert result['marsha']['model']['primary']=='openai/gpt-6-astra'
(w/'fleet-verification-summary.json').write_text(json.dumps(result,indent=2))
print('Verified evidence exported for ten Sol agents plus unchanged Marsha')
