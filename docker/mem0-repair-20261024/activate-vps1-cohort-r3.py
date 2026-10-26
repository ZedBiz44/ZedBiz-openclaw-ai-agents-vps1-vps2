"""Serial, backed-up 10.6 cohort activation. Run acceptance before the next agent."""
import pathlib,json,subprocess,os,sys,time,hashlib,shutil,sqlite3,tarfile,re
P=pathlib.Path;os.umask(0o077);agent=sys.argv[1]
allowed=['edith','vivian','amanda','victor','wilma','gohzed','grogar','inga','maggie','terry'];assert agent in allowed
W=P('/opt/openclaw/backups/fleet-10-6-20261024');W.mkdir(exist_ok=True,mode=0o700);A=W/agent;live=P('/opt/openclaw/agents')/agent
M=P('/opt/openclaw/backups/mem0-repair-20261024-r2');R=P('/opt/openclaw/recovery/release-20261024-fleet-tools')
assert json.loads((M/'terry-activation/acceptance.json').read_text())['passed']
catalog=json.loads((R/'catalog.json').read_text());proof=json.loads((R/'archive-proof.json').read_text());assert proof['allImageIdsVerified'] and proof['archiveSha256']==catalog['sha256'] and P(catalog['archive']).is_file()
assert not A.exists(),'Inspect existing agent checkpoint; do not overwrite';A.mkdir(mode=0o700)
def obj(n):return json.loads(subprocess.check_output(['docker','inspect','--type','container',n]))[0]
def imageId(n):return json.loads(subprocess.check_output(['docker','image','inspect',n]))[0]['Id']
def sha(p):
 with P(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,label,timeout=1800,input=None):
 print(json.dumps({'agent':agent,'phase':label,'started':True}),flush=True)
 with (A/(label+'.private.log')).open('w') as f:r=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT,text=True,input=input,timeout=timeout)
 assert r.returncode==0,label+' failed; inspect private log'
 return (A/(label+'.private.log')).read_text()
d=obj(agent);side=obj(agent+'-asana-mcp');assert d['State']['Health']['Status']=='healthy' and not d['State']['OOMKilled']
cfg=json.loads((live/'config/openclaw.json').read_text());slot=cfg['plugins']['slots']['memory']
cohort=agent if agent in ['amanda','victor','wilma','grogar','maggie'] else 'openclaw-base';target='zedbiz/'+cohort+':2026.10.6-tools-full-20261023';sideTarget='zedbiz/asana-http-mcp:2.0.0-'+('edith-' if agent=='edith' else '')+'components-20261023'
ids={v['ref']:v['id'] for v in catalog['images']};assert imageId(target)==ids[target] and imageId(sideTarget)==ids[sideTarget]
assert d['Config']['Image']!=target,'Agent already selects this image; inspect acceptance instead'
assert all('\n' not in value for value in d['Config']['Env']);(A/'runtime.env').write_text('\n'.join(d['Config']['Env'])+'\n')
(A/'config-before.json').write_text(json.dumps(cfg));(A/'mounts-before.json').write_text(json.dumps(d['Mounts']))
rpcCode=(M/'rpc.mjs').read_text()
def rpc(method,params=None):
 args=['docker','run','--rm','-i','--network','container:'+agent,'--pid','container:'+agent,'--memory','512m','--user','node','--env-file',str(A/'runtime.env'),'--entrypoint','node','-e','CODY_RPC_REQUEST='+json.dumps({'method':method,'params':params or {}})]
 for mount in d['Mounts']:
  if mount['Destination'].startswith('/home/node/.openclaw'):args+=['-v',mount['Source']+':'+mount['Destination']+':ro']
 text=run(args+['zedbiz/openclaw-base:2026.10.6-core-20261023','--input-type=module'],'pre-'+method,90,input=rpcCode);return json.loads(text)
gateStart=time.monotonic()
while True:
 active=rpc('status').get('shutdownBudget',{}).get('activeWork');assert active,'No active-work counters; no stop'
 cron=rpc('cron.list',{'includeDisabled':True})
 if all(v==0 for v in active.values()) and not any(j.get('state',{}).get('runningAtMs') for j in cron['jobs']):break
 print(json.dumps({'agent':agent,'waitingForIdle':True,'activeWork':active}),flush=True);assert time.monotonic()-gateStart<1200,'Still active; no interruption';time.sleep(20)
