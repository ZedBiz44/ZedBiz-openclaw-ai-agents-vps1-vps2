"""Fresh Terry checkpoint, reviewed offline migration, managed activation and rollback.

Run in the host's namespaces. All logs and environment captures stay private.
This script does not claim model/tool acceptance; that is a separate live test.
"""
import hashlib,json,os,pathlib,shutil,sqlite3,subprocess,sys,time
os.umask(0o077)
name='terry';live=pathlib.Path('/opt/openclaw/agents/terry')
rehearsal=pathlib.Path('/opt/openclaw/backups/release-20261023/terry')
work=rehearsal/'activation'
candidate='zedbiz/openclaw-base:2026.10.6-core-20261023'
recovery=pathlib.Path('/opt/openclaw/recovery/release-20261023-core')
manifest=pathlib.Path('/opt/openclaw/recovery/fleet-20261018/terry/manifest.json')
def sha(p):
 with pathlib.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,log):
 with (work/log).open('w') as out:return subprocess.run(args,stdout=out,stderr=subprocess.STDOUT)
def rpc(method,params=None):
 args=['docker','exec',name,'openclaw','gateway','call',method,'--json']
 if params is not None:args+=['--params',json.dumps(params)]
 p=subprocess.run(args,capture_output=True,text=True)
 (work/(method+'-before.log')).write_text(p.stdout+p.stderr)
 assert p.returncode==0,'RPC failed; no live stop authorized by this guard'
 obj=json.JSONDecoder().raw_decode(p.stdout[p.stdout.index('{'):])[0]
 (work/(method+'-before.json')).write_text(json.dumps(obj))
 return obj
