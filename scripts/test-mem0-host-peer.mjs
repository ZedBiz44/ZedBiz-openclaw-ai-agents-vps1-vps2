import fs from 'node:fs';
import {spawnSync} from 'node:child_process';
import assert from 'node:assert/strict';
const root = '/home/node/.openclaw/npm/projects/mem0-compat-test';
const pkg = root + '/node_modules/@mem0/openclaw-mem0';
fs.mkdirSync(pkg, {recursive:true});
fs.writeFileSync(pkg+'/package.json', JSON.stringify({name:'@mem0/openclaw-mem0',version:'1.2.1'}));
const run = (arg=root) => spawnSync('node', [process.env.TEST_HELPER ?? '/test/repair-mem0-host-peer.mjs',arg], {encoding:'utf8'});
assert.equal(run().status,0);
assert.equal(fs.realpathSync(root+'/node_modules/openclaw'),'/app');
assert.equal(run().status,0);
fs.writeFileSync(pkg+'/package.json',JSON.stringify({version:'9.9.9'}));
assert.notEqual(run().status,0);
assert.notEqual(run('/tmp').status,0);
console.log('PASS: real host link, idempotence, unexpected plugin rejection, outside-root rejection');

