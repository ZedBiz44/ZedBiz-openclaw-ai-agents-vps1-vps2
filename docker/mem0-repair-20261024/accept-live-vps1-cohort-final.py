"""Read-only production acceptance after each managed cohort activation."""
import pathlib,json,subprocess,time,re,urllib.request,uuid,os,sys,hashlib
P=pathlib.Path;os.umask(0o077);name=sys.argv[1];A=P('/opt/openclaw/backups/fleet-10-6-20261024')/name
M=P('/opt/openclaw/backups/mem0-repair-20261024-r2');out=A/'live-acceptance';out.mkdir(exist_ok=True,mode=0o700)
activation=json.loads((A/'activation.json').read_text());preserved=json.loads((A/'preservation.json').read_text());assert activation['activated']
def run(args,label,**kw):
 p=subprocess.run(args,capture_output=True,text=True,**kw);(out/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
def obj(n):return json.loads(subprocess.check_output(['docker','inspect','--type','container',n]))[0]
start=time.monotonic();last=0
while time.monotonic()-start<1000:
 d=obj(name);assert d['State']['Running'] and not d['State']['OOMKilled'] and d['RestartCount']==0,'Live gateway failed/restarted'
 p=subprocess.run(['docker','logs',name],capture_output=True,text=True);log=p.stdout+p.stderr
 if d['State'].get('Health',{}).get('Status')=='healthy' and re.search(r'startup phase: sidecars.subagent-recovery [\d.]+ms',log):break
 if time.monotonic()-start-last>40:print(json.dumps({'agent':name,'waitingForReady':True,'elapsed':round(time.monotonic()-start),'health':d['State'].get('Health',{}).get('Status')}),flush=True);last=time.monotonic()-start
 time.sleep(3)
else:raise RuntimeError('Live readiness deadline')
assert d['Image']==activation['targetId'] and obj(name+'-asana-mcp')['Image']==activation['sidecarId']
assert '2026.10.6' in run(['docker','exec',name,'node','-p','require("/app/package.json").version'],'version',timeout=30)
assert run(['docker','exec',name,'node','--version'],'node',timeout=30).strip()=='v24.22.1'
run(['docker','exec',name,'node','/home/node/.openclaw/scripts/verify-runtime-10-6.cjs',name],'runtime-guard',timeout=30)
slot=preserved['memorySlot'];required={'codex_apps.notion.fetch','asana.asana_get_user'}
if slot=='openclaw-mem0':required|={'mem0_search','mem0_get'};memory='Use mem0_search to find an EXISTING business memory, then mem0_get to read it by identifier.'
elif slot=='memory-lancedb':required.add('memory_recall');memory='Use memory_recall to read existing business memories.'
elif slot=='hindsight-openclaw':required.add('hindsight_recall');memory='Use hindsight_recall to read existing business memories using your normal configured identity and bank.'
else:raise RuntimeError('Unexpected memory provider')
def rpc(method,params=None,options=None):
 req={'method':method,'params':params or {},'options':options or {}}
 text=run(['docker','exec','-i','-e','CODY_RPC_REQUEST='+json.dumps(req),name,'node','--input-type=module'],method,input=(M/'rpc.mjs').read_text(),timeout=720);r=json.loads(text);(out/(method+'.json')).write_text(json.dumps(r));return r
assert rpc('health').get('ok')
cron=rpc('cron.list',{'includeDisabled':True});assert len(cron['jobs'])==preserved['userSchedulesPreserved'],'Schedule count changed'
prompt='Read-only upgrade acceptance. '+memory+' Through your connected Codex Notion app use codex_apps.notion.fetch to read page 37ba3e33d581816584cdf6b622a0d944. Use native Asana to get your own user identity. Return only which calls succeeded. Do not save test facts, change files or pages, create tasks, send messages, or delegate.'
sessionKey='agent:main:main' if slot=='hindsight-openclaw' else 'agent:main:cody-upgrade-live-20261024'
idleStart=time.monotonic()
while True:
 active=rpc('status').get('shutdownBudget',{}).get('activeWork');assert active,'Missing active-work counters'
 if all(v==0 for v in active.values()):break
 assert time.monotonic()-idleStart<1200,'Busy agent; defer the maintenance test';time.sleep(15)
r=rpc('agent',{'agentId':'main','sessionKey':sessionKey,'message':prompt,'idempotencyKey':str(uuid.uuid4()),'deliver':False,'disableMessageTool':True},{'expectFinal':True})
meta=r['result']['meta'];receipt=meta['agentMeta']['terminalReceipt'];assert r['status']=='ok' and not meta.get('aborted') and not receipt.get('rerouted') and required<=set(receipt.get('successfulToolNames',[])),'Live model/tool proof failed'
run(['docker','exec',name,'gog','--readonly','--no-input','--json','drive','ls','--max','1'],'drive',timeout=120)
with urllib.request.urlopen('https://'+name+'.zbiz.ca/healthz',timeout=25) as response:assert response.status==200
phases=[{'phase':m[1],'ms':float(m[2]),'totalMs':float(m[3])} for m in re.finditer(r'startup phase: (\S+) ([\d.]+)ms total=([\d.]+)ms',log)]
proof={'passed':True,'agent':name,'imageId':d['Image'],'core':'2026.10.6','node':'24.22.1','schedules':len(cron['jobs']),'memoryProvider':slot,'restarts':d['RestartCount'],'oom':d['State']['OOMKilled'],'httpsHealth':200,'effectiveModel':receipt.get('effective',{}).get('model'),'successfulTools':receipt.get('successfulToolNames',[]),'existingMemoryRead':True,'authenticatedDriveRead':True,'startupPhases':phases}
(A/'acceptance.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
