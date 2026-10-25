// Versioned safeguards for cohorts whose 10.4 startup guards are retired.
const fs=require('node:fs'),assert=require('node:assert/strict');
assert.equal(JSON.parse(fs.readFileSync('/app/package.json','utf8')).version,'2026.10.6');
assert.equal(process.versions.node,'24.22.1');
const files=fs.readdirSync('/app/dist').filter(x=>x.endsWith('.mjs'));
const memory=files.filter(x=>/^diagnostic-/.test(x)).map(x=>fs.readFileSync('/app/dist/'+x,'utf8'));
assert.ok(memory.some(x=>x.includes('options?.processMemoryLimitBytes ?? process.constrainedMemory()')),'Dynamic memory safeguard missing');
if(process.argv[2]==='amanda'){
 const code=fs.readFileSync('/app/dist/diagnostic-stuck-session-recovery.runtime-CZf9xpaE.mjs','utf8');
 const guard=code.indexOf('active_work_no_elapsed_cutoff');
 assert.ok(guard>=0&&guard<code.indexOf('const preAbortActiveTaskIds = new Set(getCommandLaneActiveTaskIds(sessionLane));'),'Amanda active-work safeguard missing or ordered incorrectly');
}
if(process.argv[2]==='grogar')assert.ok(!files.some(x=>x.startsWith('skill-collection-review-monitor-')),'Unexpected retired Workshop runtime requires review');
console.log('OpenClaw10.6, Node and applicable cohort safeguards verified');

