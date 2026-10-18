const fs=require('node:fs');
const {DatabaseSync}=require('node:sqlite');
const before=process.argv[2], after=process.argv[3];
const changes=[];
function diff(a,b,p='') {
  if(JSON.stringify(a)===JSON.stringify(b))return;
  if(a&&b&&typeof a==='object'&&typeof b==='object'&&!Array.isArray(a)&&!Array.isArray(b)) {
    for(const k of new Set([...Object.keys(a),...Object.keys(b)]))diff(a[k],b[k],p+'/'+k);
  }else changes.push({path:p,change:a===undefined?'added':b===undefined?'removed':'changed'});
}
diff(JSON.parse(fs.readFileSync(before+'/config/openclaw.json')),JSON.parse(fs.readFileSync(after+'/config/openclaw.json')));
console.log(JSON.stringify({configChanges:changes}));
const db1=new DatabaseSync(before+'/config/state/openclaw.sqlite',{readOnly:true});
const db2=new DatabaseSync(after+'/config/state/openclaw.sqlite',{readOnly:true});
const a=db1.prepare('SELECT * FROM cron_jobs ORDER BY rowid').all();
const b=db2.prepare('SELECT * FROM cron_jobs ORDER BY rowid').all();
changes.length=0;
diff(a,b,'cron_jobs');
console.log(JSON.stringify({cronBefore:a.length,cronAfter:b.length,exactRowsEqual:JSON.stringify(a)===JSON.stringify(b)}));
if(a.length!==b.length)throw new Error('Cron job count changed');
for(let i=0;i<a.length;i++) {
  changes.length=0;
  for(const key of new Set([...Object.keys(a[i]),...Object.keys(b[i])])) {
    let av=a[i][key],bv=b[i][key];
    try{av=JSON.parse(av);bv=JSON.parse(bv)}catch{}
    diff(av,bv,key);
  }
  if(changes.length)console.log(JSON.stringify({jobIndex:i,changes}));
}
db1.close();db2.close();

