import fs from 'node:fs';
import assert from 'node:assert/strict';
import {Memory} from '/root/.openclaw-harry/npm/projects/mem0-openclaw-mem0-09729737ad__openclaw-generation__g-1e5cd6aa3ff70dae/node_modules/mem0ai/dist/oss/index.mjs';
const base='/root/cody-harry-mem0-20261024';
const raw=fs.readFileSync('/root/.openclaw-harry/openclaw.json','utf8').replace(/\$\{([A-Z0-9_]+)\}/g,(m,k)=>{assert(process.env[k],'Missing environment variable');return process.env[k]});
const cfg=JSON.parse(raw).plugins.entries['openclaw-mem0'].config;
const config=structuredClone(cfg.oss);config.llm.config.model='gpt-6-luna';config.customInstructions=cfg.customInstructions;
const user='cody-harry-luna-pilot-20261024';
const m=new Memory(config); const calls=[];
const original=m.llm.openai.chat.completions.create.bind(m.llm.openai.chat.completions);
m.llm.openai.chat.completions.create=async (...args)=>{const start=Date.now();const r=await original(...args);calls.push({requested:args[0].model,effective:r.model,ms:Date.now()-start,usage:r.usage});return r;};
const report={model:'gpt-6-luna',user,calls};
try{
 const a=await m.add('For synthetic acceptance project Cedar-Pilot-484, the approved dispatch weekday is Tuesday.',{userId:user,infer:true});report.add=a;
 assert(a.results.length>0,'No inferred memory');
 const s=await m.search('When is Cedar-Pilot-484 dispatched?',{filters:{user_id:user},topK:5,threshold:0});report.recall=s;
 assert(JSON.stringify(s).includes('Tuesday'),'Initial recall failed');
 const u=await m.add('Correction: for Cedar-Pilot-484 the dispatch weekday is now Thursday, replacing Tuesday.',{userId:user,infer:true});report.update=u;
 const s2=await m.search('What is the current dispatch weekday for Cedar-Pilot-484?',{filters:{user_id:user},topK:5,threshold:0});report.updatedRecall=s2;
 assert(JSON.stringify(s2).includes('Thursday'),'Updated recall failed');
 assert(calls.length>=2 && calls.every(c=>c.requested==='gpt-6-luna' && c.effective.startsWith('gpt-6-luna')),'Wrong LLM');report.passed=true;
}catch(e){report.error={name:e.name,message:e.message};process.exitCode=1;}
finally{
 const all=await m.getAll({filters:{user_id:user}});report.cleanupIds=(all.results||all).map(x=>x.id);
 for(const id of report.cleanupIds){const item=await m.get(id);assert(JSON.stringify(item).includes(user),'Test ownership missing');await m.delete(id);}
 const remaining=await m.getAll({filters:{user_id:user}});report.cleaned=(remaining.results||remaining).length===0;assert(report.cleaned);
 fs.writeFileSync(base+'/pilot-result.json',JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}
