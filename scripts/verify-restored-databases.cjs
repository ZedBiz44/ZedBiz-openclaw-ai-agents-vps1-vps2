const fs = require('node:fs');
const path = require('node:path');
const {DatabaseSync} = require('node:sqlite');
const root = process.argv[2];
const result = [];
for (const rel of ['config/state/openclaw.sqlite', 'agents/main/agent/openclaw-agent.sqlite']) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file)) throw new Error('Missing recovery database: ' + rel);
  const db = new DatabaseSync(file);
  const check = db.prepare('PRAGMA quick_check').all();
  if (check.length !== 1 || check[0].quick_check !== 'ok') throw new Error('Recovery check failed: ' + rel);
  result.push({path:rel, quickCheck:check, schema:db.prepare('PRAGMA user_version').get()});
  db.close();
}
console.log(JSON.stringify(result));
