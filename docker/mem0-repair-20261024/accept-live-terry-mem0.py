"""Verify actual Terry after the backed-up package-only Mem0 cutover."""
import pathlib,json,subprocess,time,re,urllib.request,hashlib,uuid,os,tarfile
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/mem0-repair-20261024-r2');A=W/'terry-activation';name='terry';out=A/'live-acceptance';out.mkdir(exist_ok=True,mode=0o700)
before=json.loads((A/'before.json').read_text());assert json.loads((A/'activated.json').read_text())['activated']
def run(args,label,**kw):
 p=subprocess.run(args,capture_output=True,text=True,**kw);(out/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
def obj():return json.loads(subprocess.check_output(['docker','inspect','--type','container',name]))[0]
start=time.monotonic();last=0
while time.monotonic()-start<1000:
 d=obj();assert d['State']['Running'] and not d['State']['OOMKilled'] and d['RestartCount']==0,'Live gateway failed/restarted'
 p=subprocess.run(['docker','logs',name],capture_output=True,text=True);log=p.stdout+p.stderr
 if d['State'].get('Health',{}).get('Status')=='healthy' and re.search(r'startup phase: sidecars.subagent-recovery [\d.]+ms',log):break
 if time.monotonic()-start-last>40:print(json.dumps({'waitingForLiveTerryReady':True,'elapsed':round(time.monotonic()-start),'health':d['State'].get('Health',{}).get('Status')}),flush=True);last=time.monotonic()-start
 time.sleep(3)
else:raise RuntimeError('Live readiness deadline')
assert d['Image']==before['image'] and '[mem0-sdk]' in log and '[mem0-compat]' in log
project=json.loads((W/'clone-project.json').read_text())['projectName'];run(['docker','exec',name,'node','/home/node/.openclaw/scripts/verify-mem0-sdk331.cjs','/home/node/.openclaw/npm/projects/'+project],'sdk-guard')
with tarfile.open(A/'state-before.tar.gz','r|gz') as archive:
 for item in archive:
  if item.name.removeprefix('./')=='config/openclaw.json':configBefore=json.load(archive.extractfile(item));break
 else:raise RuntimeError('Checkpoint config missing')
assert json.loads(P('/opt/openclaw/agents/terry/config/openclaw.json').read_text())==configBefore,'Protected config changed'
assert hashlib.sha256(P('/opt/openclaw/agents/terry/workspace/post-start.sh').read_bytes()).hexdigest()==before['postStartSha256']
def rpc(method,params=None,options=None):
 req={'method':method,'params':params or {},'options':options or {}}
 text=run(['docker','exec','-i','-e','CODY_RPC_REQUEST='+json.dumps(req),name,'node','--input-type=module'],method,input=(W/'rpc.mjs').read_text(),timeout=720);r=json.loads(text);(out/(method+'.json')).write_text(json.dumps(r));return r
health=rpc('health');assert health.get('ok')
cron=rpc('cron.list',{'includeDisabled':True})
def definitions(value):return [{k:v for k,v in j.items() if k not in ['state','updatedAtMs']} for j in value['jobs']]
assert definitions(cron)==definitions(before['cron']),'Schedules changed'
prompt='Read-only Mem0 repair acceptance. Use mem0_search to recall one EXISTING ZedBiz business memory, then mem0_get to read that memory by identifier. Through the connected Codex Notion app use codex_apps.notion.fetch to read page37ba3e33d581816584cdf6b622a0d944. Use native Asana to get your own user identity. Return only which calls succeeded. Do not store test facts, use memory_add, alter files/pages, create tasks, send messages or delegate.'
r=rpc('agent',{'agentId':'main','sessionKey':'agent:main:cody-mem0-live-20261024','message':prompt,'idempotencyKey':str(uuid.uuid4()),'deliver':False,'disableMessageTool':True},{'expectFinal':True})
meta=r['result']['meta'];receipt=meta['agentMeta']['terminalReceipt'];required={'mem0_search','mem0_get','codex_apps.notion.fetch','asana.asana_get_user'}
assert r['status']=='ok' and not meta.get('aborted') and not receipt.get('rerouted') and required<=set(receipt.get('successfulToolNames',[])),'Live model/tool proof failed'
run(['docker','exec',name,'gog','--readonly','--no-input','--json','drive','ls','--max','1'],'drive',timeout=120)
with urllib.request.urlopen('https://terry.zbiz.ca/healthz',timeout=25) as response:assert response.status==200
phases=[{'phase':m[1],'ms':float(m[2]),'totalMs':float(m[3])} for m in re.finditer(r'startup phase: (\S+) ([\d.]+)ms total=([\d.]+)ms',log)]
proof={'passed':True,'imageUnchanged':True,'configurationAndPostStartUnchanged':True,'schedulesUnchanged':len(cron['jobs']),'newSdk':'3.3.1','restarts':d['RestartCount'],'oom':d['State']['OOMKilled'],'httpsHealth':200,'effectiveModel':receipt.get('effective',{}).get('model'),'successfulTools':receipt.get('successfulToolNames',[]),'existingProductionMemoryRead':True,'authenticatedDriveRead':True,'isolatedAutomaticAndExplicitSaveAlreadyPassed':True,'startupPhases':phases}
(A/'acceptance.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)

