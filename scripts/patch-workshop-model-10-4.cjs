// Preserve the existing Marsha/Grogar Workshop route in their image layer.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const file = '/app/dist/skill-collection-review-monitor-D4uXmNHG.mjs';
const old = 'message: SKILL_WORKSHOP_MAINTENANCE_PROMPT,';
const replacement = old+'\n\t\t\t\t\tmodel: "openrouter/google/gemini-3.1-flash-lite", // Preserved Workshop route.';
const source = fs.readFileSync(file, 'utf8');
assert.equal(source.split(old).length, 2, 'Unexpected Workshop declaration');
assert.ok(!source.includes('Preserved Workshop route.'), 'Already patched');
fs.writeFileSync(file, source.replace(old, replacement));
assert.equal(fs.readFileSync(file, 'utf8').split(replacement).length, 2);
console.log('Existing Workshop model route preserved in image');

