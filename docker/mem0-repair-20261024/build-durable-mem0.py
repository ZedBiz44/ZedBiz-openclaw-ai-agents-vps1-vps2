"""Build a reproducible customized Mem0 package in private staging, not live state."""
import pathlib,os,json,subprocess,shutil,hashlib,tarfile
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/mem0-repair-20261024');W.mkdir(exist_ok=True,mode=0o700)
src=P('/opt/openclaw/agents/terry/npm/projects/mem0-openclaw-mem0-09729737ad__openclaw-generation__g-1e5cd6aa3ff70dae/node_modules/@mem0/openclaw-mem0')
stage=W/'package-source';project=W/'project';verify=W/'reinstall-proof'
assert not project.exists() and not verify.exists(),'Inspect prior build before reusing work paths'
shutil.copytree(src,stage,ignore=shutil.ignore_patterns('*before-*','node_modules'))
meta=json.loads((stage/'package.json').read_text());assert meta['version']=='1.2.1' and meta['dependencies']['mem0ai']=='3.0.7'
meta['dependencies']['mem0ai']='3.3.1';meta.pop('devDependencies',None)
meta['zedbizBuild']={'revision':'mem0-1.2.1-sdk3.3.1-20261024','upstreamPluginVersion':'1.2.1','sdkVersion':'3.3.1','preserves':'explicit retention and unique mem0_search/mem0_get'}
(stage/'package.json').write_text(json.dumps(meta,indent=2)+'\n')
original=hashlib.sha256((src/'dist/index.js').read_bytes()).hexdigest();assert hashlib.sha256((stage/'dist/index.js').read_bytes()).hexdigest()==original
assert {'mem0_search','mem0_get'}<=set(json.loads((stage/'openclaw.plugin.json').read_text())['contracts']['tools'])
project.mkdir();(project/'vendor').mkdir()
for parent,dirs,files in os.walk(W):
 os.chown(parent,1000,1000)
 for name in files:os.chown(P(parent)/name,1000,1000)
image=json.loads(subprocess.check_output(['docker','image','inspect','zedbiz/openclaw-base:2026.10.6-tools-full-20261023']))[0]['Id']
def node(args,label,timeout=480):
 with (W/(label+'.private.log')).open('w') as log:
  result=subprocess.run(['docker','run','--rm','--label','cody.mem0-repair-build=true','--memory','2g','--memory-swap','2g','--cpus','2','--user','node','--entrypoint','sh','-v',str(W)+':/build','-e','HOME=/tmp',image,'-c',args],stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
 assert result.returncode==0,label+' failed; inspect private build log'
node('cd /build/package-source && npm pack --ignore-scripts --pack-destination /build/project/vendor','pack')
packed=next((project/'vendor').glob('*.tgz'))
manifest={'name':'zedbiz-mem0-managed-project','version':'2026.10.24','private':True,'dependencies':{'@mem0/openclaw-mem0':'file:vendor/'+packed.name,'@qdrant/js-client-rest':'1.18.0','better-sqlite3':'12.11.1'}}
(project/'package.json').write_text(json.dumps(manifest,indent=2)+'\n');(project/'.npmrc').write_text('legacy-peer-deps=true\nignore-scripts=true\naudit=false\nfund=false\n')
for f in [project/'package.json',project/'.npmrc']:os.chown(f,1000,1000)
node('cd /build/project && npm install --omit=dev --no-audit --no-fund','install')
verify.mkdir();os.chown(verify,1000,1000)
for name in ['package.json','package-lock.json','.npmrc']:shutil.copy2(project/name,verify/name);os.chown(verify/name,1000,1000)
shutil.copytree(project/'vendor',verify/'vendor')
for parent,dirs,files in os.walk(verify):
 os.chown(parent,1000,1000)
 for name in files:os.chown(P(parent)/name,1000,1000)
node('cd /build/reinstall-proof && npm ci --omit=dev --no-audit --no-fund','reinstall')
def digest(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
for base in [project,verify]:
 p=base/'node_modules/@mem0/openclaw-mem0';m=json.loads((p/'package.json').read_text());assert m['dependencies']['mem0ai']=='3.3.1';assert digest(p/'dist/index.js')==original
 assert json.loads((base/'node_modules/mem0ai/package.json').read_text())['version']=='3.3.1'
 assert json.loads((base/'node_modules/@qdrant/js-client-rest/package.json').read_text())['version']=='1.18.0'
 assert not any((base/'node_modules'/s).exists() for s in ['cloudflare','@azure/identity','@mistralai/mistralai'])
assert digest(project/'package-lock.json')==digest(verify/'package-lock.json')
audit=subprocess.run(['docker','run','--rm','--memory','1g','--user','node','--entrypoint','sh','-v',str(W)+':/build','-e','HOME=/tmp',image,'-c','cd /build/project && npm audit --omit=dev --json'],capture_output=True,text=True,timeout=120)
(W/'audit.json').write_text(audit.stdout);au=json.loads(audit.stdout);v=au.get('metadata',{}).get('vulnerabilities',{});assert v.get('critical',0)==0,'Critical dependency finding requires diagnosis'
count=total=0
for parent,dirs,files in os.walk(project/'node_modules'):
 for n in files:
  f=P(parent)/n
  if f.is_file():count+=1;total+=f.stat().st_size
result={'passed':True,'image':image,'pluginVersion':'1.2.1','sdkVersion':'3.3.1','qdrantClientVersion':'1.18.0','customPluginCodeSha256':original,'vendorPackage':packed.name,'vendorSha256':digest(packed),'lockSha256':digest(project/'package-lock.json'),'cleanNpmCiReproduced':True,'files':count,'bytes':total,'audit':v,'productionChanged':False}
(W/'build.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)