used=int(subprocess.check_output(['du','-sb',str(live)],text=True).split()[0]);dbFiles=[live/'config/state/openclaw.sqlite',*(live/'agents').glob('*/agent/openclaw-agent.sqlite')]
assert shutil.disk_usage(live).free>25*1024**3+used+sum(p.stat().st_size for p in dbFiles if p.exists()),'Require checkpoint and recovery headroom'
manifest=P('/opt/openclaw/recovery/fleet-20261018')/agent/'manifest.json';oldManifest=json.loads(manifest.read_text());assert sha(oldManifest['wrapper'])==oldManifest['wrapper_sha256']
shutil.copy2(manifest,A/'manifest-before.json');shutil.copy2(live/'docker-compose.yml',A/'compose-before.yml');shutil.copy2(live/'workspace/post-start.sh',A/'post-start-before.sh')
instructions={};skills={}
for f in (live/'workspace').glob('*.md'):
 if f.name in ['AGENTS.md','SOUL.md','USER.md','IDENTITY.md','MEMORY.md','TOOLS.md']:instructions[f.name]=f.read_text()
for folder in [live/'skills',live/'workspace/skills']:
 if folder.exists():
  for f in folder.rglob('*'):
   if f.is_file() and not f.is_symlink():skills[str(f.relative_to(live))]=sha(f)
(A/'protected-files.json').write_text(json.dumps({'instructions':instructions,'skills':skills}))
external=None
if slot=='memory-lancedb':
 external=P(cfg['plugins']['entries'][slot]['config']['dbPath']);assert external.resolve()==P('/opt/openclaw/shared/external-memory/lancedb')/agent and external.is_dir();assert not any(p.is_symlink() for p in external.rglob('*'))
def cronRows(path):
 with sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True) as db:
  cols=[r[1] for r in db.execute('pragma table_info(cron_jobs)')];rows=db.execute('select * from cron_jobs').fetchall()
 return cols,rows
