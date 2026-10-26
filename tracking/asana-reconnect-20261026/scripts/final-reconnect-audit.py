import importlib.util,json,subprocess,base64,concurrent.futures,datetime
from pathlib import Path
spec=importlib.util.spec_from_file_location('native','/home/ubuntu/rollout-native-reconnect.py');native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
manifest=json.load(open('/home/ubuntu/reconnect-private-proof.json'))['patch-manifest.json']
containers=['amanda','wilma','victor','terry','marsha','edith','vivian','gohzed','grogar','inga','maggie']
code1="import json,subprocess\nrows=[]\nmanifest="+repr(manifest)+"\nfor a in "+repr(containers)+":\n x=json.loads(subprocess.check_output(['docker','inspect',a],text=True))[0]\n js=\"const fs=require('fs'),h=require('crypto');console.log(JSON.stringify({version:JSON.parse(fs.readFileSync('/app/package.json')).version,node:process.version,files:\"+json.dumps(manifest)+\".map(x=>({path:x.path,sha256:h.createHash('sha256').update(fs.readFileSync(x.path)).digest('hex')}))}));\"\n y=json.loads(subprocess.check_output(['docker','exec',a,'node','-e',js],text=True));rows.append({'server':'vps1','agent':a,'version':y['version'],'node':y['node'],'repairHashesMatch':all(f['sha256']==m['patchedSha256'] for f,m in zip(y['files'],manifest)),'running':x['State']['Running'],'health':x['State'].get('Health',{}).get('Status'),'crashRestarts':x['RestartCount'],'oom':x['State']['OOMKilled']})\nprint('AUDIT_BEGIN');print(json.dumps(rows));print('AUDIT_END')\n"
def remote(server,code):
 p=subprocess.run(['vps-access','-ssh','access',server],input="python3 - <<'PY'\n"+code+'\nPY\nexit\n',capture_output=True,text=True,timeout=180);assert p.returncode==0,p.stderr[-500:];return json.loads(p.stdout.split('AUDIT_BEGIN\n',1)[1].split('\nAUDIT_END',1)[0])
def audit_native(server,names):
 rows=[]
 for a in names:
  _,root,state=native.ROOTS[a];candidate=Path('/home/ubuntu/reconnect-native-prep/candidate/'+server+'/'+a+'/dist/agents/agent-bundle-mcp-runtime.js').read_bytes()
  code=native.REMOTE.split('old=p.read_bytes()',1)[0]+"\nh=rpc('health',{});x=props();print('AUDIT_BEGIN');print(json.dumps([{'server':SERVER,'agent':a,'version':json.loads((root/'package.json').read_text())['version'],'node':subprocess.check_output(['node','--version'],text=True).strip(),'repairHashesMatch':sh(p.read_bytes())==expectedNew,'running':x['ActiveState']=='active' and x['SubState']=='running','healthOk':h.get('ok') is True,'eventLoopDegraded':h.get('eventLoop',{}).get('degraded'),'automaticRestarts':x['NRestarts']}])) ;print('AUDIT_END')\n"
  code=code.replace('AGENT',repr(a)).replace('ROOTPATH',repr(root)).replace('STATEPATH',repr(state)).replace('SERVER',repr(server)).replace('CANDIDATE64',repr(base64.b64encode(candidate).decode()));rows.extend(remote(server,code))
 return rows
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 futures=[pool.submit(remote,'vps1',code1),pool.submit(audit_native,'vps2',['frank','harry','suzy']),pool.submit(audit_native,'vps4',['rocky'])];rows=[r for f in futures for r in f.result()]
result={'capturedUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'agents':rows,'scope':'Read-only final runtime/hash/health inventory; not future scheduled acceptance; Rocky actual memory read remains unverified.'};Path('/home/ubuntu/asana-reconnect-final-runtime-audit.json').write_text(json.dumps(result,indent=2)+'\n')
assert len(rows)==15 and all(r['repairHashesMatch'] and r['running'] and r['version']=='2026.10.6' and r['node']=='v24.22.1' for r in rows)
assert all(r.get('health')=='healthy' if r['server']=='vps1' else r['healthOk'] and not r['eventLoopDegraded'] for r in rows)
for r in rows:print(r['server'],r['agent'],'repaired; version preserved; healthy',flush=True)
