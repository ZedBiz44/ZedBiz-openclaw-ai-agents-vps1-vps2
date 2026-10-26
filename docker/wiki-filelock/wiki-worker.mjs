import fs from 'node:fs/promises';
const wiki=await import('/app/dist/presentation-o87G5CIh.mjs');
const [vault,id]=process.argv.slice(2);
const entries=new Map();
const state=await import('/app/dist/import-runs-state-DSBgItyn.mjs');
const stores=new Map();
const openStore=({namespace})=>{
 if(!stores.has(namespace)) stores.set(namespace,new Map());
 const map=stores.get(namespace);
 return {async register(key,value){map.set(key,{key,value});},async lookup(key){return map.get(key);},
 async entries(){return [...map.values()];},async delete(key){return map.delete(key);},async count(){return map.size;}};
};
state.s(state.c(openStore));state.n(state.r(openStore));
wiki.M(wiki.N(()=>({
 async register(key,bytes,metadata){entries.set(key,{key,bytes,metadata});},
 async lookup(key){return entries.get(key);},
 async entries(){return [...entries.values()];},
 async delete(key){return entries.delete(key);}
})));
const config={vaultMode:'isolated',vault:{scope:'global',path:vault,renderMode:'native'},
 obsidian:{enabled:false,useOfficialCli:false,openAfterWrites:false},bridge:{enabled:false},
 unsafeLocal:{allowPrivateMemoryCoreAccess:false,paths:[]},ingest:{autoCompile:true,maxConcurrentJobs:1,allowUrlIngest:false},
 search:{backend:'local',corpus:'wiki'},context:{includeCompiledDigestPrompt:false},
 render:{preserveHumanBlocks:true,createBacklinks:true,createDashboards:true}};
if(id==='seed'){await wiki.T(config);console.log('SEEDED');process.exit(0);}
try{
 for(let i=0;i<3;i++){
  const source='/fixture/input-'+id+'-'+i+'.md';
  await fs.writeFile(source,'# Synthetic diagnosis '+id+' '+i+'\nTest-only evidence. No production data.');
  const ingested=await wiki.m({config,inputPath:source,title:'Diagnosis '+id+' '+i});
  const compiled=await wiki._(config);
  const lint=await wiki.p(config);
  console.log(JSON.stringify({id,i,ingested:ingested.pagePath,compiled:compiled.updatedFiles.length,lint:lint.issueCount}));
 }
}catch(e){console.error(e.stack);process.exitCode=2;}

