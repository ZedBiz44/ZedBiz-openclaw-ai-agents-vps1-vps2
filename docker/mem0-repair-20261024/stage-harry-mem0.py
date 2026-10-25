"""Build a private lean Harry Mem0 project; no production writes."""
import pathlib,os,json,subprocess,hashlib,tarfile,re
P=pathlib.Path;os.umask(0o077);W=P('/root/cody-mem0-repair-20261024');W.mkdir(mode=0o700,exist_ok=True);project=W/'project';assert not project.exists();project.mkdir()
source=P('/root/cody-mem0-source-20261024.tar.gz')
with tarfile.open(source) as t:
 assert all(not p.name.startswith('/') and '..' not in P(p.name).parts and not p.issym() and not p.islnk() for p in t.getmembers());t.extractall(project,filter='data')
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
assert sha(project/'package-lock.json')=='e4180c3b5587246e6b6f04d4a3ec52c85432f00c87dc6d79ab2134601a9e519c'
assert sha(project/'vendor/mem0-openclaw-mem0-1.2.1.tgz')=='2cf14e3725c9913275d3a5a72db83f05462721f9ae4cb1ad05ad85b7ef70c941'
with (W/'npm-ci.private.log').open('w') as f:r=subprocess.run(['npm','ci'],cwd=project,stdout=f,stderr=subprocess.STDOUT,timeout=900)
assert r.returncode==0,'Clean build failed'
assert json.loads((project/'node_modules/mem0ai/package.json').read_text())['version']=='3.3.1'
assert sha(project/'node_modules/@mem0/openclaw-mem0/dist/index.js')=='0e7205db54c8790c1aff7b09786ec0b7578db08181b5394a7137df4e530297c2'
patches=[]
for name in ['index.js','index.mjs']:
 p=project/'node_modules/mem0ai/dist/oss'/name;before=sha(p);s=p.read_text();pattern=r'params\.port = parsedUrl\.port \? parseInt\(parsedUrl\.port(?:, 10)?\) : 6333;';matches=re.findall(pattern,s);assert len(matches)==1,'Unexpected HTTPS patch site'
 s=re.sub(pattern,'params.port = parsedUrl.port ? parseInt(parsedUrl.port, 10) : parsedUrl.protocol === "https:" ? 443 : 6333;',s);p.write_text(s);assert subprocess.run(['node','--check',str(p)],capture_output=True).returncode==0
 patches.append({'file':str(p.relative_to(project)),'before':before,'after':sha(p)})
(W/'https-patches.json').write_text(json.dumps(patches,indent=2))
peer=P('/opt/openclaw-harry/node_modules/openclaw/dist/plugin-peer-link-Cq6_4lfP.mjs');assert peer.is_file()
proof={'staged':True,'productionUnchanged':True,'sdk':'3.3.1','plugin':'1.2.1','httpsPortFixPreserved':True,'lockSha256':sha(project/'package-lock.json'),'peerModuleSha256':sha(peer),'files':sum(1 for p in project.rglob('*') if p.is_file()),'bytes':sum(p.stat().st_size for p in project.rglob('*') if p.is_file())}
(W/'stage.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))

