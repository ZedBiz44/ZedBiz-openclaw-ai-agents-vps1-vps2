import subprocess,json,pathlib
b=pathlib.Path('/opt/openclaw/builds/vps1-email-20261003');out=[]
for n in ['terry','edith']:
 code="""const fs=require('fs'),p='/home/node/.openclaw/npm/projects';for(const d of fs.readdirSync(p)){const root=p+'/'+d+'/node_modules/';try{const a=require(root+'@mem0/openclaw-mem0/package.json');if(a.version!=='1.2.1')continue;const sdk=require(root+'mem0ai/package.json'),client=require(root+'@qdrant/js-client-rest/package.json');const files=fs.readdirSync(root+'mem0ai/dist');console.log(JSON.stringify({plugin:a.version,sdk:sdk.version,sdkQdrantDependency:sdk.dependencies['@qdrant/js-client-rest'],client:client.version,root,files}));}catch{}}"""
 j=json.loads(subprocess.check_output(['docker','exec',n,'node','-e',code]));root=j.pop('root');j.pop('files',None)
 p=subprocess.run(['docker','exec',n,'grep','-R','-l','this.client.search(',root+'mem0ai/dist'],capture_output=True,text=True)
 j.update({'agent':n,'sdkUsesLegacySearch':bool(p.stdout),'latestPlugin':subprocess.check_output(['docker','exec',n,'npm','view','@mem0/openclaw-mem0','version'],text=True).strip(),'latestSdk':subprocess.check_output(['docker','exec',n,'npm','view','mem0ai','version'],text=True).strip(),'latestClient':subprocess.check_output(['docker','exec',n,'npm','view','@qdrant/js-client-rest','version'],text=True).strip()});out.append(j)
(b/'mem0-client-review.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
