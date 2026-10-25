"""Isolated API experiment only. Does not mount production state or change installed packages."""
import pathlib, subprocess, json, os, shutil
P=pathlib.Path; os.umask(0o077)
W=P('/opt/openclaw/backups/startup-mechanism-20261024/linux-read-batch');W.mkdir(exist_ok=True,mode=0o700)
def run(args): return subprocess.run(args,capture_output=True,text=True)
def obj(name):
 r=run(['docker','inspect','--type','container',name]);assert r.returncode==0;return json.loads(r.stdout)[0]
def identity(name):
 d=obj(name);return [d['Id'],d['State']['Pid'],d['Image'],d['RestartCount']]
before={n:identity(n) for n in ['marsha','terry']}
source=W.parent/'fs-safe-0.26.13/package';candidate=W/'package'
if not candidate.exists():shutil.copytree(source,candidate)
f=candidate/'dist/root-file-open-batch-sync.js';code=(source/'dist/root-file-open-batch-sync.js').read_text()
needle='function canRetainRoot(params) {'
assert code.count(needle)==1
code=code.replace(needle,needle+'''
    // Linux experiment: direct children only; nested paths keep original admission.
    if (process.platform === "linux") return typeof params.rootPath === "string" &&
        typeof params.absolutePath === "string" && params.ioFs === undefined &&
        params.rootRealPath === undefined && !params.skipLexicalRootCheck &&
        (params.symlinks === "reject" || (params.symlinks === undefined && params.rejectSymlinks !== false)) &&
        !params.rootPath.includes("\\0") && !params.absolutePath.includes("\\0") &&
        path.isAbsolute(params.rootPath) && path.resolve(params.rootPath) === params.rootPath &&
        path.resolve(params.absolutePath) === params.absolutePath &&
        path.dirname(params.absolutePath) === params.rootPath && params.absolutePath !== params.rootPath;
''');f.write_text(code)
js=r'''
import fs from 'node:fs';
import {createRootFileOpenBatchSync,openRootFileSync} from '/candidate/dist/advanced.js';
const root='/tmp/batch-proof';fs.mkdirSync(root,{recursive:true});
const content=Buffer.from('test source '.repeat(300));for(let i=0;i<160;i++)fs.writeFileSync(root+'/'+i+'.js',content);
const results=[];
for(const mode of ['one-shot','retained-root','retained-root','one-shot']){
 const batch=createRootFileOpenBatchSync();let correct=true;const start=performance.now();
 try{for(let round=0;round<5;round++)for(let i=0;i<160;i++){
  const p={rootPath:root,absolutePath:root+'/'+i+'.js'};
  const r=mode==='one-shot'?openRootFileSync(p):batch.openFile(p);
  if(!r.ok)throw r.error;try{correct&&=fs.readFileSync(r.fd).equals(content)}finally{fs.closeSync(r.fd)}
 }}finally{batch.close()}
 results.push({mode,reads:800,elapsedMs:performance.now()-start,bytesVerified:correct});
}
const guards=[];
function rejected(name,params,setup){const b=createRootFileOpenBatchSync();try{
 if(setup)setup(b);const r=b.openFile(params);if(r.ok)fs.closeSync(r.fd);
 guards.push({name,rejected:!r.ok});
}finally{b.close()}}
fs.writeFileSync('/tmp/outside-source','outside');fs.symlinkSync('/tmp/outside-source',root+'/leaf-link');
rejected('leaf-symlink',{rootPath:root,absolutePath:root+'/leaf-link'});
fs.mkdirSync(root+'/actual');fs.writeFileSync(root+'/actual/inside','inside');fs.symlinkSync('actual',root+'/parent-link');
rejected('internal-parent-symlink',{rootPath:root,absolutePath:root+'/parent-link/inside'});
fs.symlinkSync('/tmp',root+'/escape-parent');
rejected('outside-parent-symlink',{rootPath:root,absolutePath:root+'/escape-parent/outside-source'});
fs.linkSync(root+'/0.js',root+'/hard');
rejected('hardlink',{rootPath:root,absolutePath:root+'/hard',rejectHardlinks:true});
rejected('size-limit',{rootPath:root,absolutePath:root+'/1.js',maxBytes:3});
rejected('outside-root',{rootPath:root,absolutePath:'/tmp/outside-source'});
const swap='/tmp/swap-root';fs.mkdirSync(swap);fs.writeFileSync(swap+'/a','original');
rejected('root-replaced-between-reads',{rootPath:swap,absolutePath:swap+'/a'},b=>{
 const r=b.openFile({rootPath:swap,absolutePath:swap+'/a'});if(!r.ok)throw r.error;fs.closeSync(r.fd);
 fs.renameSync(swap,swap+'-old');fs.mkdirSync(swap);fs.writeFileSync(swap+'/a','replacement');
});
const out={scope:'API only; direct-child Linux experiment; no OpenClaw integration or production patch',results,guards};
console.log(JSON.stringify(out));if(results.some(r=>!r.bytesVerified)||guards.some(g=>!g.rejected))process.exitCode=1;
'''
(W/'proof.mjs').write_text(js)
os.chown(W/'proof.mjs',1000,1000)
for parent,dirs,files in os.walk(candidate):
 os.chown(parent,1000,1000)
 for filename in files:os.chown(P(parent)/filename,1000,1000)
name='cody-linux-read-batch-proof';assert run(['docker','inspect','--type','container',name]).returncode!=0
r=run(['docker','run','--rm','--name',name,'--label','cody.startup-mechanism-fixture=true','--network','none','--memory','512m','--memory-swap','512m','--cpus','1','--user','node','--entrypoint','node','-v',str(candidate)+':/candidate:ro','-v',str(W/'proof.mjs')+':/proof.mjs:ro',obj('marsha')['Image'],'/proof.mjs'])
assert all(identity(n)==before[n] for n in before),'Production changed externally'
assert run(['docker','inspect','--type','container',name]).returncode!=0,'Fixture remains'
if r.returncode:print(r.stderr[:2500]);print(r.stdout[:5000]);raise SystemExit(r.returncode)
out=json.loads(r.stdout);out['productionUnchanged']=True;out['fixtureRemoved']=True
(W/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))

