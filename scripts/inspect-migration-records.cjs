const {DatabaseSync}=require('node:sqlite');
const db=new DatabaseSync(process.argv[2],{readOnly:true});
for(const {name} of db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%migration%' OR name LIKE '%plugin%')").all()){
 if(!/^[a-zA-Z0-9_]+$/.test(name))throw Error('Unexpected identifier');
 console.log(JSON.stringify({table:name,columns:db.prepare('PRAGMA table_info('+name+')').all().map(x=>x.name)}));
}
console.log(JSON.stringify({webhooksState:db.prepare("SELECT plugin_id,namespace,entry_key FROM plugin_state_entries WHERE plugin_id='webhooks'").all()}));
console.log(JSON.stringify({webhooksBlobs:db.prepare("SELECT plugin_id,namespace,entry_key FROM plugin_blob_entries WHERE plugin_id='webhooks'").all()}));
db.close();
