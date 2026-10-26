import fs from 'node:fs';
const path='/home/node/.openclaw/openclaw.json';
const c=JSON.parse(fs.readFileSync(path,'utf8'));
fs.copyFileSync(path,path+'.before-cody-9.8-final-20261003');
c.skills.entries['openai-whisper-api'].enabled=true;
// Doctor merged the existing 13,990-character AGENTS and 6,470-character TOOLS.
// Preserve full injection of that existing content after the upstream migration.
c.agents.defaults.bootstrapMaxChars=Math.max(c.agents.defaults.bootstrapMaxChars||20000,22000);
c.agents.defaults.models['openai/gpt-6.1-sol']={agentRuntime:{id:'codex'}};
const allow=c.agents.defaults.modelPolicy?.allow;
if (Array.isArray(allow) && !allow.includes('openai/gpt-6.1-sol')) allow.push('openai/gpt-6.1-sol');
fs.writeFileSync(path+'.tmp-cody',JSON.stringify(c,null,2)+'\n',{mode:0o600});
fs.renameSync(path+'.tmp-cody',path);
console.log('Restored transcription, preserved merged instructions, and added Sol test binding. Primary and fallbacks unchanged.');