assert json.loads((rehearsal/'rehearsal-preservation.json').read_text())['passed']
assert json.loads((rehearsal/'rehearsal-migrate-receipt.json').read_text())['exit']==0
assert json.loads((rehearsal/'readiness-gate.json').read_text())['passed'],'Rehearsal acceptance gate required'
work.mkdir(mode=0o700)
catalog=json.loads((recovery/'catalog.json').read_text());proof=json.loads((recovery/'archive-proof.json').read_text())
assert proof['allImageIdsVerified'] and proof['archiveSha256']==catalog['sha256']
assert sha(catalog['archive'])==catalog['sha256']
assert json.loads((recovery/'wiki-proof/proof.json').read_text())['fourContainerSerialization']
ids={x['ref']:x['id'] for x in catalog['images']}
d=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
assert d['State']['Health']['Status']=='healthy' and d['Config']['Image']!=candidate
assert subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',candidate],text=True).strip()==ids[candidate]
refs=subprocess.check_output(['docker','compose','--env-file','.env','config','--images'],cwd=live,text=True).split()
newrefs=[candidate if r==d['Config']['Image'] else r for r in refs];assert set(newrefs)<=ids.keys()
assert shutil.disk_usage(live).free>30*1024**3,'Require 30 GiB rollback headroom'
active=rpc('status').get('shutdownBudget',{}).get('activeWork')
assert active and all(v==0 for v in active.values()),'Active work; retry later without interrupting it'
assert not any(j.get('state',{}).get('runningAtMs') for j in rpc('cron.list',{'includeDisabled':True})['jobs'])
rpc('health')
shutil.copy2(manifest,work/'manifest-before.json')
shutil.copy2(live/'docker-compose.yml',work/'compose-before.yml')
(work/'runtime.env').write_text('\n'.join(d['Config']['Env'])+'\n')
(work/'mounts-before.json').write_text(json.dumps(d['Mounts']))
(work/'baseline.json').write_text(json.dumps({'image':d['Image'],'ref':d['Config']['Image']}))
archive=work/'state-before.tar.gz';checkpoint=False
try:
 assert run(['systemctl','stop','openclaw-terry.service'],'stop.log').returncode==0
 assert subprocess.run(['docker','inspect',name],capture_output=True).returncode!=0
 subprocess.run(['nice','-n','15','tar','-I','pigz -p 2 -3','-cf',str(archive),'-C',str(live),'.'],check=True)
 subprocess.run(['tar','-tf',str(archive)],stdout=subprocess.DEVNULL,check=True)
 restored=work/'restore-check';restored.mkdir()
 subprocess.run(['tar','-xf',str(archive),'-C',str(restored),'./config/state','./agents'],check=True)
 checked=[]
 for p in [restored/'config/state/openclaw.sqlite',*(restored/'agents').glob('*/agent/openclaw-agent.sqlite')]:
  with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as db:
   db.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True)
   assert db.execute('pragma quick_check').fetchall()==[('ok',)]
  checked.append(str(p.relative_to(restored)))
 assert checked
 (work/'checkpoint.json').write_text(json.dumps({'archive':str(archive),'sha256':sha(archive),'restoredDatabases':checked}))
 checkpoint=True
 guard=live/'config/scripts/repair-mem0-host-peer.mjs';st=guard.stat()
 guard.write_bytes(pathlib.Path('/home/jackadmin/vps1-10-6-20261023/repair-mem0-host-peer.mjs').read_bytes());os.chown(guard,st.st_uid,st.st_gid)
 args=['docker','run','--rm','--network','mem0-dev_mem0_network','--network','openclaw','--memory','3g','--env-file',str(work/'runtime.env'),'--user','node','--entrypoint','node']
 for m in d['Mounts']:
  if m['Source'] in ['/var/run/docker.sock','/dev/shm']:continue
  mode='' if m['Source'].startswith(str(live)+'/') and m['RW'] else ':ro'
  args+=['-v',m['Source']+':'+m['Destination']+mode]
 fixargs=args.copy();fixargs[fixargs.index('--entrypoint')+1]='sh'
 assert run(fixargs+[candidate,'/home/node/.openclaw/workspace/ensure-mem0-compat.sh'],'mem0.log').returncode==0
 assert run(args+[candidate,'/app/openclaw.mjs','doctor','--fix','--non-interactive'],'migration.log').returncode==0
 # Same preservation assertions used in the restored-copy rehearsal, now against the fresh checkpoint.
 compare=pathlib.Path('/home/jackadmin/compare-state-20261023.py').read_text()
 old="w=pathlib.Path('/opt/openclaw/backups/release-20261023/terry');stage=w/'rehearsal';ref=w/'comparison-original'"
 assert compare.count(old)==1
 compare=compare.replace(old,"w=pathlib.Path("+repr(str(work))+");stage=pathlib.Path("+repr(str(live))+");ref=w/'comparison-original'")
 exec(compile(compare,'preservation-check','exec'),{'__name__':'__main__'})
 # API shutdown on 2026-10-23: preserve the memory workload and use its documented replacement.
 configPath=live/'config/openclaw.json';config=json.loads(configPath.read_text())
 llm=config['plugins']['entries']['openclaw-mem0']['config']['oss']['llm']
 assert llm['provider']=='openai' and llm['config']['model']=='gpt-4.1-nano-2025-04-14'
 assert json.loads((rehearsal/'mem0-extraction-proof.json').read_text())['passed']
 llm['config']['model']='gpt-5.6-luna'
 configPath.write_text(json.dumps(config,indent=2)+'\n')
 (work/'memory-model-migration.json').write_text(json.dumps({'from':'gpt-4.1-nano-2025-04-14','to':'gpt-5.6-luna','reason':'Official shutdown 2026-10-23','isolatedExtractionAndRecallPassed':True}))
 text=(live/'docker-compose.yml').read_text();assert text.count(d['Config']['Image'])==1
 (live/'docker-compose.yml').write_text(text.replace(d['Config']['Image'],candidate))
 m=json.loads(manifest.read_text());m.update(archive=catalog['archive'],sha256=catalog['sha256'],images=[{'ref':r,'id':ids[r],'automatic':True} for r in sorted(set(newrefs))]);manifest.write_text(json.dumps(m,indent=2))
 assert run(['systemctl','start','openclaw-terry.service'],'start.log').returncode==0
 (work/'activation.json').write_text(json.dumps({'agent':name,'candidate':candidate,'id':ids[candidate],'checkpoint':str(archive),'awaitingLiveAcceptance':True}))
 print(json.dumps({'activated':name,'candidate':candidate,'awaitingLiveAcceptance':True}),flush=True)
except BaseException as error:
 (work/'failure.txt').write_text(type(error).__name__+': '+str(error))
 if checkpoint:
  run(['systemctl','stop','openclaw-terry.service'],'rollback-stop.log')
  failed=live.with_name('terry-failed-release-20261023');assert not failed.exists()
  assert live.resolve()==pathlib.Path('/opt/openclaw/agents/terry') and failed.parent==live.parent
  live.rename(failed);live.mkdir()
  subprocess.run(['tar','-xf',str(archive),'-C',str(live)],check=True)
  shutil.copy2(work/'manifest-before.json',manifest)
  (work/'rollback.json').write_text(json.dumps({'restoredArchive':str(archive),'failedStatePreserved':str(failed),'originalImage':d['Image']}))
 assert run(['systemctl','start','openclaw-terry.service'],'rollback-start.log').returncode==0
 raise
