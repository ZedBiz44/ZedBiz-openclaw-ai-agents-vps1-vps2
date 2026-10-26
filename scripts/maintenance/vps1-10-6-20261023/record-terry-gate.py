"""Record the tested gateway path separately from unresolved cold CLI diagnostics."""
import json,pathlib
w=pathlib.Path('/opt/openclaw/backups/release-20261023/terry')
s=(w/'gateway-rehearsal-model.log').read_text();r=json.loads(s[s.index('{'):])
receipt=r['result']['meta']['agentMeta']['terminalReceipt']
assert r['status']=='ok' and not r['result']['meta']['aborted']
assert receipt['effective']['model']=='gpt-6.1-sol' and not receipt['rerouted']
assert {'mem0_search','asana.asana_get_user'}<=set(receipt['successfulToolNames'])
assert json.loads((w/'gateway-rehearsal-probe-receipt.json').read_text())['exit']==0
assert (w/'gateway-rehearsal-config-before.json').read_bytes()==(w/'rehearsal/config/openclaw.json').read_bytes()
assert json.loads((w/'mem0-extraction-proof.json').read_text())['passed']
result={'passed':True,'scope':'Terry core gateway pilot, with guarded memory-model repair','gatewayModelReceipt':receipt,'isolatedMemoryExtractionAndRecallPassed':True,'knownUnresolved':['Cold local CLI plugin publication exceeds its startup budget','Slow plugin startup can delay startup orphan scan'],'widerFleetAccepted':False}
(w/'readiness-gate.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'passed':True,'scope':result['scope'],'unresolved':result['knownUnresolved']}))
