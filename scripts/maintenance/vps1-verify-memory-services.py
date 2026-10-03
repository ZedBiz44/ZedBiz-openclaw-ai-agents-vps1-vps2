import subprocess,json,urllib.request,pathlib
b=pathlib.Path('/opt/openclaw/builds/vps1-complete-20261003');out=[]
for name,port,route in [('hindsight',8888,'/health'),('mem0-dev-qdrant-1',6333,'/collections')]:
 c=json.loads(subprocess.check_output(['docker','inspect',name]))[0];ip=next(x['IPAddress'] for x in c['NetworkSettings']['Networks'].values() if x['IPAddress'])
 env=dict(x.split('=',1) for x in c['Config']['Env']);headers={}
 if 'QDRANT__SERVICE__API_KEY' in env:headers['api-key']=env['QDRANT__SERVICE__API_KEY']
 def get(path):
  with urllib.request.urlopen(urllib.request.Request(f'http://{ip}:{port}'+path,headers=headers),timeout=20) as r:return json.load(r)
 j=get(route);r={'service':name,'image':c['Config']['Image'],'running':c['State']['Running'],'httpHealthy':True}
 if name=='hindsight':r['health']=j
 else:
  r['version']=get('/')['version'];r['collections']=[{'name':x['name'],'points':get('/collections/'+x['name'])['result']['points_count']} for x in j['result']['collections']]
 (b/('service-'+name)/'verification.json').write_text(json.dumps(r,indent=2));out.append(r)
print(json.dumps(out,indent=2))
