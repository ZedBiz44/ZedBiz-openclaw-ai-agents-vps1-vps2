"""Deploy accepted Hindsight1.1 with a stopped-service database checkpoint and tested rollback inputs."""
import pathlib,subprocess,json,os,time,urllib.request,urllib.parse,hashlib,datetime,re
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/shared-updates-20261026');A=W/'update-hindsight';A.mkdir(mode=0o700)
memory=json.loads((W/'marsha-pilot/memory-proof.json').read_text());migration=json.loads((W/'hindsight-migration-proof/proof.json').read_text());assert memory['passed'] and migration['passed'];candidate=migration['candidateImage'];rpc=P('/opt/openclaw/backups/mem0-repair-20261024-r2/rpc.mjs').read_text()
def inspect(n):return json.loads(subprocess.check_output(['docker','inspect',n]))[0]
def run(args,label,timeout=300,input=None):
 p=subprocess.run(args,input=input,capture_output=True,text=True,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
def call(agent,method,params=None):return json.loads(run(['docker','exec','-i','-e','CODY_RPC_REQUEST='+json.dumps({'method':method,'params':params or {}}),agent,'node','--input-type=module'],agent+'-'+method,120,rpc))
start=time.monotonic()
while True:
 idle=True
 for agent in ['marsha','gohzed','grogar','inga','maggie']:
  work=call(agent,'status').get('shutdownBudget',{}).get('activeWork');assert work;idle &= all(v==0 for v in work.values());jobs=call(agent,'cron.list',{'includeDisabled':True})['jobs'];idle &= not any(j.get('state',{}).get('runningAtMs') for j in jobs)
 if idle:break
 assert time.monotonic()-start<1200,'Hindsight clients remain busy';time.sleep(15)
old=inspect('hindsight');pg=inspect('hindsight-db');(A/'before.inspect.private.json').write_text(json.dumps(old));labels=old['Config']['Labels'];compose=P(labels['com.docker.compose.project.config_files']);service=labels['com.docker.compose.service'];original=compose.read_bytes();(A/'compose-before.private').write_bytes(original);render=json.loads(run(['docker','compose','-f',str(compose),'config','--format','json'],'config-before'));oldRef=render['services'][service]['image'];assert original.decode().count(oldRef)==1 and oldRef==old['Config']['Image'] and old['Image']==migration['sourceImage'];env=dict(e.split('=',1) for e in pg['Config']['Env']);user=env.get('POSTGRES_USER','postgres');database=env.get('POSTGRES_DB',user);assert re.fullmatch(r'[a-zA-Z0-9_]+',user) and re.fullmatch(r'[a-zA-Z0-9_]+',database)
tables=['banks','documents','memory_units','entities','mental_models','knowledge_pages','chunks','directives','webhooks']
def counts():return {t:int(subprocess.check_output(['docker','exec','hindsight-db','psql','-U',user,'-d',database,'-Atc','select count(*) from '+t],text=True).strip()) for t in tables}
changed=False;checkpointReady=False
try:
 run(['docker','stop','-t','45','hindsight'],'stop-for-checkpoint',120);changed=True;before=counts();(A/'counts-before.json').write_text(json.dumps(before));dump=A/'before.dump'
 with dump.open('xb') as out,(A/'dump.private.err').open('w') as err:p=subprocess.run(['docker','exec','hindsight-db','pg_dump','-U',user,'-d',database,'-Fc'],stdout=out,stderr=err,timeout=300)
 assert p.returncode==0 and dump.stat().st_size>1024;run(['docker','run','--rm','--network','none','--entrypoint','pg_restore','-v',str(dump)+':/before.dump:ro',pg['Image'],'--list','/before.dump'],'dump-catalog');checkpointReady=True
 with dump.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
 compose.write_bytes(original.decode().replace(oldRef,candidate).encode());after=json.loads(run(['docker','compose','-f',str(compose),'config','--format','json'],'config-after'));expected=json.loads(json.dumps(render));expected['services'][service]['image']=candidate;assert after==expected
 run(['docker','compose','-f',str(compose),'up','-d','--no-deps','--no-build',service],'activate',300);start=time.monotonic()
 while True:
  try:
   with urllib.request.urlopen('http://127.0.0.1:8898/health',timeout=5) as response:assert response.status==200
   d=inspect('hindsight');assert d['State'].get('Health',{}).get('Status')=='healthy';break
  except Exception:assert inspect('hindsight')['State']['Running'] and time.monotonic()-start<300;time.sleep(3)
 version=run(['docker','exec','hindsight','python','-c',"from importlib.metadata import version;print(version('hindsight-api'))"],'version').strip();assert version=='1.1.0';assert run(['docker','exec','hindsight','python','-c',"from importlib.metadata import version;print(version('flashrank'))"],'flashrank').strip()=='0.2.10';afterCounts=counts();assert all(afterCounts[t]>=before[t] for t in ['banks','documents','memory_units','entities']);assert inspect('hindsight-db')['Image']==pg['Image'];new=inspect('hindsight');assert new['Image']==candidate and new['Mounts']==old['Mounts'] and new['HostConfig']['PortBindings']==old['HostConfig']['PortBindings'];oldEnv=dict(e.split('=',1) for e in old['Config']['Env']);newEnv=dict(e.split('=',1) for e in new['Config']['Env']);assert all(newEnv.get(k)==v for k,v in oldEnv.items() if k.startswith(('HINDSIGHT_','HF_','TOKENIZERS_','TRANSFORMERS_')))
 with urllib.request.urlopen('http://127.0.0.1:8898/v1/default/banks',timeout=30) as response:banks=json.load(response)
 (A/'banks-after.private.json').write_text(json.dumps(banks));assert banks
 proof={'passed':True,'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':version,'oldImageId':old['Image'],'newImageId':new['Image'],'flashrankVersion':'0.2.10','postgresImageUnchanged':True,'modelsCredentialsAndRuntimeSettingsPreserved':True,'actualAutomaticCaptureAndFreshRecallPilotPassed':True,'freshFullMigrationCountsExactlyPreserved':True,'businessCountsAtLeastCheckpoint':True,'checkpointCounts':before,'countsAfter':afterCounts,'rollbackDumpSha256':digest,'rollbackDumpBytes':dump.stat().st_size,'onlyComposeImageChanged':True,'workerEnabled':oldEnv.get('HINDSIGHT_API_WORKER_ENABLED')=='true'};(A/'acceptance.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
except Exception:
 if changed:
  current=inspect('hindsight')
  if current['State']['Running']:run(['docker','stop','-t','45','hindsight'],'rollback-stop',120)
  compose.write_bytes(original)
  if checkpointReady and current['Image']==candidate:
   run(['docker','exec','hindsight-db','dropdb','-U',user,'--if-exists','--force',database],'rollback-drop-db');run(['docker','exec','hindsight-db','createdb','-U',user,'-O',user,database],'rollback-create-db')
   with (A/'before.dump').open('rb') as src,(A/'rollback-restore.private.log').open('w') as out:p=subprocess.run(['docker','exec','-i','hindsight-db','pg_restore','--exit-on-error','--no-owner','--no-privileges','-U',user,'-d',database],stdin=src,stdout=out,stderr=subprocess.STDOUT,timeout=600)
   assert p.returncode==0 and counts()==before
  run(['docker','compose','-f',str(compose),'up','-d','--no-deps','--no-build',service],'rollback-service');(A/'rollback.json').write_text(json.dumps({'oldImageRestored':True,'databaseCheckpointRestored':checkpointReady}))
 raise
