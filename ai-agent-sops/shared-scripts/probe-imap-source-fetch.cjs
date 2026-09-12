// Read-only live proof of the installed sweep; no agent dispatch or state writes.
// Usage: node probe-imap-source-fetch.cjs PACKAGE_ROOT STATE_ROOT
// EMAIL_PASSWORD must come from the existing protected runtime environment.
const fs=require('node:fs');
const {createRequire}=require('node:module');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {DatabaseSync}=require('node:sqlite');
const assert=require('node:assert/strict');
const [root,stateRoot]=process.argv.slice(2);
const code=fs.readFileSync(root+'/dist/extensions/imap/index.js','utf8');
assert(code.includes('zedbiz-imap-metadata-first-v1'));
const start=code.indexOf('\tasync sweep(client) {');
const end=code.indexOf('\n\tasync processMessage(',start);
assert(start>=0&&end>start);
const sweep=new Function('MAX_SOURCE_BYTES','advanceImapCursor',`return ({${code.slice(start,end)}}).sweep;`)(1048576,async(state,id,v,uid)=>{state.cursor.lastSeenUid=uid;});
(async()=>{
 let ImapFlow;
 try { ({ImapFlow}=createRequire(root+'/package.json')('imapflow')); }
 catch(error) {
  if(error.code!=='MODULE_NOT_FOUND')throw error;
  // Native npm installations bundle ImapFlow instead of exposing node_modules.
  // Import an in-memory copy with resolved imports; never edit the live bundle.
  const imported=code.replace(/(\bfrom\s+|\bimport\s+)(["'])(\.{1,2}\/[^"']+)\2/g,
   (_,prefix,quote,relative)=>prefix+quote+pathToFileURL(path.resolve(root,'dist/extensions/imap',relative)).href+quote);
  const module=await import('data:text/javascript;base64,'+Buffer.from(imported+'\nexport const probeImapFlow=import_imap_flow.ImapFlow;').toString('base64'));
  ImapFlow=module.probeImapFlow;
 }
 const config=JSON.parse(fs.readFileSync(stateRoot+'/openclaw.json'));
 const a=config.plugins.entries.imap.config.accounts.agent_mail;
 const db=new DatabaseSync(stateRoot+'/state/openclaw.sqlite',{readOnly:true});
 const row=db.prepare("SELECT value_json FROM plugin_state_entries WHERE plugin_id='imap' AND namespace='cursor' AND entry_key='agent_mail'").get();db.close();
 const cursor=JSON.parse(row.value_json);
 const real=new ImapFlow({host:a.host,port:a.port,secure:a.secure,auth:{user:a.user,pass:process.env.EMAIL_PASSWORD},logger:false});
 try{
  await real.connect();const mailbox=await real.mailboxOpen(a.mailbox||'INBOX',{readOnly:true});
  assert.equal(cursor.uidValidity,mailbox.uidValidity.toString());
  const results=[];
  for(const lastSeenUid of [cursor.lastSeenUid,cursor.lastSeenUid,Math.max(0,cursor.lastSeenUid-1)]){
   const state={cursor:{...cursor,lastSeenUid},cursors:{async lookup(){return {...state.cursor};}}};
   const result={lastSeenUid,sourceBytes:0,sourceCalls:0,processed:[]};
   const client={async *fetch(range,query,opts){if(query.source)result.sourceCalls++;for await(const m of real.fetch(range,query,opts)){result.sourceBytes+=m.source?.length||0;yield m;}}};
   await sweep.call({options:{state,accountId:'agent_mail',context:{logger:{}}},client,stopping:false,async processMessage(m){result.processed.push(m.uid);return true;}},client);
   results.push(result);
  }
  assert.equal(results[0].sourceBytes,0,'Unexpected pending mail; inspect before calling this an idle proof');
  assert.equal(results[1].sourceBytes,0);
  assert(results[2].processed.includes(cursor.lastSeenUid),'Pending-message retrieval failed');
  console.log(JSON.stringify({account:a.user,readOnly:true,installedSweep:true,results}));
  await real.logout();
 }finally{real.close();}
})().catch(e=>{console.error(e.code||e.name,e.message);process.exitCode=1;});
