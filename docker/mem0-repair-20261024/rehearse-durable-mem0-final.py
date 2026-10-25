"""Current Terry state, exact production entrypoint/post-start, isolated Qdrant."""
import pathlib,subprocess,json,os,shutil,sqlite3,time,re,hashlib,sys,shlex
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/mem0-repair-20261024-r2');stage=W/'terry-rehearsal';live=P('/opt/openclaw/agents/terry')
name='cody-mem0-repair-terry';network='cody-mem0-repair-20261024';q='cody-mem0-repair-qdrant'
def run(a,**kw):return subprocess.run(a,capture_output=True,text=True,**kw)
def obj(n):
 r=run(['docker','inspect','--type','container',n]);assert r.returncode==0;return json.loads(r.stdout)[0]
def identity(n):
 d=obj(n);return [d['Id'],d['State']['Pid'],d['Image'],d['RestartCount']]
before={n:identity(n) for n in ['terry','marsha']};action=sys.argv[1] if len(sys.argv)>1 else 'prepare'
if action=='prepare':
 assert json.loads((W/'build.json').read_text())['passed'];assert not stage.exists()
 d=obj('terry');(W/'runtime.env').write_text('\n'.join(d['Config']['Env'])+'\n');(W/'mounts.json').write_text(json.dumps(d['Mounts']));(W/'container-command.json').write_text(json.dumps({'image':d['Image'],'command':d['Config']['Cmd']}))
 projects=list((live/'npm/projects').glob('mem0-*/node_modules/@mem0/openclaw-mem0/package.json'));assert len(projects)==1;project=projects[0].parents[3]
 def skip(parent,names):
  p=P(parent)
  if p==live/'npm/projects':return {project.name}
  if p==live/'config':return {'tmp','cache'}&set(names)
  return set()
 shutil.copytree(live,stage,symlinks=True,ignore=skip)
 for source in [live/'config/state/openclaw.sqlite',*(live/'agents').glob('*/agent/openclaw-agent.sqlite')]:
  if not source.exists():continue
  target=stage/source.relative_to(live)
  for suffix in ['', '-wal','-shm']:
   f=P(str(target)+suffix)
   if f.exists():f.unlink()
  with sqlite3.connect('file:'+str(source)+'?mode=ro',uri=True) as a,sqlite3.connect(target) as b:a.backup(b)
  st=source.stat();os.chown(target,st.st_uid,st.st_gid)
 ownerdb=stage/'config/state/openclaw.sqlite'
 with sqlite3.connect(ownerdb) as db:
  tables={r[0] for r in db.execute("select name from sqlite_master where type='table'")}
  if 'agent_database_leases' in tables:db.execute('delete from agent_database_leases')
  if 'state_leases' in tables:db.execute("delete from state_leases where scope='gateway-owner' and lease_key='global'")
 for root,dirs,files in os.walk(live,followlinks=False):
  for source in [P(root),*[P(root)/n for n in files+dirs]]:
   target=stage/source.relative_to(live)
   if target.exists() or target.is_symlink():st=source.lstat();os.chown(target,st.st_uid,st.st_gid,follow_symlinks=False)
 target=stage/'npm/projects'/project.name;shutil.copytree(W/'project',target,symlinks=True)
 for root,dirs,files in os.walk(target):
  os.chown(root,1000,1000)
  for n in files:os.chown(P(root)/n,1000,1000)
 cfg=stage/'config/openclaw.json';original=json.loads(cfg.read_text());c=json.loads(cfg.read_text());c.setdefault('cron',{})['enabled']=False;c.setdefault('hooks',{})['enabled']=False;c['hooks'].setdefault('internal',{})['enabled']=False
 c['agents']['defaults'].setdefault('heartbeat',{})['every']='0m'
 for a in [*c['agents'].get('list',[]),*c['agents'].get('entries',{}).values()]:a.setdefault('heartbeat',{})['every']='0m'
 c['plugins']['entries'].get('imap',{})['enabled']=False
 m=c['plugins']['entries']['openclaw-mem0']['config'];m.update(autoRecall=True,autoCapture=True)
 v=m['oss']['vectorStore']['config'];v.update(host=q,port=6333,collectionName='cody_durable_mem0_20261024');v.pop('url',None);v.pop('apiKey',None)
 assert m['oss']['disableHistory'] is True;cfg.write_text(json.dumps(c,indent=2)+'\n');os.chown(cfg,1000,1000)
 assert c['agents']['defaults']['model']==original['agents']['defaults']['model'];assert c['channels']==original['channels']
 (W/'clone-project.json').write_text(json.dumps({'projectName':project.name,'customPluginPreserved':True,'liveMemoryUntouched':True}))
 print(json.dumps({'prepared':True,'configModelsAndChannelsPreserved':True,'isolatedMemory':True,'productionUnchanged':all(identity(n)==before[n] for n in before)}),flush=True)
