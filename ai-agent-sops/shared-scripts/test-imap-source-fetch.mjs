// Exercise the actual deployed sweep method without dispatching agent work.
import fs from 'node:fs';
import assert from 'node:assert/strict';
const code = fs.readFileSync(process.argv[2], 'utf8');
const start = code.indexOf('\tasync sweep(client) {');
const end = code.indexOf('\n\tasync processMessage(', start);
assert(start >= 0 && end > start, 'Expected compiled sweep method');
const sweep = new Function('MAX_SOURCE_BYTES','advanceImapCursor',
  `return ({${code.slice(start,end)}}).sweep;`)(1048576, async (state,id,validity,uid)=>{state.cursor.lastSeenUid=uid;});
async function check(name, lastSeenUid, mailbox, rejectUid, expectedDownloads, expectedProcessed, expectedCursor) {
  const downloads=[],processed=[];
  const state={cursor:{lastSeenUid,uidValidity:'1'},cursors:{async lookup(){return {...state.cursor};}}};
  const client={async *fetch(range,query){
    const selected=Array.isArray(range)?mailbox.filter(m=>range.includes(m.uid)):
      mailbox.filter(m=>m.uid>=Number(range.split(':')[0]) || m===mailbox.at(-1));
    for(const m of selected){if(query.source)downloads.push(m.uid);yield {...m,source:query.source?Buffer.from('test'):undefined};}
  }};
  await sweep.call({options:{state,accountId:'test',context:{logger:{}}},client,stopping:false,
    async processMessage(m){processed.push(m.uid);return m.uid!==rejectUid;}},client);
  assert.deepEqual(downloads,expectedDownloads,name+' downloads');
  assert.deepEqual(processed,expectedProcessed,name+' processing');
  assert.equal(state.cursor.lastSeenUid,expectedCursor,name+' cursor');
  console.log('PASS '+name);
}
await check('quiet inbox',9,[{uid:9}],null,[],[],9);
await check('empty inbox',0,[],null,[],[],0);
await check('new messages and UID gap',9,[{uid:9},{uid:11},{uid:13}],null,[11,13],[11,13],13);
await check('retry retains cursor',9,[{uid:10},{uid:11}],10,[10,11],[10],9);
