import { build } from 'esbuild';
import assert from 'node:assert/strict';
await build({entryPoints:['src/asana-validate-xml.ts'],bundle:true,platform:'node',format:'esm',outfile:'dist/validate-probe.mjs',external:['jsdom']});
const {validateAsanaXml}=await import('./dist/validate-probe.mjs');
for(const s of ['<body>Hello <strong>team</strong></body>','<body><ul><li>One</li><li>Two</li></ul></body>','<body><a href="https://example.com">Link</a></body>']) assert.deepEqual(validateAsanaXml(s),[]);
for(const s of ['<body><strong>broken</body>','<body><script>alert(1)</script></body>','<html/>']) assert.ok(validateAsanaXml(s).length);
console.log('JSDOM_RICH_TEXT_VALIDATION_PASSED');
