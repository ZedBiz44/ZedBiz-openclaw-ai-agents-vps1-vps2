const fs = require('node:fs');
const assert = require('node:assert/strict');
assert.equal(JSON.parse(fs.readFileSync('/app/package.json')).version, '2026.10.4');
const source = fs.readFileSync('/app/dist/skill-collection-review-monitor-D4uXmNHG.mjs', 'utf8');
assert.ok(source.includes('model: "openrouter/google/gemini-3.1-flash-lite", // Preserved Workshop route.'));
console.log('Workshop image safeguard verified');

