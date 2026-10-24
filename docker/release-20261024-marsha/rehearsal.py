"""Bounded Marsha rehearsal on copied state; no inbound work or live memory writes."""
import pathlib,subprocess,json,os,sys,time,re,hashlib
P=pathlib.Path;os.umask(0o077);w=P('/opt/openclaw/backups/release-20261024-marsha');stage=w/'rehearsal';live=P('/opt/openclaw/agents/marsha');name='cody-marsha-10-6-rehearsal'
build=json.loads((w/'build.json').read_text());candidate=build['candidate'];action=sys.argv[1]
assert json.loads(subprocess.check_output(['docker','image','inspect',candidate]))[0]['Id']==build['candidateId']
def args(detached=False):
 a=['docker','run','-d' if detached else '--rm','--network','openclaw','--network','release-20261023-hindsight-rehearsal','--memory','3g','--memory-swap','3g','--env-file',str(w/'runtime.env'),'--user','node','--entrypoint','node']
 if detached:a+=['--name',name]
 for key in ['OPENCLAW_SKIP_CHANNELS','OPENCLAW_SKIP_CRON','OPENCLAW_SKIP_GMAIL_WATCHER','OPENCLAW_DISABLE_BONJOUR']:a+=['-e',key+'=1']
 for m in json.loads((w/'mounts.json').read_text()):
  src=m['Source'];dst=m['Destination']
  if src in ['/var/run/docker.sock','/dev/shm']:continue
  if src.startswith(str(live)+'/'):src=str(stage/src[len(str(live))+1:]);mode='' if m['RW'] else ':ro'
  else:mode=':ro'
  if src in ['/opt/openclaw/shared/bin/'+x for x in ['gog','mcporter','summarize']]:src='/opt/openclaw/shared/tools-20261023/bin/'+P(src).name+'-wrapper'
  a+=['-v',src+':'+dst+mode]
 a+=['-v',str(w/'wiki')+':/opt/openclaw/shared/knowledge/wiki',candidate,'/app/openclaw.mjs']
 return a
if action=='isolate-memory':
 assert json.loads((w/'memory-fixture.json').read_text())['backendVersionMatchesProduction']
 f=stage/'config/openclaw.json';d=json.loads(f.read_text());m=d['plugins']['entries']['hindsight-openclaw']['config'];m.update(hindsightApiUrl='http://cody-marsha-hindsight-1-0:8888',bankId='cody-marsha-isolated-20261024',autoRetain=True);f.write_text(json.dumps(d,indent=2)+'\n');print('Clone targets empty isolated memory backend; production bank untouched',flush=True)
elif action in ['migrate','plugin-plan','plugin-update','lint']:
 if action=='migrate':(w/'before-migration-config.json').write_bytes((stage/'config/openclaw.json').read_bytes())
 tail={'migrate':['doctor','--fix','--non-interactive'],'plugin-plan':['plugins','update','@vectorize-io/hindsight-openclaw@1.2.0','--dry-run'],'plugin-update':['plugins','update','@vectorize-io/hindsight-openclaw@1.2.0','--accept-capabilities'],'lint':['doctor','--lint','--json']}[action]
 with (w/(action+'.log')).open('w') as f:p=subprocess.run(args()+tail,stdout=f,stderr=subprocess.STDOUT)
 (w/(action+'-receipt.json')).write_text(json.dumps({'exit':p.returncode}));print(json.dumps({'phase':action,'exit':p.returncode}),flush=True)
 if action=='plugin-update' and p.returncode==0:
  f=stage/'config/openclaw.json';d=json.loads(f.read_text());d['plugins']['entries']['hindsight-openclaw']['config']['allowKnowledgeDelete']=False;f.write_text(json.dumps(d,indent=2)+'\n')
 sys.exit(p.returncode)
