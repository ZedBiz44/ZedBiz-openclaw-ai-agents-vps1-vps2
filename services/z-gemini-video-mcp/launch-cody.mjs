import {spawn,spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const keyFile=process.env.ZEDBIZ_GEMINI_SSH_KEY;
if(!keyFile){process.stderr.write('ZEDBIZ_GEMINI_SSH_KEY is not configured.\n');process.exit(1);}
// Capture only the dedicated Gemini credential in memory; never print or persist it.
const r=spawnSync('ssh',['-o','BatchMode=yes','-o','ConnectTimeout=12','-i',keyFile,'jackadmin@187.77.210.223',`docker exec terry node -e 'process.stdout.write(process.env.GEMINI_API_KEY || "")'`],{encoding:'utf8',stdio:['ignore','pipe','pipe'],timeout:20000,windowsHide:true});
if(r.status!==0 || !r.stdout.trim() || r.stdout.trim().startsWith('op://')){process.stderr.write('Dedicated Gemini credential unavailable through protected VPS1 route.\n');process.exit(1);}
const child=spawn(process.execPath,[fileURLToPath(new URL('./server.mjs',import.meta.url))],{env:{...process.env,GEMINI_API_KEY:r.stdout.trim()},stdio:'inherit',windowsHide:true});
child.on('exit',code=>process.exit(code??1));
for(const sig of ['SIGINT','SIGTERM']) process.on(sig,()=>child.kill(sig));
