import subprocess,pathlib,json,sys,os,re,time,hashlib,urllib.request
base=pathlib.Path('/opt/openclaw/builds/vps1-complete-20261003')
targets={
 'hindsight-db':('pgvector/pgvector:pg18',['/var/lib/docker/volumes/hindsight-pg18-data/_data'],5432,''),
 'hindsight':('zedbiz/hindsight:0.10.2-flashrank-20261003',[],8888,'/health'),
 'mem0-dev-qdrant-1':('qdrant/qdrant:v1.19.1',['/var/lib/docker/volumes/mem0-dev_qdrant_storage/_data'],6333,'/collections'),
 'caddy':('caddy:2',['/opt/caddy/Caddyfile','/opt/caddy/data','/opt/caddy/config'],2019,'/config/'),
 'uptime-kuma':('louislam/uptime-kuma:2.5.5',['/opt/uptime-kuma/data'],3001,'/'),
 'portainer':('portainer/portainer-ce:2.45.1',['/opt/portainer/data'],9000,'/api/status'),
 'dozzle':('amir20/dozzle:v11.2.0',[],8080,'/'),
 'homepage':('ghcr.io/gethomepage/homepage:v2.4.0',['/opt/homepage/config','/opt/homepage/icons'],3000,'/'),
 'docker-socket-proxy':('tecnativa/docker-socket-proxy:v0.5.0',[],2375,'/_ping'),
 'filebrowser':('filebrowser/filebrowser:v2.63.23',['/opt/filebrowser/.filebrowser.json','/opt/filebrowser/filebrowser.db'],80,'/'),
}
name=sys.argv[1];image,paths,port,url=targets[name]
def run(args,**kw):return subprocess.run(args,check=True,**kw)
c=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
labels=c['Config']['Labels'];compose=pathlib.Path(labels['com.docker.compose.project.config_files']);service=labels['com.docker.compose.service']
w=base/('service-'+name);w.mkdir(mode=0o700,exist_ok=True);assert not (w/'activation.log').exists(),'Activation already attempted; inspect first'
text=compose.read_text();(w/'compose-before.yml').write_text(text);os.chmod(w/'compose-before.yml',0o600)
(w/'previous-image.txt').write_text(c['Config']['Image']+'\n'+c['Image'])
new=json.loads(subprocess.check_output(['docker','image','inspect',image]))[0]
pin=new['RepoDigests'][0] if new.get('RepoDigests') else image
pattern=r'(?m)^(\s*image:\s*)([\x27\"]?)'+re.escape(c['Config']['Image'])+r'\2\s*$'
if text.lstrip().startswith('{'):
 doc=json.loads(text);assert doc['services'][service]['image']==c['Config']['Image'];doc['services'][service]['image']=pin;updated=json.dumps(doc,indent=2)+'\n'
else:
 updated,count=re.subn(pattern,lambda m:m[1]+pin,text);assert count==1,'Nonunique image replacement'
(w/'compose-after.yml').write_text(updated);os.chmod(w/'compose-after.yml',0o600)
run(['docker','stop','-t','60',name],stdout=subprocess.DEVNULL)
try:
 if name=='hindsight':
  dockerfile=compose.parent/'Dockerfile';(w/'Dockerfile.before').write_text(dockerfile.read_text());dockerfile.write_text((base/'Dockerfile.hindsight').read_text())
  db=json.loads(subprocess.check_output(['docker','inspect','hindsight-db']))[0]
  ev=dict(x.split('=',1) for x in db['Config']['Env'])
  with (w/'hindsight-database.dump').open('wb') as f:run(['docker','exec','hindsight-db','pg_dump','-U',ev.get('POSTGRES_USER','postgres'),'-d',ev.get('POSTGRES_DB','postgres'),'-Fc'],stdout=f)
  os.chmod(w/'hindsight-database.dump',0o600)
  with (w/'hindsight-database.dump').open('rb') as f:run(['docker','exec','-i','hindsight-db','pg_restore','--list'],stdin=f,stdout=(w/'database-restore-list.txt').open('w'))
 for i,p in enumerate(paths):
  source=pathlib.Path(p);archive=f'data-{i}.tar'
  run(['docker','run','--rm','-v',str(source.parent)+':/source:ro','-v',str(w)+':/backup','alpine:3.22','sh','-c','umask 077; tar -cf /backup/'+archive+' -C /source '+source.name+' && chown 1001:1001 /backup/'+archive])
  h=hashlib.sha256()
  with (w/archive).open('rb') as f:
   for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
  (w/(archive+'.sha256')).write_text(h.hexdigest()+'  '+archive+'\n')
 run(['docker','run','--rm','-v',str(compose.parent)+':/target','-v',str(w)+':/backup:ro','alpine:3.22','sh','-c','cat /backup/compose-after.yml > /target/'+compose.name])
 with (w/'activation.log').open('w') as log:run(['docker','compose','-p',labels['com.docker.compose.project'],'-f',str(compose),'up','-d','--no-deps',service],stdout=log,stderr=subprocess.STDOUT)
except Exception:
 run(['docker','start',name],stdout=subprocess.DEVNULL);raise
healthy=False
for attempt in range(2400 if name=='uptime-kuma' else 200 if name=='hindsight' else 60):
 c2=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 ips=[x['IPAddress'] for x in c2['NetworkSettings']['Networks'].values() if x['IPAddress']]
 if name=='hindsight-db':
  p=subprocess.run(['docker','exec',name,'pg_isready'],capture_output=True)
  if p.returncode==0:healthy=True;break
 if name=='caddy':
  p=subprocess.run(['docker','exec',name,'wget','-q','-O','/dev/null','http://127.0.0.1:2019/config/'],capture_output=True)
  if p.returncode==0:healthy=True;break
 for ip in ips:
  try:
   headers={'Host':'localhost'}
   if name=='mem0-dev-qdrant-1':
    env=dict(x.split('=',1) for x in c2['Config']['Env'])
    if env.get('QDRANT__SERVICE__API_KEY'):headers['api-key']=env['QDRANT__SERVICE__API_KEY']
   req=urllib.request.Request(f'http://{ip}:{port}{url}',headers=headers)
   with urllib.request.urlopen(req,timeout=3) as r:body=r.read(1000);status=r.status
   if status==200:healthy=True;break
  except Exception:pass
 if healthy:break
 time.sleep(3)
r={'service':name,'oldImage':c['Config']['Image'],'oldImageId':c['Image'],'newImage':pin,'newImageId':c2['Image'],'running':c2['State']['Running'],'httpHealthy':healthy,'backup':str(w)}
(w/'verification.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
assert healthy,'Service did not pass HTTP check; inspect before proceeding'