elif action=='compare':
 before=json.loads((w/'before-migration-config.json').read_text());after=json.loads((stage/'config/openclaw.json').read_text());checks={}
 for k in ['mcp','tools','channels']:checks[k]=before.get(k)==after.get(k)
 for k in ['model','models','modelPolicy','thinkingDefault','timeoutSeconds']:checks['defaults.'+k]=before['agents']['defaults'].get(k)==after['agents']['defaults'].get(k)
 checks['auth']=before.get('gateway',{}).get('auth')==after.get('gateway',{}).get('auth');checks['memorySlot']=before['plugins']['slots']==after['plugins']['slots']
 old=before['plugins']['entries']['hindsight-openclaw']['config'];new=after['plugins']['entries']['hindsight-openclaw']['config'];overrides={'hindsightApiUrl':'http://cody-marsha-hindsight-1-0:8888','bankId':'cody-marsha-isolated-20261024','autoRetain':True};checks['memorySettings']=all(new.get(k)==overrides.get(k,v) for k,v in old.items());checks['knowledgeDeletionDisabled']=new.get('allowKnowledgeDelete') is False
 skills=json.loads((w/'skills-before.json').read_text());checks['skills']=all((stage/p).is_file() and hashlib.sha256((stage/p).read_bytes()).hexdigest()==h for p,h in skills.items())
 ref=w/'comparison-original';instructions=[]
 for f in (ref/'workspace').glob('*'):
  p=stage/'workspace'/f.name
  if f.name=='TOOLS.md':checks['instructions.TOOLS']=p.read_bytes()==f.read_bytes() if p.exists() else f.read_text().strip() in (stage/'workspace/AGENTS.md').read_text()
  elif f.name=='AGENTS.md' and p.read_bytes()!=f.read_bytes():
   expected=f.read_text().rstrip()+'\n\n## Tools\n\n### Local notes (migrated from TOOLS.md)\n\n'+(ref/'workspace/TOOLS.md').read_text().strip();checks['instructions.AGENTS']=p.read_text().strip()==expected.strip();instructions.append('TOOLS.md migrated into AGENTS.md')
  else:checks['instructions.'+f.name]=p.is_file() and p.read_bytes()==f.read_bytes()
 result={'passed':all(checks.values()),'checks':checks,'customSkills':len(skills),'instructionMigrations':instructions};(w/'preservation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True);assert result['passed']
elif action=='start':
 assert json.loads((w/'preservation.json').read_text())['passed']
 subprocess.run(args(True)+['gateway','run','--port',str(json.loads((stage/'config/openclaw.json').read_text())['gateway']['port']),'--bind','loopback'],check=True,stdout=subprocess.DEVNULL)
 start=time.monotonic();samples=[];ready=None
 try:
  while time.monotonic()-start<480:
   d=json.loads(subprocess.check_output(['docker','inspect',name]))[0];p=subprocess.run(['docker','logs',name],capture_output=True,text=True);log=p.stdout+p.stderr
   if not d['State']['Running']:raise RuntimeError('Fixture exited; inspect private log')
   root=P('/sys/fs/cgroup'+P('/proc/'+str(d['State']['Pid'])+'/cgroup').read_text().strip().split('::')[-1]);stats={x[0]:int(x[1]) for line in (root/'memory.stat').read_text().splitlines() if len(x:=line.split())==2}
   samples.append({'elapsed':round(time.monotonic()-start,1),'memoryMiB':round(int((root/'memory.current').read_text())/2**20,1),'anonMiB':round(stats['anon']/2**20,1),'workingMiB':round((int((root/'memory.current').read_text())-stats.get('inactive_file',0))/2**20,1)})
   if 'startup phase: sidecars.subagent-recovery' in log:
    ready=ready or time.monotonic()
    if time.monotonic()-ready>30:break
   time.sleep(3)
  else:raise RuntimeError('Fixture readiness deadline')
  phases=[{'phase':m[1],'ms':float(m[2]),'totalMs':float(m[3])} for m in re.finditer(r'startup phase: (\S+) ([\d.]+)ms total=([\d.]+)ms',log)]
  result={'ready':ready is not None,'samples':samples,'phases':phases,'oom':d['State']['OOMKilled']};(w/'startup.json').write_text(json.dumps(result,indent=2));print(json.dumps({'ready':result['ready'],'settled':samples[-1],'phases':sorted(phases,key=lambda x:-x['ms'])[:8]}),flush=True)
 finally:
  (w/'rehearsal-gateway.log').write_text(log)
elif action=='stop':
 if subprocess.run(['docker','inspect',name],capture_output=True).returncode==0:
  with (w/'rehearsal-gateway.log').open('w') as f:subprocess.run(['docker','logs',name],stdout=f,stderr=subprocess.STDOUT)
  subprocess.run(['docker','stop',name],check=True,stdout=subprocess.DEVNULL);subprocess.run(['docker','rm',name],check=True,stdout=subprocess.DEVNULL)
 print(json.dumps({'stopped':name}),flush=True)
else:raise SystemExit('Unsupported phase')

