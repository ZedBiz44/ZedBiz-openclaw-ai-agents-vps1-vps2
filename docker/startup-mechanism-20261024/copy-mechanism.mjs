import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const root='/diagnostic/micro-'+process.env.CODY_VARIANT+'-'+Date.now();
fs.mkdirSync(root,{recursive:true});
const source=root+'/source/a/b/c/d/e/f',target=root+'/target/a/b/c/d/e/f';
fs.mkdirSync(source,{recursive:true});fs.mkdirSync(target,{recursive:true});
const counts={},top=new Map();let measuring=false;
for(const k of ['lstatSync','realpathSync','statSync','fstatSync','openSync','readSync','copyFileSync']){
 const original=fs[k];const wrapped=function(...args){if(measuring){counts[k]=(counts[k]??0)+1;if(k==='lstatSync'&&typeof args[0]==='string')top.set(args[0],(top.get(args[0])??0)+1);}return original.apply(this,args)};
 Object.assign(wrapped,original);fs[k]=wrapped;
}
const {I:copy}=await import('/app/dist/plugin-generation-source-lookup-CDeIIp1I.mjs');
const require=createRequire('/app/package.json');
const {createRootFileCopyBatchSync}=await import(pathToFileURL(require.resolve('@openclaw/fs-safe/advanced')).href);
const content=Buffer.from('small source bytes '.repeat(200));const N=160;
for(let i=0;i<N;i++)fs.writeFileSync(source+'/'+i+'.js',content);
const b=createRootFileCopyBatchSync();let elapsed;
try{
 measuring=true;const start=performance.now();
 for(let i=0;i<N;i++)copy(source+'/'+i+'.js',source,target+'/'+i+'.js',{hashCopiedContent:true,copyFile:b.copyFile.bind(b)});
 elapsed=performance.now()-start;measuring=false;
}finally{measuring=false;b[Symbol.dispose]();}
let verified=true;
for(let i=0;i<N;i++)verified&&=fs.readFileSync(target+'/'+i+'.js').equals(content);
const guards=[];
const check=(name,fn)=>{let rejected=false;try{fn()}catch{rejected=true}guards.push({name,rejected});};
fs.writeFileSync(root+'/outside.js','outside');fs.symlinkSync(root+'/outside.js',source+'/escape.js');
check('source-symlink-escape',()=>copy(source+'/escape.js',source,target+'/escape.js',{hashCopiedContent:true}));
fs.writeFileSync(source+'/swap.js','pinned');
const oldOpen=fs.openSync;let armed=true;
fs.openSync=function(...args){const fd=oldOpen.apply(this,args);if(armed&&String(args[0])===source+'/swap.js'){armed=false;fs.renameSync(source+'/swap.js',source+'/old.js');fs.writeFileSync(source+'/swap.js','replacement');}return fd;};
const guardBatch=createRootFileCopyBatchSync();
try{check('source-replaced-during-open',()=>copy(source+'/swap.js',source,target+'/swap.js',{hashCopiedContent:true,copyFile:guardBatch.copyFile.bind(guardBatch)}));}finally{fs.openSync=oldOpen;guardBatch[Symbol.dispose]();}
const result={variant:process.env.CODY_VARIANT,files:N,bytesEach:content.length,elapsedMs:elapsed,counts,mostRepeatedLstats:[...top].sort((a,b)=>b[1]-a[1]).slice(0,12).map(([p,n])=>({path:p.replace(root,'[fixture]'),calls:n})),bytesVerified:verified,guards};
fs.writeFileSync('/diagnostic/micro-'+process.env.CODY_VARIANT+'.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
if(!verified||guards.some(x=>!x.rejected))process.exitCode=1;

