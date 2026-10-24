"""Isolated Hindsight1.0 API with an empty test database; no production backlog."""
import pathlib,subprocess,json,os,sys,time,urllib.parse
P=pathlib.Path;os.umask(0o077);w=P('/opt/openclaw/backups/release-20261024-marsha');name='cody-marsha-hindsight-1-0';db='release-20261023-hindsight-rehearsal-db';network='release-20261023-hindsight-rehearsal';dbname='marsha_pilot_20261024'
def inspect(n):return json.loads(subprocess.check_output(['docker','inspect',n]))[0]
if sys.argv[1]=='start':
 assert not (w/'memory-fixture.json').exists()
 d=inspect(db);assert d['State']['Running'] and list(d['NetworkSettings']['Networks'])==[network]
 assert any(m['Source']=='/opt/openclaw/backups/release-20261023/hindsight-rehearsal/data' for m in d['Mounts'])
 p=subprocess.run(['docker','exec',db,'psql','-U','hindsight','-d','postgres','-At','-c',"select datname from pg_database where datname='"+dbname+"'"],capture_output=True,text=True,check=True);assert not p.stdout.strip()
 subprocess.run(['docker','exec',db,'psql','-U','hindsight','-d','postgres','-v','ON_ERROR_STOP=1','-c','CREATE DATABASE '+dbname],check=True,stdout=subprocess.DEVNULL)
 prod=inspect('hindsight');e=dict(x.split('=',1) for x in prod['Config']['Env'] if '=' in x);url=urllib.parse.urlsplit(e['HINDSIGHT_API_DATABASE_URL']);auth=url.netloc.rsplit('@',1)[0]
 e['HINDSIGHT_API_DATABASE_URL']=urllib.parse.urlunsplit((url.scheme,auth+'@'+db+':5432','/'+dbname,url.query,url.fragment));e.update(HINDSIGHT_API_WORKER_ENABLED='true',HINDSIGHT_API_WORKER_MAX_SLOTS='1',HINDSIGHT_API_WORKER_CONSOLIDATION_MAX_SLOTS='1',HINDSIGHT_API_WORKER_ID='cody-marsha-isolated',HINDSIGHT_CP_ENABLED='false')
 env=w/'hindsight-fixture.env';env.write_text('\n'.join(k+'='+v for k,v in e.items())+'\n')
 # Existing API fixture remains stopped with its original database and backlog intact.
 old=inspect('release-20261023-hindsight-rehearsal-api');(w/'prior-fixture-state.json').write_text(json.dumps({'apiWasRunning':old['State']['Running'],'apiId':old['Id'],'originalDatabaseUnchanged':True}))
 if old['State']['Running']:subprocess.run(['docker','stop','release-20261023-hindsight-rehearsal-api'],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['docker','run','-d','--name',name,'--network',network,'--memory','1536m','--memory-swap','1536m','--env-file',str(env),prod['Image'],*prod['Config']['Cmd']],check=True,stdout=subprocess.DEVNULL)
 for _ in range(120):
  d=inspect(name)
  assert d['State']['Running'],'Isolated API exited; inspect private log'
  p=subprocess.run(['docker','exec',name,'python','-c','import urllib.request;print(urllib.request.urlopen("http://127.0.0.1:8888/health",timeout=3).status)'],capture_output=True,text=True)
  if p.returncode==0 and '200' in p.stdout:break
  time.sleep(2)
 else:raise RuntimeError('Isolated API readiness deadline')
 result={'container':name,'imageId':prod['Image'],'backendVersionMatchesProduction':True,'emptyDatabase':dbname,'workerEnabled':True,'copiedBacklogReplayed':False};(w/'memory-fixture.json').write_text(json.dumps(result));print(json.dumps(result),flush=True)
elif sys.argv[1]=='stop':
 if subprocess.run(['docker','inspect',name],capture_output=True).returncode==0:
  with (w/'memory-fixture.log').open('w') as f:subprocess.run(['docker','logs',name],stdout=f,stderr=subprocess.STDOUT)
  subprocess.run(['docker','stop',name],check=True,stdout=subprocess.DEVNULL)
 print(json.dumps({'stopped':name,'testDatabaseRetained':True}),flush=True)