archive=A/'state-before.tar.gz';stopped=False;checkpoint=False;changed=False;startedNew=False;startAttempted=False
try:
 run(['systemctl','stop','openclaw-'+agent+'.service'],'managed-stop',650);stopped=True;assert subprocess.run(['docker','inspect','--type','container',agent],capture_output=True).returncode!=0
 cols,oldRows=cronRows(live/'config/state/openclaw.sqlite');(A/'cron-before.json').write_text(json.dumps({'columns':cols,'rows':oldRows}))
 run(['nice','-n','15','tar','-I','pigz -p 2 -3','-cf',str(archive),'-C',str(live),'.'],'offline-backup',3600)
 # The selected restore traverses the compressed archive and verifies tar headers/CRC.
 restore=A/'restore-check';restore.mkdir();run(['tar','-xf',str(archive),'-C',str(restore),'./config/state','./agents'],'restore-databases',900)
 checked=[]
 for p in [restore/'config/state/openclaw.sqlite',*(restore/'agents').glob('*/agent/openclaw-agent.sqlite')]:
  if not p.exists():continue
  with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as db:
   db.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True);assert db.execute('pragma quick_check').fetchall()==[('ok',)]
  checked.append(str(p.relative_to(restore)))
 assert checked
 if external:
  run(['nice','-n','15','tar','-I','pigz -p 2 -3','-cf',str(A/'lancedb-before.tar.gz'),'-C',str(external),'.'],'external-memory-backup',900)
  externalRestore=A/'lancedb-restore-check';externalRestore.mkdir();run(['tar','-xf',str(A/'lancedb-before.tar.gz'),'-C',str(externalRestore)],'external-memory-restore',900)
  externalFiles={str(p.relative_to(external)):sha(p) for p in external.rglob('*') if p.is_file()};restoredFiles={str(p.relative_to(externalRestore)):sha(p) for p in externalRestore.rglob('*') if p.is_file()};assert externalFiles and externalFiles==restoredFiles,'External memory restore differs'
  (A/'external-memory-restore.json').write_text(json.dumps({'passed':True,'files':len(externalFiles),'allFileHashesMatched':True}))
 (A/'checkpoint.json').write_text(json.dumps({'archive':str(archive),'sha256':sha(archive),'sqliteChecks':checked,'externalMemory':str(external) if external else None,'externalArchiveSha256':sha(A/'lancedb-before.tar.gz') if external else None}));checkpoint=True
 maint=['docker','run','--rm','--name','cody-'+agent+'-offline-maintenance','--memory','3g','--memory-swap','3g','--env-file',str(A/'runtime.env'),'--user','node','--entrypoint','node']
 for network in d['NetworkSettings']['Networks']:maint+=['--network',network]
 for k in ['OPENCLAW_SKIP_CHANNELS','OPENCLAW_SKIP_CRON','OPENCLAW_SKIP_GMAIL_WATCHER','OPENCLAW_DISABLE_BONJOUR']:maint+=['-e',k+'=1']
 for mount in d['Mounts']:
  src=mount['Source'];dest=mount['Destination']
  if src in ['/var/run/docker.sock','/dev/shm']:continue
  mode='' if src.startswith(str(live)+'/') and mount['RW'] else ':ro';maint+=['-v',src+':'+dest+mode]
 maint+=[target,'/app/openclaw.mjs'];changed=True
 if '2026.10.4' in d['Config']['Image']:run(maint+['doctor','--fix','--non-interactive'],'core-migration',1800)
 c=json.loads((live/'config/openclaw.json').read_text())
 if slot=='openclaw-mem0':
  assert json.loads((M/'edith-sdk6-proof/sdk-memory-proof.json').read_text())['passed'] if agent=='edith' else True
  projects=list((live/'npm/projects').glob('mem0-*/node_modules/@mem0/openclaw-mem0/package.json'));assert len(projects)==1;project=projects[0].parents[3]
  assert sha(project/'node_modules/@mem0/openclaw-mem0/dist/index.js')==json.loads((M/'build.json').read_text())['customPluginCodeSha256']
  if json.loads((project/'node_modules/mem0ai/package.json').read_text())['version']!='3.3.1':
   project.rename(A/'old-mem0-project');shutil.copytree(M/'project',project,symlinks=True)
   for root,dirs,files in os.walk(project,followlinks=False):
    os.chown(root,1000,1000)
    for f in files+dirs:os.chown(P(root)/f,1000,1000,follow_symlinks=False)
  shutil.copy2('/home/jackadmin/vps1-10-6-20261023/repair-mem0-host-peer.mjs',live/'config/scripts/repair-mem0-host-peer.mjs');os.chown(live/'config/scripts/repair-mem0-host-peer.mjs',1000,1000)
  guard=live/'config/scripts/verify-mem0-sdk331.cjs';guard.write_bytes((M/'mem0-sdk-guard.cjs').read_bytes());os.chown(guard,1000,1000)
  ensure=live/'workspace/ensure-mem0-compat.sh';s=ensure.read_text()
  if 'verify-mem0-sdk331' not in s:
   needle="echo '[mem0-compat]";assert s.count(needle)==1;s=s.replace(needle,'node /home/node/.openclaw/scripts/verify-mem0-sdk331.cjs "$project_dir"\n'+needle);ensure.write_text(s);os.chown(ensure,1000,1000)
  model=c['plugins']['entries'][slot]['config']['oss']['llm']['config']['model']
  if agent=='edith':assert model=='gpt-4.1-nano-2025-04-14';c['plugins']['entries'][slot]['config']['oss']['llm']['config']['model']='gpt-6-luna'
  (live/'config/openclaw.json').write_text(json.dumps(c,indent=2)+'\n')
  compat=maint[:-2];compat[compat.index('--entrypoint')+1]='sh';run(compat+[target,'/home/node/.openclaw/workspace/ensure-mem0-compat.sh'],'memory-compatibility-guard',120)
 elif slot=='hindsight-openclaw':
  run(maint+['plugins','update','@vectorize-io/hindsight-openclaw@1.2.0','--accept-capabilities'],'memory-plugin-update',1800)
  c=json.loads((live/'config/openclaw.json').read_text());c['plugins']['entries'][slot]['config']['allowKnowledgeDelete']=False;(live/'config/openclaw.json').write_text(json.dumps(c,indent=2)+'\n')
 print(json.dumps({'agent':agent,'phase':'doctor-lint','started':True}),flush=True)
 lint=subprocess.run(maint+['doctor','--lint','--json'],capture_output=True,text=True,timeout=1200)
 (A/'lint.private.log').write_text(lint.stdout+'\n'+lint.stderr)
 raw=lint.stdout;begin=raw.find('{');assert begin>=0,'Doctor lint returned no JSON'
 lintData=json.JSONDecoder().raw_decode(raw[begin:])[0];assert 'findings' in lintData and lintData.get('checksRun'),'Doctor lint incomplete'
 (A/'lint.json').write_text(json.dumps(lintData))
 errors=[f for f in lintData['findings'] if str(f.get('severity','')).lower() in ['critical','error']]
 assert not errors,'Doctor lint errors require diagnosis before activation'
 for key in ['channels','mcp','tools']:assert c.get(key)==cfg.get(key),'Protected configuration changed: '+key
 for key in ['model','models','modelPolicy','thinkingDefault','timeoutSeconds']:assert c['agents']['defaults'].get(key)==cfg['agents']['defaults'].get(key),'Protected model policy changed'
 assert c['gateway'].get('auth')==cfg['gateway'].get('auth') and c['plugins']['slots']==cfg['plugins']['slots']
 memBefore=cfg['plugins']['entries'][slot]['config'];memAfter=c['plugins']['entries'][slot]['config']
 expected=json.loads(json.dumps(memBefore))
 if agent=='edith':expected['oss']['llm']['config']['model']='gpt-6-luna'
 assert all(memAfter.get(k)==v for k,v in expected.items()),'Memory configuration changed unexpectedly'
 assert all((live/p).is_file() and sha(live/p)==v for p,v in skills.items()),'Custom skill changed'
 for n,text in instructions.items():
  f=live/'workspace'/n
  if f.exists() and f.read_text()==text:continue
  if n=='TOOLS.md' and not f.exists():assert text.strip() in (live/'workspace/AGENTS.md').read_text()
  elif n=='AGENTS.md':assert f.read_text().strip()==(text.rstrip()+'\n\n## Tools\n\n### Local notes (migrated from TOOLS.md)\n\n'+instructions.get('TOOLS.md','').strip()).strip()
  else:raise AssertionError('Instruction changed: '+n)
 newCols,newRows=cronRows(live/'config/state/openclaw.sqlite');assert cols==newCols;idx=cols.index('declaration_key');retired=[r for r in oldRows if str(r[idx]).startswith('skill-collection-review:')];kept=[r for r in oldRows if r not in retired];assert sorted(kept)==sorted(newRows),'User schedules changed'
 runtimeGuard=live/'config/scripts/verify-runtime-10-6.cjs';runtimeGuard.write_bytes((M/'verify-vps1-runtime-10-6.cjs').read_bytes());os.chown(runtimeGuard,1000,1000)
 post=live/'workspace/post-start.sh';text=post.read_text()
 for old in ['node /opt/zedbiz/verify-amanda-runtime-10-4.cjs','node /opt/zedbiz/verify-workshop-model-10-4.cjs']:
  if old in text:assert text.count(old)==1;text=text.replace(old,'node /home/node/.openclaw/scripts/verify-runtime-10-6.cjs '+agent)
 if 'verify-runtime-10-6.cjs' not in text:
  guardLine='node /home/node/.openclaw/scripts/verify-runtime-10-6.cjs '+agent+' || exit $?\n'
  if text.startswith('#!'):first,rest=text.split('\n',1);text=first+'\n'+guardLine+rest
  else:text=guardLine+text
 post.write_text(text);os.chown(post,1000,1000)
 compose=(A/'compose-before.yml').read_text();assert compose.count(d['Config']['Image'])==1 and compose.count(side['Config']['Image'])==1
 compose=compose.replace(d['Config']['Image'],target).replace(side['Config']['Image'],sideTarget)
 for binary in ['gog','mcporter','summarize']:
  old='/opt/openclaw/shared/bin/'+binary
  if old+':' in compose:assert compose.count(old+':')==1;compose=compose.replace(old+':','/opt/openclaw/shared/tools-20261023/bin/'+binary+'-wrapper:')
 (live/'docker-compose.yml').write_text(compose)
 m=json.loads(manifest.read_text());m.update(archive=catalog['archive'],sha256=catalog['sha256'],images=[v for v in catalog['images'] if v['ref'] in [target,sideTarget]]);manifest.write_text(json.dumps(m,indent=2))
 (A/'preservation.json').write_text(json.dumps({'passed':True,'skills':len(skills),'userSchedulesPreserved':len(kept),'retiredBuiltinReviews':len(retired),'memorySlot':slot,'target':target,'targetId':ids[target],'sidecar':sideTarget,'sidecarId':ids[sideTarget]}))
 startAttempted=True;run(['systemctl','start','openclaw-'+agent+'.service'],'managed-start',1500);startedNew=True
 (A/'activation.json').write_text(json.dumps({'activated':True,'target':target,'targetId':ids[target],'sidecar':sideTarget,'sidecarId':ids[sideTarget],'awaitingLiveAcceptance':True,'checkpoint':str(archive)}));print(json.dumps({'activated':agent,'target':target,'awaitingLiveAcceptance':True}),flush=True)
except BaseException as error:
 (A/'failure.json').write_text(json.dumps({'errorType':type(error).__name__,'message':str(error),'stopped':stopped,'checkpoint':checkpoint,'changed':changed,'startedNew':startedNew}))
 if stopped and not startAttempted:
  maintName='cody-'+agent+'-offline-maintenance'
  if subprocess.run(['docker','inspect','--type','container',maintName],capture_output=True).returncode==0:run(['docker','rm','-f',maintName],'stop-failed-maintenance',180)
  if changed and checkpoint:
   failed=A/'failed-preactivation-state';assert live.resolve()==P('/opt/openclaw/agents')/agent and not failed.exists();live.rename(failed);live.mkdir();run(['tar','-xf',str(archive),'-C',str(live)],'restore-preactivation-state',1800);shutil.copy2(A/'manifest-before.json',manifest)
  run(['systemctl','start','openclaw-'+agent+'.service'],'resume-original',1500)
 raise

