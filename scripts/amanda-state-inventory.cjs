const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const r=process.argv[2],c=JSON.parse(fs.readFileSync(r+'/config/openclaw.json'));
console.log(JSON.stringify({model:c.agents?.defaults?.model,authOrder:c.auth?.order,bootstrap:c.agents?.defaults?.bootstrapMaxChars,timeout:c.agents?.defaults?.timeoutSeconds,memory:c.plugins?.slots,plugins:Object.keys(c.plugins?.entries??{}),channels:Object.keys(c.channels??{})}));
for(const f of ['workspace/post-start.sh','workspace/runtime-repair-20260927/preserve-amanda-runtime-9-8.py']){
 const s=fs.readFileSync(path.join(r,f),'utf8');
 console.log(JSON.stringify({file:f,sha256:crypto.createHash('sha256').update(s).digest('hex'),repairLines:s.split('\n').filter(l=>/runtime-repair|preserve-amanda|apply\.py|version.*2026|active_work_no_elapsed_cutoff/.test(l))}));
}
