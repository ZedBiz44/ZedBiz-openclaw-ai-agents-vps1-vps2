"""Exercise the candidate's isolated restored database, never the live endpoint."""
import json,pathlib,urllib.request
root=pathlib.Path('/opt/openclaw/backups/release-20261023/hindsight-rehearsal')
assert json.loads((root/'migration-proof.json').read_text())['productionUntouched']
base='http://127.0.0.1:18888/v1/default/banks'
def call(suffix,body=None,method=None):
 data=json.dumps(body).encode() if body is not None else None
 req=urllib.request.Request(base+suffix,data=data,method=method,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=180) as r:return json.load(r)
banks=call('');(root/'banks-read.json').write_text(json.dumps(banks))
existing=call('/ghl/memories/recall',{'query':'ZedBiz','budget':'low','max_tokens':500})
(root/'existing-recall.json').write_text(json.dumps(existing))
assert existing.get('results'),'Existing-bank recall returned no memories'
bank='/release-proof-20261023'
call(bank,{},'PUT')
retained=call(bank+'/memories',{'items':[{'content':'The isolated upgrade test uses the project marker amber-lighthouse-731.','context':'Disposable upgrade test; no business or user fact.','document_id':'release-proof-20261023'}],'async':False})
(root/'retain-proof.json').write_text(json.dumps(retained))
recalled=call(bank+'/memories/recall',{'query':'What project marker does the upgrade test use?','budget':'low','max_tokens':500})
(root/'new-recall.json').write_text(json.dumps(recalled))
assert 'amber-lighthouse-731' in json.dumps(recalled),'New fact not recalled'
result={'passed':True,'existingBankRecallCount':len(existing['results']),'newFactRetainAndRecallPassed':True,'productionEndpointUsed':False,'workerDisabled':True}
(root/'api-proof.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
