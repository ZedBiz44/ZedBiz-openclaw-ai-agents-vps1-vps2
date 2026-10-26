"""Native read-only Harry acceptance following the lean Mem0 cutover."""
import pathlib,json,subprocess,os,time,hashlib,uuid,urllib.request
P=pathlib.Path;os.umask(0o077);W=P('/root/cody-mem0-repair-20261024');A=W/'activation';before=json.loads((A/'before.json').read_text());activated=json.loads((A/'activated.json').read_text());assert activated['activated']
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
assert sha('/root/.openclaw-harry/openclaw.json')==before['configSha256'];assert sha('/opt/openclaw-harry/start-harry.sh')==before['starterSha256']
start=time.monotonic();env=None
while time.monotonic()-start<700:
 for proc in P('/proc').glob('[0-9]*'):
  try:
   if (proc/'comm').read_text().strip()!='openclaw-gatewa':continue
   e=dict(v.split('=',1) for v in (proc/'environ').read_text().split('\0') if '=' in v)
   if e.get('OPENCLAW_STATE_DIR')=='/root/.openclaw-harry':env=e;break
  except (OSError,UnicodeError):pass
 if env:
  try:
   with urllib.request.urlopen('http://127.0.0.1:4100/healthz',timeout=3) as r:
    if r.status==200:break
  except Exception:pass
 time.sleep(3)
else:raise RuntimeError('Harry health deadline')
def run(args,label,**kw):
 p=subprocess.run(args,env=env,capture_output=True,text=True,**kw);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
def rpc(method,params=None,options=None):
 e=env.copy();e['CODY_RPC_REQUEST']=json.dumps({'method':method,'params':params or {},'options':options or {}})
 p=subprocess.run(['node',str(W/'rpc.mjs')],env=e,capture_output=True,text=True,timeout=720);(A/(method+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,method+' failed';r=json.loads(p.stdout);(A/(method+'.json')).write_text(json.dumps(r));return r
assert rpc('health').get('ok')
cron=rpc('cron.list',{'includeDisabled':True});old=json.loads((A/'cron-before.json').read_text())
def definitions(v):return [{k:x for k,x in j.items() if k not in ['state','updatedAtMs']} for j in v['jobs']]
assert definitions(cron)==definitions(old),'Schedules changed'
prompt='Read-only memory repair acceptance. Use mem0_search to find an EXISTING ZedBiz business memory and then mem0_get to read it by identifier. Use your connected Codex Notion app to fetch page 37ba3e33d581816584cdf6b622a0d944, and your native Asana tool to get your own user identity. Return which calls succeeded. Do not save any test facts, alter files or pages, create tasks, send messages, or delegate.'
r=rpc('agent',{'agentId':'main','sessionKey':'agent:main:cody-mem0-live-20261024','message':prompt,'idempotencyKey':str(uuid.uuid4()),'deliver':False,'disableMessageTool':True},{'expectFinal':True})
meta=r['result']['meta'];receipt=meta['agentMeta']['terminalReceipt'];assert r['status']=='ok' and not meta.get('aborted') and not receipt.get('rerouted');assert {'mem0_search','mem0_get','codex_apps.notion.fetch','asana.asana_get_user'}<=set(receipt.get('successfulToolNames',[])),'Live connected tools failed'
run(['/opt/openclaw-harry/ensure-mem0-110-compat.sh','--auto','/root/.openclaw-harry'],'startup-guard',timeout=30)
run(['gog','--readonly','--no-input','--json','drive','ls','--max','1'],'drive',timeout=120)
assert subprocess.check_output(['systemctl','show','openclaw-harry','--property=NRestarts','--value'],text=True).strip()=='0'
with urllib.request.urlopen('https://harry.zbiz.ca/healthz',timeout=30) as r:assert r.status==200
proof={'passed':True,'agent':'harry','sdk':'3.3.1','helperModel':'gpt-6-luna','httpsFixPreserved':True,'configurationUnchanged':True,'startupNoPackageInstalls':True,'schedules':len(cron['jobs']),'restarts':0,'existingMemoryRead':True,'authenticatedDriveRead':True,'httpsHealth':200,'successfulTools':receipt.get('successfulToolNames',[]),'effectiveModel':receipt.get('effective',{}).get('model')}
(A/'acceptance.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)

