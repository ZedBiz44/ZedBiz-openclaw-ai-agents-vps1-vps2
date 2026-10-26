import fs from 'node:fs';
const path=process.env.CODY_CONFIG_PATH??'/home/node/.openclaw/openclaw.json';
const raw=fs.readFileSync(path,'utf8').replace(/\$\{([A-Z0-9_]+)\}/g,(m,k)=>process.env[k]??m);
const c=JSON.parse(raw),slot=c.plugins.slots.memory,tool=slot==='openclaw-mem0'?'mem0_search':'hindsight_recall';
const token=c.gateway.auth?.token??process.env.OPENCLAW_GATEWAY_TOKEN;
const response=await fetch('http://127.0.0.1:'+c.gateway.port+'/tools/invoke',{method:'POST',headers:{'Content-Type':'application/json',Authorization:'Bearer '+token},body:JSON.stringify({tool,args:{query:'ZedBiz',limit:3},sessionKey:'agent:main:main'}),signal:AbortSignal.timeout(90000)});
const body=await response.json();
// The caller stores this response privately and publishes only counts and status.
console.log(JSON.stringify({status:response.status,provider:slot,tool,body}));
