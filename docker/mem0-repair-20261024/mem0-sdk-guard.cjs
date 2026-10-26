// Small fail-closed check; never installs packages during startup.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const project=fs.realpathSync(process.argv[2]);
const read=p=>JSON.parse(fs.readFileSync(path.join(project,p),'utf8'));
assert.equal(read('node_modules/@mem0/openclaw-mem0/package.json').version,'1.2.1');
assert.equal(read('node_modules/@mem0/openclaw-mem0/package.json').dependencies.mem0ai,'3.3.1');
assert.equal(read('node_modules/mem0ai/package.json').version,'3.3.1');
assert.equal(read('node_modules/@qdrant/js-client-rest/package.json').version,'1.18.0');
assert.equal(read('node_modules/zod/package.json').version,'4.6.6');
assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(project,'node_modules/@mem0/openclaw-mem0/dist/index.js'))).digest('hex'),'0e7205db54c8790c1aff7b09786ec0b7578db08181b5394a7137df4e530297c2');
assert.ok(read('package.json').dependencies['@mem0/openclaw-mem0'].startsWith('file:vendor/'));
assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(project,'package-lock.json'))).digest('hex'),'e4180c3b5587246e6b6f04d4a3ec52c85432f00c87dc6d79ab2134601a9e519c');
for(const unused of ['cloudflare','@azure/identity','@mistralai/mistralai'])assert.ok(!fs.existsSync(path.join(project,'node_modules',unused)));
console.log('[mem0-sdk] Reproducible SDK3.3.1 package, custom tools and dependency lock verified.');
