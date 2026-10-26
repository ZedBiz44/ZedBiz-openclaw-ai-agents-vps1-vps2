import json,subprocess
from pathlib import Path
manifest=json.loads(Path('/home/ubuntu/reconnect-private-proof.json').read_text())['patch-manifest.json']
code=r'''
import pathlib,json,subprocess,hashlib,os,datetime
os.umask(0o077)
base=pathlib.Path('/home/jackadmin/manus-asana-reconnect-20261026');base.mkdir(mode=0o700,exist_ok=True)
manifest=MANIFEST
agents=['terry','marsha','edith','vivian','gohzed','grogar','inga','maggie']
def inspect(name):return json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
def sha(b):return hashlib.sha256(b).hexdigest()
testRoot=pathlib.Path('/home/jackadmin/victor-mcp-reconnect-20261026/v2/proof')
receipts=[]
for a in agents:
 print(a+': preparing exact-parent candidate',flush=True)
 before=inspect(a);parent=before['Config']['Image'];parentId=before['Image'];assert inspect(parent)['Id']==parentId,'Parent tag changed'
 root=base/a;root.mkdir(mode=0o700,exist_ok=True);receipt=root/'candidate-acceptance.json'
 if receipt.exists():
  saved=json.loads(receipt.read_text());assert saved['parentImageId']==parentId and inspect(saved['candidateImage'])['Id']==saved['candidateImageId'],'Saved candidate differs';receipts.append(saved);print(a+': existing verified candidate preserved',flush=True);continue
 image='zedbiz/'+a+':2026.10.6-mcp-reconnect-manus-20261026'
 existingImage=subprocess.run(['docker','image','inspect',image],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
 compose=pathlib.Path('/opt/openclaw/agents/'+a+'/docker-compose.yml');beforeBytes=compose.read_bytes();backup=root/'docker-compose.before.yml'
 if backup.exists():assert backup.read_bytes()==beforeBytes,'Original Compose backup changed; stop'
 else:backup.write_bytes(beforeBytes)
 for m in manifest:
  dest=root/'patched-dist'/m['path'].removeprefix('/app/dist/');dest.parent.mkdir(parents=True,exist_ok=True)
  subprocess.run(['docker','cp',a+':'+m['path'],str(dest)],check=True,stdout=subprocess.DEVNULL)
  b=dest.read_bytes();assert sha(b)==m['originalSha256'],'Original hash mismatch '+a+' '+m['path'];assert b.count(m['originalSnippet'].encode())==1
  b=b.replace(m['originalSnippet'].encode(),m['replacement'].encode());assert sha(b)==m['patchedSha256'];dest.write_bytes(b)
 (root/'patch-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 (root/'Dockerfile').write_text('FROM '+parent+'\nCOPY --chown=node:node patched-dist/ /app/dist/\n')
 proof=root/'proof';proof.mkdir(mode=0o755,exist_ok=True)
 proof.chmod(0o755)
 for p in testRoot.glob('*.mjs'):(proof/p.name).write_text(p.read_text());(proof/p.name).chmod(0o644)
 if not existingImage:
  with (root/'build-private.log').open('w') as f:r=subprocess.run(['docker','build','--pull=false','-t',image,'-f',str(root/'Dockerfile'),str(root)],stdout=f,stderr=subprocess.STDOUT)
  assert r.returncode==0,'Candidate build failed; review private log'
 else:print(a+': recovering existing image; no rebuild',flush=True)
 child=inspect(image);parentImage=inspect(parent);assert parentImage['Id']==parentId,'Parent changed during build'
 assert child['RootFS']['Layers'][:len(parentImage['RootFS']['Layers'])]==parentImage['RootFS']['Layers'],'Candidate ancestry mismatch'
 assert all(child['Config'].get(k)==parentImage['Config'].get(k) for k in ['Env','Cmd','Entrypoint','User','WorkingDir','Healthcheck','Volumes','ExposedPorts']),'Candidate settings altered'
 tests=[]
 for name,expected in [('regression-agents.mjs',7),('regression-worker.mjs',6)]:
  r=subprocess.run(['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--memory','1g','--tmpfs','/tmp:rw,nosuid,nodev,mode=1777','--entrypoint','node','-v',str(proof)+':/proof:ro',image,'/proof/'+name],capture_output=True,text=True,timeout=45)
  for suffix in ['stdout','stderr']:
   old=root/(name+'.'+suffix);saved=root/(name+'.initial.'+suffix)
   if old.exists() and not saved.exists():saved.write_bytes(old.read_bytes())
  (root/(name+'.stdout')).write_text(r.stdout);(root/(name+'.stderr')).write_text(r.stderr)
  assert r.returncode==0,'Isolated fixture failed '+a+' '+name
  d=json.loads(r.stdout);assert d['passed']==expected;tests.append({'name':name,'passed':expected,'network':'none','liveDataCredentialsAndChannels':False})
 js="const fs=require('fs'),c=require('crypto');const rows="+json.dumps(manifest)+";console.log(JSON.stringify(rows.map(x=>({path:x.path,sha256:c.createHash('sha256').update(fs.readFileSync(x.path)).digest('hex')}))))"
 r=subprocess.run(['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL','--memory','256m','--entrypoint','node',image,'-e',js],capture_output=True,text=True,timeout=30);assert r.returncode==0
 hashes=json.loads(r.stdout);assert all(x['sha256']==m['patchedSha256'] for x,m in zip(hashes,manifest))
 after=inspect(a);assert after['Id']==before['Id'] and after['State']['StartedAt']==before['State']['StartedAt'] and compose.read_bytes()==beforeBytes,'Live state changed during staging; inspect'
 saved={'agent':a,'capturedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parentImage':parent,'parentImageId':parentId,'candidateImage':image,'candidateImageId':child['Id'],'tests':tests,'allThreeCandidateImageHashesVerified':True,'imageSettingsUnchanged':True,'imageBaseLayersPreserved':True,'composeUnchanged':True,'liveContainerIdUnchanged':True,'liveStartedAtUnchanged':True,'originalContainerId':before['Id'],'deployed':False,'root':str(root)}
 receipt.write_text(json.dumps(saved,indent=2)+'\n');receipts.append(saved);print(a+': candidate passed isolated7+6 tests; live agent unchanged',flush=True)
(base/'staging-summary.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('STAGE_BEGIN');print(json.dumps(receipts));print('STAGE_END')
'''.replace('MANIFEST',repr(manifest))
p=subprocess.Popen(['vps-access','-ssh','access','vps1'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
p.stdin.write("python3 - <<'PY'\n"+code+'\nPY\nexit\n');p.stdin.close()
out=[]
for line in p.stdout:print(line,end='',flush=True);out.append(line)
rc=p.wait();text=''.join(out);Path('/home/ubuntu/vps1-reconnect-staging-output.txt').write_text(text)
if 'STAGE_BEGIN\n' in text:Path('/home/ubuntu/vps1-reconnect-staging-receipts.json').write_text(text.split('STAGE_BEGIN\n',1)[1].split('\nSTAGE_END',1)[0]+'\n')
raise SystemExit(rc)
