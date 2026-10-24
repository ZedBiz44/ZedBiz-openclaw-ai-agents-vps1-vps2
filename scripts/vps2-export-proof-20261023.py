import json
from pathlib import Path
B=Path('/root/cody-vps2-followup-20261023')
r=json.loads((B/'final-audit.json').read_text())
assert r['bootId']!= (B/'boot-id-before').read_text().strip()
r['prebootId']=(B/'boot-id-before').read_text().strip()
r['acceptance']={}
for n in ['frank','harry','suzy']:
 d=json.loads((B/(n+'-accepted.json')).read_text());before=json.loads((B/(n+'-preboot-accepted.json')).read_text())
 assert d['accepted'] and d['receipt']['runId']!=before['receipt']['runId']
 t=d['receipt'];r['acceptance'][n]={'accepted':True,'runId':t['runId'],'effective':t['effective'],'rerouted':t['rerouted'],'successfulToolNames':t['successfulToolNames']}
r['cleanup']=[json.loads((B/x).read_text()) for x in ['cleanup-temporary.json','cleanup-extracted.json','cleanup-followup.json']]
r['archives']=json.loads(Path('/root/zedbiz-maintenance-archives/2026-10-23/manifest.json').read_text())
(B/'public-verification.json').write_text(json.dumps(r,indent=2))
print('Verified postboot evidence exported')
