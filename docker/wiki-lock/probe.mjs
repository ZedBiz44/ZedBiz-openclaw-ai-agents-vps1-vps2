import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
const [vault, action, duration = '1000'] = process.argv.slice(2);
const files = await fs.readdir('/app/dist');
let coordinate;
for (const name of files.filter(name => name.startsWith('presentation-') && name.endsWith('.mjs'))) {
  if ((await fs.readFile('/app/dist/' + name, 'utf8')).includes('zedbiz-wiki-flock-v1')) {
    const module = await import('/app/dist/' + name);
    coordinate = module.b;
  }
}
assert.equal(typeof coordinate, 'function');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
await coordinate(vault, async () => {
  console.log('ENTER ' + Date.now());
  if (action === 'hold') await pause(Number(duration));
  if (action === 'nested') {
    await coordinate(vault, async () => console.log('NESTED'));
  }
  if (action === 'throw') throw new Error('intentional-test-error');
  if (action === 'increment') {
    const counter = path.join(vault, 'counter');
    let value = Number(await fs.readFile(counter, 'utf8').catch(() => '0'));
    await pause(100);
    await fs.writeFile(counter, String(value + 1));
  }
  console.log('LEAVE ' + Date.now());
});
