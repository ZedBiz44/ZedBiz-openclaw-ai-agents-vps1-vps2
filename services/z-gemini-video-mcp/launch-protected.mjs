import {spawn,spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
let key=process.env.GEMINI_API_KEY;
if (!key || key.startsWith('op://')) {
  const r=spawnSync('op',['read',process.env.GEMINI_VIDEO_SECRET_REF || 'op://openclaw-agents-shared/gemini-video-api-key/credential'],{encoding:'utf8',stdio:['ignore','pipe','pipe'],timeout:20000});
  if(r.status!==0 || !r.stdout.trim()){process.stderr.write('Protected Gemini credential resolution failed.\n');process.exit(1);}
  key=r.stdout.trim();
}
const child=spawn(process.execPath,[fileURLToPath(new URL('./server.mjs',import.meta.url))],{env:{...process.env,GEMINI_API_KEY:key},stdio:'inherit'});
child.on('exit',code=>process.exit(code??1));
for(const sig of ['SIGINT','SIGTERM']) process.on(sig,()=>child.kill(sig));
