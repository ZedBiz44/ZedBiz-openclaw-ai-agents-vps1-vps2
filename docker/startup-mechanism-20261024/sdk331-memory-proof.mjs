import fs from 'node:fs';
import assert from 'node:assert/strict';
import {Memory} from '/candidate/node_modules/mem0ai/dist/oss/index.mjs';
const raw=fs.readFileSync('/input/openclaw.json','utf8').replace(/\$\{([A-Z0-9_]+)\}/g,(m,k)=>{assert(process.env[k],'Missing existing runtime environment');return process.env[k]});
const plugin=JSON.parse(raw).plugins.entries['openclaw-mem0'].config;
const cfg=structuredClone(plugin.oss),originalModel=cfg.llm.config.model;
assert(cfg.disableHistory===true,'Preserve existing disabled history policy');
cfg.vectorStore.config={...cfg.vectorStore.config,host:'cody-sdk-pilot-qdrant',port:6333,collectionName:'cody_startup_sdk_20261024'};
delete cfg.vectorStore.config.url;delete cfg.vectorStore.config.apiKey;
const user='cody-sdk331-'+Date.now(),calls=[];
const report={sdk:'3.3.1',configuredModel:originalModel,isolatedQdrant:true,modelUnchanged:true,calls};
try{
 const m=new Memory(cfg);
 if(m.llm?.openai?.chat?.completions){const f=m.llm.openai.chat.completions.create.bind(m.llm.openai.chat.completions);m.llm.openai.chat.completions.create=async(...a)=>{const r=await f(...a);calls.push({requested:a[0].model,effective:r.model});return r;};}
 const added=await m.add('For fictional startup acceptance project Cedar-Ligament-024, the approved dispatch weekday is Thursday.',{userId:user,infer:true});
 const rows=added.results??added;assert(Array.isArray(rows)&&rows.length,'No inferred memory saved');report.savedCount=rows.length;
 const recalled=await m.search('What weekday is Cedar-Ligament-024 dispatched?',{filters:{user_id:user},topK:5,threshold:0});assert(JSON.stringify(recalled).includes('Thursday'),'Recall failed');report.recall=true;
 const fresh=new Memory(cfg);const persisted=await fresh.search('What is the dispatch weekday for Cedar-Ligament-024?',{filters:{user_id:user},topK:5,threshold:0});assert(JSON.stringify(persisted).includes('Thursday'),'Fresh-instance recall failed');report.freshInstanceRecall=true;
 const all=await fresh.getAll({filters:{user_id:user}});for(const x of (all.results??all))await fresh.delete(x.id);
 const left=await fresh.getAll({filters:{user_id:user}});assert((left.results??left).length===0);report.testMemoryRemoved=true;report.passed=true;
}catch(e){report.passed=false;report.errorName=e.name;fs.writeFileSync('/diagnostic/sdk-memory-error.private.txt',e.stack??String(e),{mode:0o600});process.exitCode=1;}
fs.writeFileSync('/diagnostic/sdk-memory-proof.json',JSON.stringify(report,null,2),{mode:0o600});console.log(JSON.stringify(report));
process.exit(process.exitCode??0);

