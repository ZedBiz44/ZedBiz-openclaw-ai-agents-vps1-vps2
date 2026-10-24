"""Verify real configured model/embedding inference on an isolated disposable Qdrant."""
import pathlib,subprocess,json,time,urllib.request,os
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/startup-mechanism-20261024')
def run(a):return subprocess.run(a,capture_output=True,text=True)
def obj(n):return json.loads(run(['docker','inspect','--type','container',n]).stdout)[0]
network='cody-sdk331-memory-proof';q='cody-sdk-pilot-qdrant';test='cody-sdk331-memory-proof'
assert not run(['docker','ps','-q','--filter','label=cody.startup-mechanism-fixture=true']).stdout.strip(),'Finish startup benchmarks first'
assert run(['docker','network','inspect',network]).returncode!=0
assert run(['docker','inspect','--type','container',q]).returncode!=0 and run(['docker','inspect','--type','container',test]).returncode!=0
before={n:(obj(n)['Id'],obj(n)['State']['Pid'],obj(n)['RestartCount']) for n in ['marsha','terry']}
assert run(['docker','network','create','--label','cody.startup-mechanism-fixture=true',network]).returncode==0
try:
 image=obj('mem0-dev-qdrant-1')['Image']
 p=run(['docker','run','-d','--name',q,'--label','cody.startup-mechanism-fixture=true','--network',network,'--memory','512m','--memory-swap','512m','--cpus','1','--tmpfs','/qdrant/storage:rw,size=128m',image]);assert p.returncode==0
 for _ in range(40):
  ip=obj(q)['NetworkSettings']['Networks'][network]['IPAddress']
  try:
   assert urllib.request.urlopen('http://'+ip+':6333/healthz',timeout=1).status==200;break
  except Exception:time.sleep(.5)
 else:raise RuntimeError('Isolated Qdrant readiness failed')
 args=['docker','run','--rm','--name',test,'--label','cody.startup-mechanism-fixture=true','--network',network,'--memory','2g','--memory-swap','2g','--cpus','2','--user','node','--entrypoint','node','--env-file','/opt/openclaw/backups/release-20261023/terry/runtime.env','-e','MEM0_TELEMETRY=false','-v',str(W)+':/diagnostic','-v',str(W/'mem0-lean')+':/candidate:ro','-v','/opt/openclaw/agents/terry/config/openclaw.json:/input/openclaw.json:ro',obj('terry')['Image'],'/diagnostic/sdk331-memory-proof.mjs']
 p=subprocess.run(args,capture_output=True,text=True,timeout=240);(W/'sdk-memory-proof.private.log').write_text(p.stdout+p.stderr)
 proof=json.loads((W/'sdk-memory-proof.json').read_text());print(json.dumps(proof),flush=True);assert p.returncode==0 and proof['passed'],'Functional SDK proof failed; private diagnostics retained'
finally:
 for n in [test,q]:
  if run(['docker','inspect','--type','container',n]).returncode==0:
   assert obj(n)['Config']['Labels'].get('cody.startup-mechanism-fixture')=='true';run(['docker','rm','-f',n])
 run(['docker','network','rm',network])
 for n,x in before.items():assert x==(obj(n)['Id'],obj(n)['State']['Pid'],obj(n)['RestartCount'])
 print(json.dumps({'temporaryMemoryServicesRemoved':True,'productionIdentitiesUnchanged':True}),flush=True)

