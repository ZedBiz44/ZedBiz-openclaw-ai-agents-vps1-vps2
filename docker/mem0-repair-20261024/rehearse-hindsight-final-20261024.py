"""Restore a fresh Hindsight dump into isolated PostgreSQL/API containers before any backend cutover."""
import pathlib,json,subprocess,hashlib,os,time,urllib.parse,urllib.request
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/private-recovery-20261024/hindsight-final-proof');assert not W.exists()
mem={k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in P('/proc/meminfo').read_text().splitlines() if ':' in line)};assert mem['MemAvailable']>8*1024**3,'Defer isolated test until more RAM is available';W.mkdir(mode=0o700)
network='cody-hindsight-fresh-20261024';dbName=network+'-db';apiName=network+'-api';candidate='zedbiz/hindsight:1.1.0-flashrank-20261023';assert subprocess.run(['docker','network','inspect',network],capture_output=True).returncode!=0
def inspect(name):return json.loads(subprocess.check_output(['docker','inspect',name]))[0]
def run(args,label,timeout=300,input=None,asJson=False):
 print(json.dumps({'freshHindsightProof':label}),flush=True);p=subprocess.run(args,input=input,capture_output=True,text=True,timeout=timeout);(W/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return json.loads(p.stdout) if asJson else p.stdout
old=inspect('hindsight');db=inspect('hindsight-db');apiEnv=dict(x.split('=',1) for x in old['Config']['Env']);dbEnv=dict(x.split('=',1) for x in db['Config']['Env']);user=dbEnv.get('POSTGRES_USER','postgres');database=dbEnv.get('POSTGRES_DB',user);dump=W/'before.dump'
assert json.loads(subprocess.check_output(['docker','image','inspect',candidate]))[0]['Id']=='sha256:7b52bf008c64f3ff129bb39004b5a7e930843aea23a6a9fd526cd1fbc4eec42a'
with dump.open('xb') as out,(W/'dump.private.err').open('w') as err:r=subprocess.run(['docker','exec','hindsight-db','pg_dump','-U',user,'-d',database,'-Fc'],stdout=out,stderr=err,timeout=300)
assert r.returncode==0 and dump.stat().st_size>1024
with dump.open('rb') as f:dumpSha=hashlib.file_digest(f,'sha256').hexdigest()
run(['docker','run','--rm','--network','none','--entrypoint','pg_restore','-v',str(dump)+':/backup.dump:ro',db['Image'],'--list','/backup.dump'],'dump-catalog')
env={k:v for k,v in dbEnv.items() if k in ['POSTGRES_USER','POSTGRES_PASSWORD','POSTGRES_DB']};assert all('\n' not in v for v in env.values());(W/'database.env').write_text('\n'.join(k+'='+v for k,v in env.items())+'\n')
run(['docker','network','create','--label','cody.hindsight-proof=true',network],'network-create');created=True
try:
 data=W/'data';data.mkdir();os.chown(data,999,999)
 run(['docker','run','-d','--name',dbName,'--label','cody.hindsight-proof=true','--network',network,'--memory','1g','--env-file',str(W/'database.env'),'-v',str(data)+':/var/lib/postgresql',db['Image']],'database-start')
 start=time.monotonic()
 while subprocess.run(['docker','exec',dbName,'pg_isready','-U',user,'-d',database],capture_output=True).returncode!=0:
  assert inspect(dbName)['State']['Running'] and time.monotonic()-start<120;time.sleep(2)
 with dump.open('rb') as src,(W/'restore.private.log').open('w') as out:r=subprocess.run(['docker','exec','-i',dbName,'pg_restore','--exit-on-error','--no-owner','--no-privileges','-U',user,'-d',database],stdin=src,stdout=out,stderr=subprocess.STDOUT,timeout=600)
 assert r.returncode==0
 tables=['banks','documents','memory_units','entities','mental_models','knowledge_pages','chunks','directives','webhooks']
 def counts():return {table:int(subprocess.check_output(['docker','exec',dbName,'psql','-U',user,'-d',database,'-Atc','select count(*) from '+table],text=True).strip()) for table in tables}
 before=counts();url=urllib.parse.urlsplit(apiEnv['HINDSIGHT_API_DATABASE_URL']);assert url.hostname in ['hindsight-db','hindsight-postgres'];userinfo=url.netloc.rsplit('@',1)[0]
 apiEnv['HINDSIGHT_API_DATABASE_URL']=urllib.parse.urlunsplit((url.scheme,userinfo+'@'+dbName+':'+str(url.port or 5432),url.path,url.query,url.fragment));apiEnv.update(HINDSIGHT_API_WORKER_ENABLED='false',HINDSIGHT_API_WORKER_ID='cody-fresh-proof',HINDSIGHT_ENABLE_API='true',HINDSIGHT_ENABLE_CP='false')
 filtered={k:v for k,v in apiEnv.items() if k.startswith(('HINDSIGHT_','HF_','TOKENIZERS_','TRANSFORMERS_'))};assert all('\n' not in v for v in filtered.values());(W/'api.env').write_text('\n'.join(k+'='+v for k,v in filtered.items())+'\n')
 run(['docker','run','-d','--name',apiName,'--label','cody.hindsight-proof=true','--network',network,'--memory','3g','--cpus','2','--env-file',str(W/'api.env'),'-p','127.0.0.1:18889:8888',candidate],'api-start')
 start=time.monotonic()
 while True:
  try:
   with urllib.request.urlopen('http://127.0.0.1:18889/health',timeout=5) as response:
    if response.status==200:break
  except Exception:pass
  assert inspect(apiName)['State']['Running'] and time.monotonic()-start<240,'Candidate health deadline';time.sleep(3)
 after=counts();assert before==after,'Business row counts changed in candidate migration'
 with urllib.request.urlopen('http://127.0.0.1:18889/v1/default/banks',timeout=15) as response:banks=json.load(response)
 (W/'api-banks.private.json').write_text(json.dumps(banks));bankList=banks if isinstance(banks,list) else banks.get('banks',[]);assert not before['banks'] or bankList,'Candidate API did not see restored banks'
 version=subprocess.check_output(['docker','exec',dbName,'psql','-U',user,'-d',database,'-Atc','select version_num from alembic_version'],text=True).strip()
 proof={'passed':True,'productionUntouched':True,'workerDisabledInFixture':True,'dumpSha256':dumpSha,'dumpBytes':dump.stat().st_size,'countsBefore':before,'countsAfter':after,'candidateImage':inspect(apiName)['Image'],'sourceImage':old['Image'],'databaseImage':db['Image'],'migrationVersion':version,'candidateApiSeesRestoredBanks':True}
 (W/'proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
finally:
 for name in [apiName,dbName]:
  if subprocess.run(['docker','inspect',name],capture_output=True).returncode==0:run(['docker','stop','-t','15',name],name+'-stop',90);run(['docker','rm',name],name+'-remove',60)
 if created:run(['docker','network','rm',network],'network-remove',60)
