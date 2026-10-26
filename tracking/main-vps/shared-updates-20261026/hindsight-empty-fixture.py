"""Start 1.1 with production model settings, an empty private database and a real worker."""
import pathlib,subprocess,json,os,time,urllib.parse,urllib.request,secrets
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/shared-updates-20261026');A=W/'hindsight-empty-test';A.mkdir(mode=0o700)
net='cody-shared-20261026';db='cody-shared-20261026-db';api='cody-shared-20261026-api'
def inspect(n):return json.loads(subprocess.check_output(['docker','inspect',n]))[0]
def run(args,label,timeout=180):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
prod=inspect('hindsight');pg=inspect('hindsight-db');candidate='zedbiz/hindsight:1.1.0-flashrank-20261023';im=json.loads(subprocess.check_output(['docker','image','inspect',candidate]))[0];assert im['Id']=='sha256:7b52bf008c64f3ff129bb39004b5a7e930843aea23a6a9fd526cd1fbc4eec42a'
assert subprocess.run(['docker','network','inspect',net],capture_output=True).returncode!=0
password=secrets.token_urlsafe(30);(A/'db.env').write_text('POSTGRES_USER=hindsight\nPOSTGRES_PASSWORD='+password+'\nPOSTGRES_DB=shared_update_probe\n');(A/'data').mkdir();os.chown(A/'data',999,999)
run(['docker','network','create','--label','cody.shared-update-fixture=true',net],'network')
run(['docker','run','-d','--name',db,'--label','cody.shared-update-fixture=true','--network',net,'--memory','768m','--env-file',str(A/'db.env'),'-v',str(A/'data')+':/var/lib/postgresql',pg['Image']],'database')
start=time.monotonic()
while subprocess.run(['docker','exec',db,'pg_isready','-U','hindsight','-d','shared_update_probe'],capture_output=True).returncode:
 assert inspect(db)['State']['Running'] and time.monotonic()-start<120;time.sleep(2)
e=dict(x.split('=',1) for x in prod['Config']['Env']);old=urllib.parse.urlsplit(e['HINDSIGHT_API_DATABASE_URL']);e['HINDSIGHT_API_DATABASE_URL']=urllib.parse.urlunsplit((old.scheme,'hindsight:'+password+'@'+db+':5432','/shared_update_probe','',''));e.update(HINDSIGHT_API_WORKER_ENABLED='true',HINDSIGHT_API_WORKER_MAX_SLOTS='2',HINDSIGHT_API_WORKER_CONSOLIDATION_MAX_SLOTS='1',HINDSIGHT_API_WORKER_ID='cody-shared-update-fixture',HINDSIGHT_ENABLE_API='true',HINDSIGHT_ENABLE_CP='false')
assert all('\n' not in v for v in e.values());(A/'api.env').write_text('\n'.join(k+'='+v for k,v in e.items())+'\n')
run(['docker','run','-d','--name',api,'--label','cody.shared-update-fixture=true','--network',net,'--memory','2g','--cpus','2','--env-file',str(A/'api.env'),'-p','127.0.0.1:18886:8888',im['Id']],'api')
start=time.monotonic()
while True:
 try:
  with urllib.request.urlopen('http://127.0.0.1:18886/health',timeout=3) as r:
   if r.status==200:break
 except Exception:pass
 assert inspect(api)['State']['Running'] and time.monotonic()-start<300,'Fixture readiness deadline';time.sleep(3)
proof={'ready':True,'api':api,'db':db,'network':net,'imageId':im['Id'],'workerEnabled':True,'emptyDatabase':True,'productionModelsPreserved':True,'productionUntouched':True}
(A/'fixture.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