elif action=='start':
 assert stage.exists() and not run(['docker','inspect','--type','container',name]).returncode==0
 if run(['docker','network','inspect',network]).returncode!=0:assert run(['docker','network','create','--label','cody.mem0-repair-fixture=true',network]).returncode==0
 if run(['docker','inspect','--type','container',q]).returncode!=0:
  qstore=W/'qdrant-fixture-storage';qstore.mkdir(exist_ok=True,mode=0o700)
  assert run(['docker','run','-d','--name',q,'--label','cody.mem0-repair-fixture=true','--network',network,'--memory','512m','--memory-swap','512m','-v',str(qstore)+':/qdrant/storage',obj('mem0-dev-qdrant-1')['Image']]).returncode==0
 d=obj('terry');args=['docker','run','-d','--name',name,'--label','cody.mem0-repair-fixture=true','--network',network,'--network','openclaw','--memory','4g','--memory-swap','4g','--cpus','2','--env-file',str(W/'runtime.env'),'--user','node']
 health=d['Config']['Healthcheck'];test=health['Test'];assert test[0] in ['CMD','CMD-SHELL']
 args+=['--health-cmd',test[1] if test[0]=='CMD-SHELL' else shlex.join(test[1:])]
 for key,flag in [('Interval','interval'),('Timeout','timeout'),('StartPeriod','start-period')]:
  if health.get(key):args+=['--health-'+flag,str(health[key])+'ns']
 if health.get('Retries'):args+=['--health-retries',str(health['Retries'])]
 for key in ['OPENCLAW_SKIP_CHANNELS','OPENCLAW_SKIP_CRON','OPENCLAW_SKIP_GMAIL_WATCHER','OPENCLAW_DISABLE_BONJOUR']:args+=['-e',key+'=1']
 for mount in d['Mounts']:
  source=mount['Source'];dest=mount['Destination']
  if source in ['/var/run/docker.sock','/dev/shm']:continue
  mode=':ro'
  if source.startswith(str(live)+'/'):source=str(stage/source[len(str(live))+1:]);mode='' if mount['RW'] else ':ro'
  args+=['-v',source+':'+dest+mode]
 args+=[d['Image'],*d['Config']['Cmd']]
 assert run(args).returncode==0,'Fixture launch failed';start=time.monotonic();last=0;log=''
 try:
  while time.monotonic()-start<900:
   state=obj(name);r=run(['docker','logs',name]);log=r.stdout+r.stderr;elapsed=time.monotonic()-start
   assert state['State']['Running'],'Actual startup route exited; inspect private log'
   phases=[{'phase':m[1],'ms':float(m[2]),'totalMs':float(m[3])} for m in re.finditer(r'startup phase: (\S+) ([\d.]+)ms total=([\d.]+)ms',log)]
   if state['State'].get('Health',{}).get('Status')=='healthy' and any(p['phase']=='sidecars.subagent-recovery' for p in phases):break
   if elapsed-last>40:print(json.dumps({'elapsedSeconds':round(elapsed),'postStartComplete':'[mem0-compat]' in log,'gatewayPhases':len(phases)}),flush=True);last=elapsed
   available=int(next(l.split()[1] for l in P('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')));assert available>3*1024**2,'Host memory below safety floor'
   time.sleep(3)
  else:raise RuntimeError('Exact startup readiness deadline')
  assert '[mem0-compat]' in log and state['RestartCount']==0
  history=json.loads((W/'full-starts.json').read_text()) if (W/'full-starts.json').exists() else []
  result={'passed':True,'wallSeconds':time.monotonic()-start,'exactEntrypointAndPostStart':True,'phases':phases,'restarts':state['RestartCount'],'oom':state['State']['OOMKilled'],'productionUnchanged':all(identity(n)==before[n] for n in before)};history.append(result);(W/'full-starts.json').write_text(json.dumps(history,indent=2));print(json.dumps(result),flush=True)
 finally:(W/'full-start-latest.private.log').write_text(log)
elif action=='stop-gateway':
 if run(['docker','inspect','--type','container',name]).returncode==0:
  assert obj(name)['Config']['Labels'].get('cody.mem0-repair-fixture')=='true';assert run(['docker','stop','--time','90',name]).returncode==0;assert run(['docker','rm',name]).returncode==0
 print(json.dumps({'fixtureGatewayRemoved':True}),flush=True)
else:raise SystemExit('Unknown action')

