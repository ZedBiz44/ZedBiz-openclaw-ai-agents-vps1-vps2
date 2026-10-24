"""Real model/tool and automatic-memory acceptance; synthetic writes stay isolated."""
import pathlib,subprocess,json,sys,time,re,os
P=pathlib.Path;os.umask(0o077);w=P('/opt/openclaw/backups/host-20261024');mode=sys.argv[1];assert mode in ['rehearsal','live'];name='cody-marsha-10-6-rehearsal' if mode=='rehearsal' else 'terry'
out=w/('acceptance-terry-'+mode);out.mkdir(mode=0o700,exist_ok=True)
def reset(label):
 assert mode=='rehearsal'
 p=subprocess.run(['python3',str(w/'rpc-run.py'),name,label,json.dumps([['sessions.reset',{'key':'agent:main:main','reason':'new'}]])],capture_output=True,text=True)
 (out/(label+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,'Fixture session reset failed'
def model(label,prompt):
 p=subprocess.run(['docker','exec','-w','/home/node/.openclaw/workspace',name,'node','/app/openclaw.mjs','agent','--agent','main','--session-key','agent:main:main','--message',prompt,'--json'],capture_output=True,text=True,timeout=1200)
 text=p.stdout+p.stderr;(out/(label+'.log')).write_text(text);assert p.returncode==0,label+' command failed; inspect private log'
 decoder=json.JSONDecoder();r=None
 for m in re.finditer(r'\{',p.stdout):
  try:
   value,_=decoder.raw_decode(p.stdout[m.start():])
   if isinstance(value,dict) and value.get('status') and 'result' in value:r=value;break
  except ValueError:pass
 assert r is not None,'No model result JSON'
 (out/(label+'.json')).write_text(json.dumps(r,indent=2));meta=r['result']['meta'];receipt=meta['agentMeta']['terminalReceipt']
 assert r['status']=='ok' and not meta.get('aborted') and not receipt.get('rerouted'),'Model failed or rerouted'
 return r,receipt
if mode=='rehearsal':reset('fresh-tools')
prompt='Read-only upgrade acceptance. Through your Codex connection, use Notion fetch to read page37ba3e33d581816584cdf6b622a0d944. Use native Asana to get your own user identity. Use mem0_search to query for existing ZedBiz context; an empty test bank is acceptable. Return the tool names and whether each succeeded. Do not send messages, change files/pages, create tasks, explicitly store memories or delegate.'
r,receipt=model('tools',prompt)
required={'codex_apps.notion.fetch','asana.asana_get_user','mem0_search'}
assert required<=set(receipt.get('successfulToolNames',[])),'Required integrations were not all successful'
drive=subprocess.run(['docker','exec',name,'gog','--readonly','--no-input','--json','drive','ls','--max','1'],capture_output=True,text=True,timeout=120);(out/'drive.log').write_text(drive.stdout+drive.stderr);assert drive.returncode==0,'Authenticated Drive read failed'
proof={'passed':True,'mode':mode,'receipt':receipt,'driveAuthenticatedRead':True,'requiredTools':sorted(required)}
(w/('model-proof.json' if mode=='rehearsal' else 'terry-live-model-proof.json')).write_text(json.dumps(proof,indent=2));print(json.dumps({'modelAndToolsPassed':True,'mode':mode,'receipt':receipt}),flush=True)
if mode=='live':sys.exit()
reset('fresh-capture')
r,capture=model('capture','Remember this durable fact for a fictional training client: Aurora Orchard has approved the campaign code Saffron Maple742. This is the lasting campaign code for future training conversations. This is isolated upgrade acceptance data, not a real customer. Do not use any tools on this turn. Reply exactly ACK_TEST_FACT.')
assert not capture.get('successfulToolNames',[]),'Capture turn used tools; cannot attribute storage to the automatic hook'
query='Aurora Orchard approved campaign code';bank='cody-marsha-isolated-20261024'
code='''import urllib.request,json
req=urllib.request.Request('http://127.0.0.1:8888/v1/default/banks/'''+bank+'''/memories/recall',data=json.dumps({'query':''' +repr(query)+''','budget':'low','max_tokens':1024}).encode(),headers={'Content-Type':'application/json'})
try:
 with urllib.request.urlopen(req,timeout=30) as r:print(json.dumps(json.load(r)))
except Exception as e:print(json.dumps({'errorType':type(e).__name__,'status':getattr(e,'code',None)}))
'''
found=False
for i in range(36):
 p=subprocess.run(['docker','exec','-i','cody-marsha-hindsight-1-0','python','-'],input=code,capture_output=True,text=True,timeout=45);(out/'backend-recall-latest.json').write_text(p.stdout+p.stderr)
 if re.search(r'Saffron\s+Maple\s*742',p.stdout,re.I):found=True;break
 time.sleep(5)
assert found,'Automatic capture was not found in isolated backend'
reset('fresh-recall')
r,recall=model('fresh-recall','Use mem0_search to retrieve the approved campaign code for the fictional training client Aurora Orchard. Return the exact code from memory. Do not guess, store another memory, send messages or delegate.')
assert 'mem0_search' in recall.get('successfulToolNames',[]) and re.search(r'Saffron\s+Maple\s*742',json.dumps(r['result'].get('payloads',[])),re.I),'Independent fresh-session recall failed'
proof={'passed':True,'automaticCaptureTurnUsedNoTools':True,'backendRecallFoundFact':True,'freshSessionRecallPassed':True,'bank':bank,'productionBackendVersionTested':'1.0','pluginVersion':'1.2.0','captureReceipt':capture,'recallReceipt':recall,'productionMemoryModified':False}
(w/'memory-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps({'automaticCaptureAndFreshRecallPassed':True,'productionMemoryModified':False}),flush=True)

