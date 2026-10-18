const fs=require('node:fs');
const p='/home/node/.openclaw/openclaw.json',b=p+'.stage-proof-backup';
if(process.argv[2]==='prepare'){
 if(fs.existsSync(b))throw Error('Prior proof backup exists; review before retry');
 fs.copyFileSync(p,b);fs.chmodSync(b,0o600);
 const c=JSON.parse(fs.readFileSync(p));
 c.agents.defaults.model.fallbacks=[];
 fs.writeFileSync(p,JSON.stringify(c,null,2)+'\n');
 console.log('Only restored-state fallback chain disabled for proof');
}else if(process.argv[2]==='restore'){
 fs.renameSync(b,p);console.log('Restored-stage configuration restored');
}else throw Error('Expected prepare or restore');
