import fs from 'node:fs';
import path from 'node:path';
const base='/home/node/.openclaw/npm/projects';
const host=JSON.parse(fs.readFileSync('/app/package.json','utf8'));
if(host.version!=='2026.9.8') throw new Error('Review host compatibility before use');
const {a:linkHost}=await import('/app/dist/plugin-peer-link-S4jA-R0H.mjs');
const packages=['@openclaw/memory-lancedb','@mem0/openclaw-mem0','@vectorize-io/hindsight-openclaw'];
for(const dir of fs.readdirSync(base)) {
 const root=path.join(base,dir);
 for(const pkg of packages) {
  const manifest=path.join(root,'node_modules',pkg,'package.json');
  if(!fs.existsSync(manifest))continue;
  const p=JSON.parse(fs.readFileSync(manifest,'utf8'));
  const allowed=pkg==='@openclaw/memory-lancedb'?['2026.9.8']:pkg==='@mem0/openclaw-mem0'?['1.1.0','1.2.1']:['0.12.0','0.13.0'];
  if(!allowed.includes(p.version))continue;
  await linkHost({installedDir:root,peerDependencies:{openclaw:'2026.9.8'},hostRoot:'/app',logger:console});
  if(fs.realpathSync(path.join(root,'node_modules/openclaw'))!=='/app')throw new Error('Peer repair failed');
  console.log(`Verified ${pkg}@${p.version} host peer`);
 }
}
