"""Restore an online database snapshot to isolated containers; no production writes."""
import hashlib,json,os,pathlib,subprocess,sys,time,urllib.parse,urllib.request
os.umask(0o077)
root=pathlib.Path('/opt/openclaw/backups/release-20261023/hindsight-rehearsal')
resume=sys.argv[1:]==['resume-database-init']
if not resume:root.mkdir(mode=0o700)
network='release-20261023-hindsight-rehearsal';dbName=network+'-db';apiName=network+'-api'
candidate='zedbiz/hindsight:1.1.0-flashrank-20261023'
old=json.loads(subprocess.check_output(['docker','inspect','hindsight']))[0]
db=json.loads(subprocess.check_output(['docker','inspect','hindsight-db']))[0]
apiEnv=dict(x.split('=',1) for x in old['Config']['Env'] if '=' in x)
dbEnv=dict(x.split('=',1) for x in db['Config']['Env'] if '=' in x)
user=dbEnv.get('POSTGRES_USER','postgres');database=dbEnv.get('POSTGRES_DB',user)
dump=root/'before.dump'
if not resume:
 with dump.open('xb') as out,(root/'dump.stderr').open('w') as err:
  subprocess.run(['docker','exec','hindsight-db','pg_dump','-U',user,'-d',database,'-Fc'],stdout=out,stderr=err,check=True)
with dump.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
with (root/'dump-catalog.txt').open('w') as out:
 subprocess.run(['docker','run','--rm','--network','none','--entrypoint','pg_restore','-v',str(dump)+':/backup.dump:ro',db['Image'],'--list','/backup.dump'],stdout=out,check=True)
assert dump.stat().st_size>1024
(root/'database.env').write_text('\n'.join(k+'='+v for k,v in dbEnv.items() if k in ['POSTGRES_USER','POSTGRES_PASSWORD','POSTGRES_DB'])+'\n')
if not resume:
 subprocess.run(['docker','network','create',network],check=True,stdout=subprocess.DEVNULL)
 (root/'data').mkdir()
else:
 prior=json.loads(subprocess.check_output(['docker','inspect',dbName]))[0]
 assert not prior['State']['Running'] and prior['Image']==db['Image']
 assert any(m['Source']==str(root/'data') and m['Destination']=='/var/lib/postgresql' for m in prior['Mounts'])
 assert not (root/'data/18/docker/PG_VERSION').exists(),'Do not reinitialize an existing database'
# The entrypoint changes only PGDATA ownership; its parent must also be traversable.
os.chown(root/'data',999,999)
if resume:subprocess.run(['docker','start',dbName],check=True,stdout=subprocess.DEVNULL)
else:subprocess.run(['docker','run','-d','--name',dbName,'--network',network,'--memory','1g','--env-file',str(root/'database.env'),'-v',str(root/'data')+':/var/lib/postgresql',db['Image']],check=True,stdout=subprocess.DEVNULL)
while True:
 p=subprocess.run(['docker','exec',dbName,'pg_isready','-U',user,'-d',database],capture_output=True)
 if p.returncode==0:break
 state=json.loads(subprocess.check_output(['docker','inspect',dbName]))[0]['State'];assert state['Running'],'Rehearsal database exited'
 time.sleep(3)
with dump.open('rb') as src,(root/'restore.log').open('w') as out:
 subprocess.run(['docker','exec','-i',dbName,'pg_restore','--exit-on-error','--no-owner','--no-privileges','-U',user,'-d',database],stdin=src,stdout=out,stderr=subprocess.STDOUT,check=True)
tables=['banks','documents','memory_units','entities','mental_models','knowledge_pages','chunks','directives','webhooks']
def counts():
 result={}
 for table in tables:
  result[table]=int(subprocess.check_output(['docker','exec',dbName,'psql','-U',user,'-d',database,'-Atc','select count(*) from '+table],text=True).strip())
 return result
before=counts()
url=urllib.parse.urlsplit(apiEnv['HINDSIGHT_API_DATABASE_URL'])
assert url.hostname in ['hindsight-db','hindsight-postgres'],'Review unexpected production database endpoint'
userinfo=url.netloc.rsplit('@',1)[0]
apiEnv['HINDSIGHT_API_DATABASE_URL']=urllib.parse.urlunsplit((url.scheme,userinfo+'@'+dbName+':'+str(url.port or 5432),url.path,url.query,url.fragment))
apiEnv.update(HINDSIGHT_API_WORKER_ENABLED='false',HINDSIGHT_API_WORKER_ID='release-rehearsal',HINDSIGHT_ENABLE_API='true',HINDSIGHT_ENABLE_CP='false')
(root/'api.env').write_text('\n'.join(k+'='+v for k,v in apiEnv.items() if k.startswith(('HINDSIGHT_','HF_','TOKENIZERS_','TRANSFORMERS_')))+'\n')
subprocess.run(['docker','run','-d','--name',apiName,'--network',network,'--memory','3g','--cpus','2','--env-file',str(root/'api.env'),'-p','127.0.0.1:18888:8888',candidate],check=True,stdout=subprocess.DEVNULL)
while True:
 try:
  with urllib.request.urlopen('http://127.0.0.1:18888/health',timeout=10) as response:
   health=json.load(response)
  if response.status==200:break
 except Exception:pass
 state=json.loads(subprocess.check_output(['docker','inspect',apiName]))[0]['State'];assert state['Running'],'Rehearsal API exited; retain private logs'
 time.sleep(5)
after=counts();assert before==after,'Migration changed stored row counts; investigate'
version=subprocess.check_output(['docker','exec',dbName,'psql','-U',user,'-d',database,'-Atc','select version_num from alembic_version'],text=True).strip()
result={'dump':str(dump),'sha256':digest,'oldImage':old['Image'],'candidateImage':json.loads(subprocess.check_output(['docker','inspect',apiName]))[0]['Image'],'databaseImage':db['Image'],'countsBefore':before,'countsAfter':after,'migrationVersion':version,'healthPassed':True,'workerDisabled':True,'productionUntouched':True}
(root/'migration-proof.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
