"""Pilot and patch Connect API/sync together while retaining credentials, cache and access boundaries."""
import pathlib,subprocess,json,os,time,urllib.request,urllib.error,hashlib,datetime
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/shared-updates-20261026');A=W/'update-connect';A.mkdir(mode=0o700);names=['1password-connect-api','1password-connect-sync'];clones=['cody-connect-api-20261026','cody-connect-sync-20261026'];network='cody-dashboard-proof-20261026';catalog=json.loads((W/'candidate-images.json').read_text());candidates=[catalog['connect-api'],catalog['connect-sync']]
def inspect(n):return json.loads(subprocess.check_output(['docker','inspect',n]))[0]
def run(args,label,timeout=180):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
old=[inspect(n) for n in names];assert all(d['State']['Running'] for d in old);(A/'before.inspect.private.json').write_text(json.dumps(old));compose=P(old[0]['Config']['Labels']['com.docker.compose.project.config_files']);assert all(d['Config']['Labels']['com.docker.compose.project.config_files']==str(compose) for d in old);services=[d['Config']['Labels']['com.docker.compose.service'] for d in old];original=compose.read_bytes();(A/'compose-before.private').write_bytes(original);render=json.loads(run(['docker','compose','-f',str(compose),'config','--format','json'],'config-before'));data=next(P(m['Source']) for m in old[0]['Mounts'] if m['Destination']=='/home/opuser/.op/data');credentials=next(P(m['Source']) for m in old[0]['Mounts'] if m['Destination']=='/home/opuser/.op/1password-credentials.json');assert data==P('/var/lib/docker/volumes/1password-connect_1password-data/_data') and data.resolve()==data and credentials==P('/opt/openclaw/1password-connect/1password-credentials.json');credentialSha=hashlib.sha256(credentials.read_bytes()).hexdigest()
def health(container):
 d=inspect(container);assert d['State']['Running'];ip=next(iter(d['NetworkSettings']['Networks'].values()))['IPAddress']
 with urllib.request.urlopen('http://'+ip+':8080/health',timeout=8) as r:assert r.status==200;body=json.load(r)
 states={row['service']:row['status'] for row in body['dependencies']};assert states['sqlite']=='ACTIVE' and states['account_data']=='AVAILABLE';return body
def wait(container,version):
 start=time.monotonic()
 while True:
  try:
   h=health(container);assert h['version']==version;return h
  except Exception:assert inspect(container)['State']['Running'] and time.monotonic()-start<180;time.sleep(3)
baseline=wait(names[0],'1.8.3');(A/'health-before.json').write_text(json.dumps(baseline));run(['docker','stop','-t','15',*names],'snapshot-stop',90)
try:run(['cp','-a',str(data),str(A/'before-data')],'consistent-cache-copy');run(['cp','-a',str(A/'before-data'),str(A/'pilot-data')],'pilot-cache-copy')
finally:run(['docker','start',*names],'resume-original',90);wait(names[0],'1.8.3')
for n,d,candidate in zip(clones,old,candidates):
 env=A/(n+'.env');env.write_text('\n'.join(d['Config']['Env'])+'\n');args=['docker','run','-d','--name',n,'--label','cody.connect-proof=true','--network',network,'--memory','384m','--env-file',str(env),'-v',str(credentials)+':/home/opuser/.op/1password-credentials.json:ro','-v',str(A/'pilot-data')+':/home/opuser/.op/data',candidate['imageId'],*(d['Config'].get('Cmd') or [])];run(args,'start-'+n)
try:
 h=wait(clones[0],'1.8.4');assert inspect(clones[1])['State']['Running'];d=inspect(clones[0]);ip=next(iter(d['NetworkSettings']['Networks'].values()))['IPAddress']
 try:urllib.request.urlopen('http://'+ip+':8080/v1/vaults',timeout=8);raise AssertionError('Unauthenticated access unexpectedly allowed')
 except urllib.error.HTTPError as e:assert e.code in [401,403]
 (A/'pilot.json').write_text(json.dumps({'passed':True,'version':'1.8.4','copiedAccountDataAvailable':True,'unauthenticatedAccessDenied':True,'outboundNetworkDisabled':True,'health':h},indent=2))
finally:
 for n in clones:
  with (A/(n+'.private.log')).open('w') as out:subprocess.run(['docker','logs',n],stdout=out,stderr=subprocess.STDOUT)
 run(['docker','stop','-t','10',*clones],'pilot-stop',90);run(['docker','rm',*clones],'pilot-remove')
assert compose.read_bytes()==original and all(inspect(n)['Id']==d['Id'] for n,d in zip(names,old));changed=False
try:
 run(['docker','stop','-t','15',*names],'activation-stop',90);changed=True;run(['cp','-a',str(data),str(A/'pre-activation-data')],'activation-cache-copy');text=original.decode();expected=json.loads(json.dumps(render))
 for d,service,candidate in zip(old,services,candidates):
  oldRef=render['services'][service]['image'];assert text.count(oldRef)==1 and oldRef==d['Config']['Image'];text=text.replace(oldRef,candidate['pinnedRef']);expected['services'][service]['image']=candidate['pinnedRef']
 compose.write_bytes(text.encode());after=json.loads(run(['docker','compose','-f',str(compose),'config','--format','json'],'config-after'));assert after==expected;run(['docker','compose','-f',str(compose),'up','-d','--no-deps',*services],'activate');h=wait(names[0],'1.8.4')
 for n,d,candidate in zip(names,old,candidates):
  new=inspect(n);assert new['Image']==candidate['imageId'] and new['State']['Running'];assert new['Mounts']==d['Mounts'] and new['HostConfig']['PortBindings']==d['HostConfig']['PortBindings']
 assert hashlib.sha256(credentials.read_bytes()).hexdigest()==credentialSha
 authenticated=False
 if (W/'connect-token.txt').exists():
  token=(W/'connect-token.txt').read_text().strip();assert not token.startswith('ops_')
  with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8080/v1/vaults',headers={'Authorization':'Bearer '+token}),timeout=30) as response:assert response.status==200;vaults=json.load(response)
  (A/'vaults-after.private.json').write_text(json.dumps(vaults));authenticated=True
 proof={'passed':True,'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':'1.8.4','apiImageId':candidates[0]['imageId'],'syncImageId':candidates[1]['imageId'],'pairRunning':True,'existingAccountDataAvailable':True,'credentialsSha256':credentialSha,'credentialsMountsPortsAndEnvironmentPreserved':True,'onlyComposeImagePinsChanged':True,'isolatedPairPilotPassed':True,'authenticatedCallerVaultReadPassed':authenticated,'baselineCallerState':'Existing service reports TOKEN_NEEDED/UNINITIALIZED; no configured Connect bearer token found. Existing op-token.txt is a service-account token and was never sent to Connect.','healthAfter':h,'rollbackCachePreserved':True};(A/'acceptance.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
except Exception:
 if changed:
  run(['docker','stop','-t','15',*names],'rollback-stop',90);assert data.resolve()==data and not (A/'failed-data').exists();data.rename(A/'failed-data');run(['cp','-a',str(A/'pre-activation-data'),str(data)],'rollback-cache');compose.write_bytes(original);run(['docker','compose','-f',str(compose),'up','-d','--no-deps',*services],'rollback');wait(names[0],'1.8.3');(A/'rollback.json').write_text(json.dumps({'oldPairAndCacheRestored':True}))
 raise
