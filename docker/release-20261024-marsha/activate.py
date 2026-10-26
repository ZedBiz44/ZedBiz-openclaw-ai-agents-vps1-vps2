"""Fresh idle/offline checkpoint and managed Marsha cutover after isolated acceptance."""
import pathlib,subprocess,json,sqlite3,os,sys,shutil,hashlib,time
P=pathlib.Path;os.umask(0o077);live=P('/opt/openclaw/agents/marsha');w=P('/opt/openclaw/backups/release-20261024-marsha');a=w/'activation';manifest=P('/opt/openclaw/recovery/fleet-20261018/marsha/manifest.json')
def sha(p):
 with P(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,label,timeout=None):
 with (a/(label+'.log')).open('w') as out:return subprocess.run(args,stdout=out,stderr=subprocess.STDOUT,timeout=timeout)
def inspect(n):return json.loads(subprocess.check_output(['docker','inspect',n]))[0]
for f in ['preservation.json','model-proof.json','memory-proof.json','lint-summary.json']:
 assert json.loads((w/f).read_text())['passed'],f+' is not accepted'
assert json.loads((w/'startup.json').read_text())['ready']
assert json.loads((w/'asana-pilot/marsha/acceptance.json').read_text())['catalogSchemasAndIdentityMatch']
assert subprocess.run(['docker','inspect','cody-marsha-10-6-rehearsal'],capture_output=True).returncode!=0,'Stop rehearsal first'
catalog=json.loads(P('/opt/openclaw/recovery/release-20261024-marsha/catalog.json').read_text());proof=json.loads(P('/opt/openclaw/recovery/release-20261024-marsha/archive-proof.json').read_text())
assert proof['allImageIdsVerified'] and sha(catalog['archive'])==catalog['sha256']
assert shutil.disk_usage(live).free>25*1024**3
assert not a.exists();a.mkdir(mode=0o700)
assert run(['python3',str(w/'rpc-run.py'),'marsha','pre-cutover'],'idle-rpc').returncode==0
r=json.loads((w/'pre-cutover-rpc.json').read_text());active=r['status'].get('shutdownBudget',{}).get('activeWork');assert active and all(v==0 for v in active.values()),'Active work; no stop'
assert not any(j.get('state',{}).get('runningAtMs') for j in r['cron.list']['jobs']),'Scheduled work active; no stop'
d=inspect('marsha');assert d['State']['Health']['Status']=='healthy'
ids={x['ref']:x['id'] for x in catalog['images']};candidate=json.loads((w/'build.json').read_text())['candidate'];sidecar='zedbiz/asana-http-mcp:2.0.0-components-20261023'
assert inspect(candidate)['Id']==ids[candidate] and inspect(sidecar)['Id']==ids[sidecar]
oldCompose=(live/'docker-compose.yml').read_text();oldSidecar=inspect('marsha-asana-mcp')['Config']['Image'];assert oldCompose.count(d['Config']['Image'])==1 and oldCompose.count(oldSidecar)==1
shutil.copy2(live/'docker-compose.yml',a/'compose-before.yml');shutil.copy2(manifest,a/'manifest-before.json')
(a/'runtime.env').write_text('\n'.join(d['Config']['Env'])+'\n');(a/'mounts.json').write_text(json.dumps(d['Mounts']));(a/'before.json').write_text(json.dumps({'gatewayId':d['Image'],'gatewayRef':d['Config']['Image'],'sidecarRef':oldSidecar}))
archive=a/'state-before.tar.gz';checkpoint=False;changed=False
try:
 assert run(['systemctl','stop','openclaw-marsha.service'],'stop').returncode==0
 assert subprocess.run(['docker','inspect','marsha'],capture_output=True).returncode!=0
 subprocess.run(['nice','-n','15','tar','-I','pigz -p 2 -3','-cf',str(archive),'-C',str(live),'.'],check=True)
 subprocess.run(['tar','-tf',str(archive)],check=True,stdout=subprocess.DEVNULL)
 restored=a/'restore-check';restored.mkdir();subprocess.run(['tar','-xf',str(archive),'-C',str(restored),'./config/state','./agents'],check=True)
 checked=[]
 for p in [restored/'config/state/openclaw.sqlite',*(restored/'agents').glob('*/agent/openclaw-agent.sqlite')]:
  if not p.exists():continue
  with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as db:
   db.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True);assert db.execute('pragma quick_check').fetchall()==[('ok',)]
  checked.append(str(p.relative_to(restored)))
 assert len(checked)==4
 (a/'checkpoint.json').write_text(json.dumps({'archive':str(archive),'sha256':sha(archive),'restoredDatabases':checked}));checkpoint=True
 args=['docker','run','--rm','--name','cody-marsha-live-maintenance','--network','openclaw','--memory','3g','--memory-swap','3g','--env-file',str(a/'runtime.env'),'--user','node','--entrypoint','node']
 for m in d['Mounts']:
  if m['Source'] in ['/var/run/docker.sock','/dev/shm']:continue
  mode='' if m['Source'].startswith(str(live)+'/') and m['RW'] else ':ro';args+=['-v',m['Source']+':'+m['Destination']+mode]
 args+=[candidate,'/app/openclaw.mjs']
 print(json.dumps({'offlineCheckpointVerified':True,'databases':len(checked),'productionMigrationStarting':True}),flush=True)
 changed=True
 assert run(args+['doctor','--fix','--non-interactive'],'migration',1800).returncode==0
 assert run(args+['plugins','update','@vectorize-io/hindsight-openclaw@1.2.0','--accept-capabilities'],'plugin-update',900).returncode==0
 cfg=live/'config/openclaw.json';c=json.loads(cfg.read_text());old=json.loads((w/'config-before.json').read_text())
 for key in ['channels','mcp','tools']:assert c.get(key)==old.get(key),'Protected config changed: '+key
 assert c['agents']['defaults']['model']==old['agents']['defaults']['model']
 mem=c['plugins']['entries']['hindsight-openclaw']['config'];original=old['plugins']['entries']['hindsight-openclaw']['config'];assert all(mem.get(k)==v for k,v in original.items()),'Production memory policy changed'
 mem['allowKnowledgeDelete']=False;cfg.write_text(json.dumps(c,indent=2)+'\n')
 skills=json.loads((w/'skills-before.json').read_text());assert all((live/p).is_file() and sha(live/p)==h for p,h in skills.items())
 # Change only this agent's mounts to the already verified versioned tool wrappers.
 text=oldCompose.replace(d['Config']['Image'],candidate).replace(oldSidecar,sidecar)
 for binary in ['gog','mcporter','summarize']:
  oldPath='/opt/openclaw/shared/bin/'+binary;assert text.count(oldPath)==1
  text=text.replace(oldPath+':','/opt/openclaw/shared/tools-20261023/bin/'+binary+'-wrapper:')
 (live/'docker-compose.yml').write_text(text)
 m=json.loads(manifest.read_text());assert sha(m['wrapper'])==m['wrapper_sha256'];m.update(archive=catalog['archive'],sha256=catalog['sha256'],images=catalog['images']);manifest.write_text(json.dumps(m,indent=2))
 assert run(['systemctl','start','openclaw-marsha.service'],'start',1600).returncode==0
 (a/'activation.json').write_text(json.dumps({'candidate':candidate,'gatewayId':ids[candidate],'sidecarId':ids[sidecar],'backup':str(archive),'awaitingLiveAcceptance':True}));print(json.dumps({'activated':'marsha','candidate':candidate,'awaitingLiveAcceptance':True}),flush=True)
except BaseException as error:
 (a/'failure.txt').write_text(type(error).__name__+': '+str(error))
 if subprocess.run(['docker','inspect','cody-marsha-live-maintenance'],capture_output=True).returncode==0:
  run(['docker','logs','cody-marsha-live-maintenance'],'maintenance-failure')
  assert run(['docker','stop','--time','120','cody-marsha-live-maintenance'],'maintenance-stop').returncode==0
  assert subprocess.run(['docker','inspect','cody-marsha-live-maintenance'],capture_output=True).returncode!=0
 if changed and checkpoint:
  run(['systemctl','stop','openclaw-marsha.service'],'rollback-stop')
  failed=live.with_name('marsha-failed-release-20261024');assert live.resolve()==P('/opt/openclaw/agents/marsha') and not failed.exists() and failed.parent==live.parent
  live.rename(failed);live.mkdir();subprocess.run(['tar','-xf',str(archive),'-C',str(live)],check=True);shutil.copy2(a/'manifest-before.json',manifest)
  (a/'rollback.json').write_text(json.dumps({'restored':str(archive),'failedStatePreserved':str(failed)}))
 assert run(['systemctl','start','openclaw-marsha.service'],'rollback-start',1600).returncode==0
 raise

