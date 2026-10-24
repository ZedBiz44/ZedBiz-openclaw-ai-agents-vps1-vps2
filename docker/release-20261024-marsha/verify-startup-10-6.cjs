// Marsha's versioned boot gate replaces the retired Skill Workshop10.4 gate.
const fs=require('node:fs'),assert=require('node:assert/strict'),crypto=require('node:crypto');
assert.equal(JSON.parse(fs.readFileSync('/app/package.json','utf8')).version,'2026.10.6');
assert.equal(process.versions.node,'24.22.1');
const manifest=JSON.parse(fs.readFileSync('/opt/zedbiz/marsha-10-6-originals/manifest.json','utf8'));
assert.ok(manifest.every(x=>crypto.createHash('sha256').update(fs.readFileSync('/app/'+x.file)).digest('hex')===x.after),'Marsha scheduling/caller-binding patch differs');
if(process.argv.includes('--identity-is-current')){
 const c=JSON.parse(fs.readFileSync('/home/node/.openclaw/openclaw.json','utf8'));
 const identity=c.agents?.entries?.main?.identity||c.agents?.list?.find(x=>x.id==='main')?.identity;
 process.exit(identity?.name==='Marsha'&&identity?.avatar==='avatars/openclaw.png'?0:1);
}
console.log('Marsha10.6 runtime, Node and scheduling patch verified');

