"""Run the actual Hindsight plugin with copied Marsha state against an empty 1.1 fixture."""
import pathlib,subprocess,json,os,sqlite3,time,re,sys,urllib.request
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/shared-updates-20261026');A=W/'marsha-pilot';live=P('/opt/openclaw/agents/marsha');stage=A/'profile';name='cody-shared-marsha-20261026';bank='cody-shared-20261026';api='cody-shared-20261026-api';action=sys.argv[1]
def inspect(n):return json.loads(subprocess.check_output(['docker','inspect',n]))[0]
def run(args,label,timeout=900,input=None):
 p=subprocess.run(args,input=input,capture_output=True,text=True,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
if action=='start':
 fixture=json.loads((W/'hindsight-empty-test/fixture.json').read_text());assert fixture['ready'] and fixture['workerEnabled'];A.mkdir(mode=0o700);d=inspect('marsha');assert d['State']['Health']['Status']=='healthy';(A/'runtime.env').write_text('\n'.join(d['Config']['Env'])+'\n');run(['cp','-a',str(live),str(stage)],'copy-state')
 for src in [live/'config/state/openclaw.sqlite',*(live/'agents').glob('*/agent/openclaw-agent.sqlite')]:
  dst=stage/src.relative_to(live)
  for p in [dst,P(str(dst)+'-wal'),P(str(dst)+'-shm')]:
   if p.exists():p.unlink()
  with sqlite3.connect('file:'+str(src)+'?mode=ro',uri=True) as old,sqlite3.connect(dst) as new:old.backup(new);new.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True);assert new.execute('pragma quick_check').fetchall()==[('ok',)]
  s=src.stat();os.chown(dst,s.st_uid,s.st_gid)
 cfg=stage/'config/openclaw.json';c=json.loads(cfg.read_text());c.setdefault('cron',{})['enabled']=False;c.setdefault('hooks',{})['enabled']=False;c['hooks'].setdefault('internal',{})['enabled']=False;c['agents']['defaults'].setdefault('heartbeat',{})['every']='0m'
 for agent in c['agents'].get('list',[]):agent.setdefault('heartbeat',{})['every']='0m'
 m=c['plugins']['entries']['hindsight-openclaw']['config'];m.update(hindsightApiUrl='http://'+api+':8888',bankId=bank,autoRetain=True);m['allowKnowledgeDelete']=False;cfg.write_text(json.dumps(c,indent=2)+'\n');os.chown(cfg,1000,1000)
 with sqlite3.connect(stage/'config/state/openclaw.sqlite') as db:db.execute('delete from agent_database_leases');db.execute("delete from state_leases where scope='gateway-owner' and lease_key='global'")
 wiki=A/'wiki';run(['cp','-a','/opt/openclaw/shared/knowledge/wiki',str(wiki)],'copy-wiki');args=['docker','run','-d','--name',name,'--label','cody.shared-update-fixture=true','--network','openclaw','--network',fixture['network'],'--memory','3g','--memory-swap','3g','--env-file',str(A/'runtime.env'),'--user','node','--entrypoint','node']
 for k in ['OPENCLAW_SKIP_CHANNELS','OPENCLAW_SKIP_CRON','OPENCLAW_SKIP_GMAIL_WATCHER','OPENCLAW_DISABLE_BONJOUR']:args+=['-e',k+'=1']
 for mount in d['Mounts']:
  src=mount['Source'];dst=mount['Destination']
  if src in ['/var/run/docker.sock','/dev/shm']:continue
  if src.startswith(str(live)+'/'):src=str(stage/src[len(str(live))+1:]);suffix='' if mount['RW'] else ':ro'
  else:suffix=':ro'
  args+=['-v',src+':'+dst+suffix]
 args+=['-v',str(wiki)+':/opt/openclaw/shared/knowledge/wiki',d['Image'],'/app/openclaw.mjs','gateway','run','--port',str(c['gateway']['port']),'--bind','loopback'];run(args,'start-gateway');start=time.monotonic()
 while True:
  gateway=inspect(name);p=subprocess.run(['docker','logs',name],capture_output=True,text=True);log=p.stdout+p.stderr;(A/'gateway.private.log').write_text(log)
  assert gateway['State']['Running'] and not gateway['State']['OOMKilled'],'Pilot exited'
  if 'startup phase: sidecars.subagent-recovery' in log:break
  assert time.monotonic()-start<600,'Pilot startup deadline';time.sleep(4)
 proof={'ready':True,'gateway':name,'backendVersion':'1.1.0','imageId':d['Image'],'productionGatewayUnchanged':inspect('marsha')['Id']==d['Id'],'productionMemoryUntouched':True};(A/'ready.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
elif action=='accept':
 assert json.loads((A/'ready.json').read_text())['ready'];rpc=P('/opt/openclaw/backups/mem0-repair-20261024-r2/rpc.mjs').read_text()
 def reset(label):run(['docker','exec','-i','-e','CODY_RPC_REQUEST='+json.dumps({'method':'sessions.reset','params':{'key':'agent:main:main','reason':'new'}}),name,'node','--input-type=module'],label,120,input=rpc)
 def turn(label,prompt):
  text=run(['docker','exec','-w','/home/node/.openclaw/workspace',name,'node','/app/openclaw.mjs','agent','--agent','main','--session-key','agent:main:main','--message',prompt,'--json'],label,900);decoder=json.JSONDecoder();result=None
  for match in re.finditer(r'\{',text):
   try:
    v,_=decoder.raw_decode(text[match.start():])
    if isinstance(v,dict) and v.get('status') and 'result' in v:result=v;break
   except ValueError:pass
  assert result and result['status']=='ok';meta=result['result']['meta'];receipt=meta['agentMeta']['terminalReceipt'];assert not meta.get('aborted') and not receipt.get('rerouted');(A/(label+'.private.json')).write_text(json.dumps(result));return result,receipt
 reset('reset-capture');result,capture=turn('automatic-capture','Remember this durable fact for a fictional training client: Aurora Orchard approved campaign code Copper Aspen826. This is the lasting campaign code for future training conversations. This is isolated upgrade acceptance data, not a real customer. Do not use any tools on this turn. Reply exactly ACK_TEST_FACT.');assert not capture.get('successfulToolNames',[]),'Capture attribution requires no explicit memory tool'
 found=False
 for attempt in range(48):
  req=urllib.request.Request('http://127.0.0.1:18886/v1/default/banks/'+bank+'/memories/recall',data=json.dumps({'query':'Aurora Orchard approved campaign code','budget':'low','max_tokens':1024}).encode(),headers={'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=45) as r:recall=json.load(r)
   (A/'backend-recall.private.json').write_text(json.dumps(recall));found=bool(re.search(r'Copper\s+Aspen\s*826',json.dumps(recall),re.I))
  except Exception:pass
  if found:break
  time.sleep(5)
 assert found,'Automatic capture not found in isolated1.1 bank';reset('reset-recall');result,receipt=turn('fresh-recall','Use hindsight_recall to retrieve the approved campaign code for the fictional training client Aurora Orchard. Return the exact code from memory. Do not guess, store another memory, send messages or delegate.');assert 'hindsight_recall' in receipt.get('successfulToolNames',[]) and re.search(r'Copper\s+Aspen\s*826',json.dumps(result['result'].get('payloads',[])),re.I)
 proof={'passed':True,'backendVersion':'1.1.0','pluginVersion':'1.2.0','actualAutomaticCaptureUsedNoTools':True,'backendProcessedAndRetainedFact':True,'separateFreshSessionRecallPassed':True,'productionMemoryUntouched':True,'captureReceipt':capture,'recallReceipt':receipt};(A/'memory-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps({k:v for k,v in proof.items() if not k.endswith('Receipt')}),flush=True)
else:raise SystemExit('Use start or accept')
