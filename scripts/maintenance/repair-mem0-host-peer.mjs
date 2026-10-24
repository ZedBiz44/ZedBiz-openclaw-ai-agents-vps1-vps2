// Mem0 does not declare an OpenClaw peer. OpenClaw 2026.9.8's retained
// native dependency loader nevertheless requires the managed root host link.
// Use the installer implementation, preserving the loader's host validation.
import fs from 'node:fs';
import path from 'node:path';
const root=fs.realpathSync(process.argv[2]);
const base='/home/node/.openclaw/npm/projects/';
if (!root.startsWith(base+'mem0-')) throw new Error('Unexpected managed project');
const host=JSON.parse(fs.readFileSync('/app/package.json','utf8'));
if (host.version!=='2026.9.8') throw new Error('Review host-link compatibility for this OpenClaw version');
const plugin=JSON.parse(fs.readFileSync(path.join(root,'node_modules/@mem0/openclaw-mem0/package.json'),'utf8'));
if (plugin.version!=='1.2.1') throw new Error('Unexpected Mem0 version');
const {a:linkHost}=await import('/app/dist/plugin-peer-link-S4jA-R0H.mjs');
const result=await linkHost({installedDir:root,peerDependencies:{openclaw:'2026.9.8'},hostRoot:'/app',logger:console});
if (result.skipped || fs.realpathSync(path.join(root,'node_modules/openclaw'))!=='/app') throw new Error('Host peer repair failed');
console.log('Verified managed Mem0 host peer -> /app');
