// Preserve empty legacy Workshop backup manifests outside the migration scan.
// Refuse any backup containing skills, hashes, or additional files.
import fs from 'node:fs';
import path from 'node:path';
const state=path.resolve(process.argv[2]);
const source=path.join(state,'skill-workshop','collection-backups');
const archive=path.join(state,'backups','preserved-empty-workshop-20260912');
if(!fs.existsSync(source)){console.log('No legacy Workshop collection backups');process.exit(0);}
for(const root of fs.readdirSync(source,{withFileTypes:true})){
 if(!root.isDirectory())throw Error('Unexpected collection backup entry');
 const from=path.join(source,root.name),to=path.join(archive,root.name);
 let count=0;
 for(const batch of fs.readdirSync(from,{withFileTypes:true})){
  if(!batch.isDirectory())throw Error('Unexpected backup structure');
  const dir=path.join(from,batch.name),files=fs.readdirSync(dir);
  if(files.length!==1||files[0]!=='manifest.json')throw Error('Backup contains more than an empty manifest');
  const m=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'),'utf8'));
  if(m.schema!=='openclaw.skill-collection-backup.v1'||!Array.isArray(m.skillDirs)||m.skillDirs.length||!Array.isArray(m.resultSkillDirs)||m.resultSkillDirs.length||!m.resultSkillHashes||Object.keys(m.resultSkillHashes).length)throw Error('Backup is not empty; review required');
  count++;
 }
 if(!count)throw Error('No manifest to verify');
 if(fs.existsSync(to))throw Error('Archive already exists; no overwrite permitted');
 fs.mkdirSync(archive,{recursive:true});fs.renameSync(from,to);
 console.log(JSON.stringify({status:'preserved-empty-manifests',from,to,count}));
}

