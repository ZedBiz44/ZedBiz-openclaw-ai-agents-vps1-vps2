import {spawn,spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const keyFile=process.env.ZEDBIZ_GEMINI_SSH_KEY;
if(!keyFile){process.stderr.write('ZEDBIZ_GEMINI_SSH_KEY is not configured.\n');process.exit(1);}
const sshArgs=['-o','BatchMode=yes','-o','ConnectTimeout=12'];
if(process.env.ZEDBIZ_GEMINI_KNOWN_HOSTS)sshArgs.push('-o','UserKnownHostsFile='+process.env.ZEDBIZ_GEMINI_KNOWN_HOSTS);
// Reuse the agent's authorized SSH route. Dedicated credential stays in memory.
sshArgs.push('-i',keyFile,'jackadmin@187.77.210.223',`docker exec terry node -e 'process.stdout.write(process.env.GEMINI_API_KEY || "")'`);
const r=spawnSync('ssh',sshArgs,{encoding:'utf8',stdio:['ignore','pipe','pipe'],timeout:20000,windowsHide:true});
if(r.status!==0 || !r.stdout.trim() || r.stdout.trim().startsWith('op://')){process.stderr.write('Dedicated Gemini credential unavailable through protected VPS1 route.\n');process.exit(1);}
const child=spawn(process.execPath,[fileURLToPath(new URL('./server.mjs',import.meta.url))],{env:{...process.env,GEMINI_API_KEY:r.stdout.trim()},stdio:'inherit',windowsHide:true});
child.on('exit',code=>process.exit(code??1));
for(const sig of ['SIGINT','SIGTERM'])process.on(sig,()=>child.kill(sig));
