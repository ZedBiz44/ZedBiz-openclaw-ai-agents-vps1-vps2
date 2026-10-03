// Run inside one authorized agent. Marsha is explicitly excluded by the host runner.
import fs from 'node:fs';
const p='/home/node/.openclaw/openclaw.json';
const raw=fs.readFileSync(p,'utf8');
const c=JSON.parse(raw);const d=c.agents.defaults;
const key='openai/gpt-6.1-sol';
const selected=key+'@openai:api-key-backup';
const backup=p+'.before-sol-fleet-20261003';
if (!fs.existsSync(backup))fs.writeFileSync(backup,raw,{mode:0o600});
d.models??={};d.models[key]={...(d.models[key]||{}),agentRuntime:{id:'codex'}};
if (Array.isArray(d.modelPolicy?.allow) && !d.modelPolicy.allow.includes(key))d.modelPolicy.allow.push(key);
if (typeof d.model==='string')d.model=selected;else d.model.primary=selected;
const main=c.agents.entries?.main || c.agents.list?.find(x=>x.id==='main');
if (main?.model) {if(typeof main.model==='string')main.model=selected;else main.model.primary=selected;}
fs.writeFileSync(p+'.sol-tmp',JSON.stringify(c,null,2)+'\n',{mode:0o600});fs.renameSync(p+'.sol-tmp',p);
console.log(JSON.stringify({primary:d.model,fallbacksPreserved:true,thinking:d.thinkingDefault}));
