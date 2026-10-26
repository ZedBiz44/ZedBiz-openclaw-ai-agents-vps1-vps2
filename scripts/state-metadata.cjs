const {DatabaseSync} = require('node:sqlite');
const crypto = require('node:crypto');
const db = new DatabaseSync(process.argv[2], {readOnly:true});
const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").all().map(r=>r.name);
for (const name of tables.filter(n=>/cron|automation|agent_roster|agent_config/.test(n))) {
  if (!/^[a-zA-Z0-9_]+$/.test(name)) throw new Error('Unexpected table name');
  const rows=db.prepare('SELECT * FROM "'+name+'"').all();
  console.log(JSON.stringify({table:name,count:rows.length,contentHash:crypto.createHash('sha256').update(JSON.stringify(rows)).digest('hex')}));
}
db.close();
