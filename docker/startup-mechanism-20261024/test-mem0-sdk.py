"""Serial copied-state startup controls; never restart or mount writable production agent state."""
import pathlib,json,os,subprocess,time,re,hashlib,sys
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/startup-mechanism-20261024/mem0-full');W.mkdir(parents=True,exist_ok=True,mode=0o700)
def run(a):return subprocess.run(a,capture_output=True,text=True)
def inspect(n):
 p=run(['docker','inspect',n]);assert p.returncode==0,'Inspect failed';return json.loads(p.stdout)[0]
def identity(n):
 d=inspect(n);return (d['Id'],d['State']['Pid'],d['Image'],d['RestartCount'])
prod={n:identity(n) for n in ['marsha','terry']};results=[]
assert int(next(l.split()[1] for l in P('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))>7*1024**2,'Insufficient headroom'
for agent in sys.argv[1:]:
 old=P('/opt/openclaw/backups')/('release-20261024-marsha' if agent=='marsha' else 'release-20261023/terry')
 stage=old/'rehearsal';cfg=stage/'config/openclaw.json';original=cfg.read_bytes();assert cfg.exists()
 baseline=inspect(agent);image=baseline['Image'];out=W/agent;out.mkdir(exist_ok=True,mode=0o700);os.chown(out,1000,1000)
 assert not any(d['State']['Running'] and any(m['RW'] and m['Source'].startswith(str(stage)) for m in d['Mounts']) for d in json.loads(run(['docker','inspect',*run(['docker','ps','-aq']).stdout.split()]).stdout)), 'Existing clone is in use'
 try:
  for variant in ['sdk331-lean','stock']:
   config=json.loads(original);config.setdefault('cron',{})['enabled']=False;config.setdefault('hooks',{})['enabled']=False;config['hooks'].setdefault('internal',{})['enabled']=False
   config['agents']['defaults'].setdefault('heartbeat',{})['every']='0m'
   for a in config['agents'].get('list',[]):a.setdefault('heartbeat',{})['every']='0m'
   config.setdefault('diagnostics',{})['flags']=['plugin.load-profile'];entries=config['plugins']['entries']
   if 'imap' in entries:entries['imap']['enabled']=False
   memory='hindsight-openclaw' if agent=='marsha' else 'openclaw-mem0';mc=entries[memory].setdefault('config',{})
   if agent=='marsha':mc.update(autoRecall=False,autoRetain=False)
   else:mc.update(autoRecall=False,autoCapture=False)
   if variant=='memory-disabled':entries[memory]['enabled']=False;config['plugins']['slots']['memory']='none'
   cfg.write_text(json.dumps(config));os.chown(cfg,1000,1000)
   name='cody-startup-sdk-'+agent+'-'+variant
   assert run(['docker','inspect',name]).returncode!=0,'Fixture name already exists'
   args=['docker','run','-d','--name',name,'--label','cody.startup-mechanism-fixture=true','--network','none','--memory','4g','--memory-swap','4g','--cpus','2','--user','node','--entrypoint','node','--env-file',str(old/'runtime.env')]
   for key in ['OPENCLAW_SKIP_CHANNELS','OPENCLAW_SKIP_CRON','OPENCLAW_SKIP_GMAIL_WATCHER','OPENCLAW_DISABLE_BONJOUR','OPENCLAW_PLUGIN_LOAD_DEBUG']:args+=['-e',key+'=1']
   args+=['-e','OPENCLAW_DIAGNOSTICS=plugin.load-profile']
   for m in baseline['Mounts']:
    src=m['Source'];dest=m['Destination']
    if src in ['/var/run/docker.sock','/dev/shm']:continue
    live='/opt/openclaw/agents/'+agent+'/'
    if src.startswith(live):src=str(stage/src[len(live):]);mode='' if m['RW'] else ':ro'
    else:mode=':ro'
    assert P(src).exists(), 'Missing fixture mount: '+src
    assert not(mode=='' and src.startswith('/opt/openclaw/agents/'))
    args+=['-v',src+':'+dest+mode]
   if variant=='sdk331-lean':args+=['-v','/opt/openclaw/backups/startup-mechanism-20261024/mem0-lean/node_modules:/home/node/.openclaw/npm/projects/mem0-openclaw-mem0-09729737ad__openclaw-generation__g-1e5cd6aa3ff70dae/node_modules:ro']
   args+=['-v',str(out)+':/diagnostic',image,'--cpu-prof','--cpu-prof-dir=/diagnostic','--cpu-prof-name='+variant+'.cpuprofile','/app/openclaw.mjs','gateway','run','--port','3010','--bind','loopback']
   p=run(args);assert p.returncode==0,'Fixture launch failed';print(json.dumps({'started':agent,'variant':variant,'network':'none','productionUnchanged':True}),flush=True)
   start=time.monotonic();ready=None;last=0;log='';samples=[]
   try:
    while time.monotonic()-start<420:
     d=inspect(name);l=run(['docker','logs',name]);log=l.stdout+l.stderr;elapsed=time.monotonic()-start
     if not d['State']['Running']:break
     root=P('/sys/fs/cgroup'+P('/proc/'+str(d['State']['Pid'])+'/cgroup').read_text().strip().split('::')[-1]);s={a[0]:int(a[1]) for line in (root/'memory.stat').read_text().splitlines() if len(a:=line.split())==2}
     samples.append({'elapsed':elapsed,'anonMiB':s['anon']/2**20,'memoryMiB':int((root/'memory.current').read_text())/2**20})
     if 'startup phase: sidecars.subagent-recovery' in log:
      ready=ready or elapsed
      if elapsed-ready>8:break
     if elapsed-last>45:print(json.dumps({'agent':agent,'variant':variant,'elapsed':round(elapsed),'ready':ready is not None}),flush=True);last=elapsed
     available=int(next(l.split()[1] for l in P('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))
     assert available>3*1024**2,'Host available memory below safety floor'
     time.sleep(2)
    phases=[{'phase':m[1],'ms':float(m[2]),'totalMs':float(m[3])} for m in re.finditer(r'startup phase: (\S+) ([\d.]+)ms total=([\d.]+)ms',log)]
    result={'agent':agent,'variant':variant,'ready':ready is not None,'wallSeconds':ready,'phases':phases,'finalSample':samples[-1] if samples else None,'oom':d['State']['OOMKilled'],'exitCode':d['State']['ExitCode']}
    (out/(variant+'.log')).write_text(log);(out/(variant+'.json')).write_text(json.dumps(result,indent=2));results.append(result)
    print(json.dumps({'finished':agent,'variant':variant,'ready':result['ready'],'wallSeconds':ready,'topPhases':sorted(phases,key=lambda x:-x['ms'])[:4]}),flush=True)
   finally:
    run(['docker','stop','--time','30',name]);run(['docker','rm',name])
    assert all(identity(n)==prod[n] for n in prod),'Production changed externally'
 finally:
  cfg.write_bytes(original);os.chown(cfg,1000,1000);assert hashlib.sha256(cfg.read_bytes()).digest()==hashlib.sha256(original).digest()
(W/'tests.json').write_text(json.dumps({'tests':results,'productionUnchanged':True,'cloneConfigsRestored':True},indent=2));print(json.dumps({'complete':True,'tests':len(results),'productionUnchanged':True}),flush=True)



