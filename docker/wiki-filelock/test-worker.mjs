import fs from 'node:fs/promises';
import {acquireWikiLock} from '/opt/zedbiz/wiki-lock/lock.mjs';
const [vault, id, action = 'hold', duration = '150'] = process.argv.slice(2);
const bundle = (await fs.readdir('/app/dist')).filter(n=>n.endsWith('.mjs'));
let wiki;
for (const name of bundle) {
  if ((await fs.readFile('/app/dist/'+name,'utf8')).includes('async function withMemoryWikiVaultMutation(')) {
    wiki = await import('/app/dist/'+name); break;
  }
}
const event=async kind=>fs.appendFile(vault+'/events',JSON.stringify({id,kind,time:Date.now()})+'\n');
const body=async()=>{
  await event('ENTER');
  if(action==='nested') await wiki.x(vault,()=>event('NESTED'));
  if(action==='throw') throw new Error('intentional');
  const value=Number(await fs.readFile(vault+'/counter','utf8').catch(()=>0));
  await new Promise(r=>setTimeout(r,Number(duration)));
  await fs.writeFile(vault+'/counter',String(value+1));
  await event('LEAVE');
};
try {
  if(action==='timeout') {
    const release=await acquireWikiLock(vault,0.25);
    try {await body();} finally {await release();}
  } else await wiki.x(vault,body);
} catch(e) {await event(e.code==='WIKI_LOCK_TIMEOUT'?'TIMEOUT':'ERROR'); process.exitCode=2;}
