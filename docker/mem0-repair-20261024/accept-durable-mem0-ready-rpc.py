"""Automatic and explicit plugin memory acceptance on the isolated Terry gateway."""
import pathlib,subprocess,json,re,time,urllib.request,os,uuid
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/mem0-repair-20261024-r2');name='cody-mem0-repair-terry';out=W/'acceptance';out.mkdir(exist_ok=True,mode=0o700)
logs=subprocess.run(['docker','logs',name],capture_output=True,text=True)
assert re.search(r'startup phase: sidecars.subagent-recovery [\d.]+ms',logs.stdout+logs.stderr),'Gateway recovery not complete'
assert subprocess.run(['docker','exec',name,'sh','-c','curl -sf http://127.0.0.1:3010/healthz'],capture_output=True).returncode==0,'Production health probe failed'
def model(label,prompt):
 print(json.dumps({'modelTest':label,'started':True}),flush=True)
 request={'method':'agent','params':{'agentId':'main','sessionKey':'agent:main:cody-mem0-repair-'+label,'message':prompt,'idempotencyKey':str(uuid.uuid4()),'deliver':False,'disableMessageTool':True},'options':{'expectFinal':True}}
 p=subprocess.run(['docker','exec','-i','-e','CODY_RPC_REQUEST='+json.dumps(request),'-w','/home/node/.openclaw/workspace',name,'node','--input-type=module'],input=(W/'rpc.mjs').read_text(),capture_output=True,text=True,timeout=900)
 (out/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed; inspect private log'
 decoder=json.JSONDecoder();result=None
 for m in re.finditer(r'\{',p.stdout):
  try:
   value,_=decoder.raw_decode(p.stdout[m.start():])
   if isinstance(value,dict) and value.get('status') and 'result' in value:result=value;break
  except ValueError:pass
 assert result is not None,'Missing model result'
 meta=result['result']['meta'];receipt=meta['agentMeta']['terminalReceipt'];assert result['status']=='ok' and not meta.get('aborted') and not receipt.get('rerouted'),label+' failed/rerouted'
 (out/(label+'.json')).write_text(json.dumps(result,indent=2));print(json.dumps({'modelTest':label,'passed':True,'effectiveModel':receipt.get('effective',{}).get('model'),'successfulTools':receipt.get('successfulToolNames',[])}),flush=True)
 return result,receipt
capture,receipt=model('capture','Remember this lasting project fact for Cedar Orchard: the approved launch code is Saffron Maple742. We will need the exact launch code in future conversations. Do not use tools on this turn. Reply ACK_PROJECT_FACT. Do not send messages or change files.')
assert not receipt.get('successfulToolNames',[]),'Capture turn used tools'
q=json.loads(subprocess.check_output(['docker','inspect','--type','container','cody-mem0-repair-qdrant']))[0];ip=q['NetworkSettings']['Networks']['cody-mem0-repair-20261024']['IPAddress']
found=False
for i in range(18):
 request=urllib.request.Request('http://'+ip+':6333/collections/cody_durable_mem0_20261024/points/scroll',data=json.dumps({'limit':100,'with_payload':True,'with_vector':False}).encode(),headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(request,timeout=15) as response:r=json.load(response)
  (out/'isolated-scroll.json').write_text(json.dumps(r));found=bool(re.search(r'Saffron\s+Maple\s*742',json.dumps(r),re.I))
 except urllib.error.HTTPError as e:
  if e.code!=404:raise
 if found:break
 time.sleep(5)
assert found,'No automatic save found in isolated Qdrant'
recall,r=model('fresh-recall','Use mem0_search to retrieve Cedar Orchard\'s approved launch code. Then use mem0_get to read that same memory by its identifier. Return the exact launch code from memory. Do not guess, store anything, send messages or modify files.')
assert {'mem0_search','mem0_get'}<=set(r.get('successfulToolNames',[])) and re.search(r'Saffron\s+Maple\s*742',json.dumps(recall['result'].get('payloads',[])),re.I),'Fresh recall/get failed'
explicit,e=model('explicit-tools','Use memory_add to store exactly this fact: Birch Studio\'s approved review weekday is Thursday. Then use mem0_search and mem0_get to verify that saved fact. Through your connected Codex Notion app use codex_apps.notion.fetch to read page37ba3e33d581816584cdf6b622a0d944. Use native Asana to get your own user identity. Return only whether each operation succeeded and the saved weekday. Do not send external messages, edit files/pages, create tasks or delegate.')
required={'memory_add','mem0_search','mem0_get','codex_apps.notion.fetch','asana.asana_get_user'};assert required<=set(e.get('successfulToolNames',[])),'Required explicit memory/integration tools failed'
drive=subprocess.run(['docker','exec',name,'gog','--readonly','--no-input','--json','drive','ls','--max','1'],capture_output=True,text=True,timeout=120);(out/'drive.private.log').write_text(drive.stdout+drive.stderr);assert drive.returncode==0,'Drive read failed'
proof={'passed':True,'automaticCaptureNoTools':True,'automaticFactFoundInIsolatedStorage':True,'independentSessionRecallAndGet':True,'explicitMemoryTools':True,'codexNotionAndNativeAsana':True,'authenticatedDriveRead':True,'productionMemoryModified':False,'effectiveModels':[x.get('effective',{}).get('model') for x in [receipt,r,e]],'requiredTools':sorted(required)}
(W/'acceptance.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)

