const fs=require('node:fs'),path=require('node:path');
const root=process.argv[2],p=path.join(root,'workspace/post-start.sh');
const old='python3 /home/node/.openclaw/workspace/runtime-repair-20260927/preserve-amanda-runtime-9-8.py || exit $?';
const replacement='node /opt/zedbiz/verify-amanda-runtime-10-4.cjs || exit $?';
const source=fs.readFileSync(p,'utf8');
if(source.includes(old)){
 if(source.split(old).length!==2)throw Error('Unexpected startup repair count');
 fs.copyFileSync(p,p+'.before-10.4');fs.writeFileSync(p,source.replace(old,replacement));
}else if(!source.includes(replacement))throw Error('Unexpected startup source');
const config=path.join(root,'config/openclaw.json'),c=JSON.parse(fs.readFileSync(config));
if(c.agents.defaults.timeoutSeconds!==0)throw Error('Unlimited work setting changed');
const chars=fs.readFileSync(path.join(root,'workspace/AGENTS.md'),'utf8').length+(fs.existsSync(path.join(root,'workspace/TOOLS.md'))?fs.readFileSync(path.join(root,'workspace/TOOLS.md'),'utf8').length:0)+256;
c.agents.defaults.bootstrapMaxChars=Math.max(c.agents.defaults.bootstrapMaxChars??20000,Math.ceil(chars/1000)*1000);
fs.writeFileSync(config,JSON.stringify(c,null,2)+'\n');
const backup=path.join(root,'config/backups/tools-md-migration');fs.mkdirSync(backup,{recursive:true});fs.chownSync(backup,1000,1000);fs.chmodSync(backup,0o700);
console.log(JSON.stringify({startupVerifier:'10.4',timeoutSeconds:0,bootstrapMaxChars:c.agents.defaults.bootstrapMaxChars}));
