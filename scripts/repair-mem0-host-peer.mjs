// Reviewed host-link implementations; reject unreviewed runtime/plugin versions.
import fs from 'node:fs';
import path from 'node:path';
const root = fs.realpathSync(process.argv[2]);
const base = '/home/node/.openclaw/npm/projects/';
if (!root.startsWith(base + 'mem0-')) throw new Error('Unexpected managed project');
const host = JSON.parse(fs.readFileSync('/app/package.json', 'utf8'));
const modules = {
  '2026.9.8': '/app/dist/plugin-peer-link-S4jA-R0H.mjs',
  '2026.10.4': '/app/dist/plugin-peer-link-D9lvYxJ1.mjs',
};
if (!modules[host.version]) throw new Error('Review host-link compatibility for this OpenClaw version');
const plugin = JSON.parse(fs.readFileSync(path.join(root, 'node_modules/@mem0/openclaw-mem0/package.json'), 'utf8'));
if (plugin.version !== '1.2.1') throw new Error('Unexpected Mem0 version');
const { a: linkHost } = await import(modules[host.version]);
const result = await linkHost({installedDir: root, peerDependencies: {openclaw: host.version}, hostRoot: '/app', logger: console});
if (result.skipped || fs.realpathSync(path.join(root, 'node_modules/openclaw')) !== '/app') throw new Error('Host peer repair failed');
console.log('Verified managed Mem0 host peer -> /app for ' + host.version);

