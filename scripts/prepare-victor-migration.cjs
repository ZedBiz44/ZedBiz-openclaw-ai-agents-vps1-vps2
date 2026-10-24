// Run against one offline Victor tree after verifying its protected recovery archive.
const fs=require('node:fs');
const path=require('node:path');
const root=process.argv[2];
const file=path.join(root,'config/openclaw.json');
const cfg=JSON.parse(fs.readFileSync(file));
const defaults=cfg.agents.defaults;
const before=defaults.bootstrapMaxChars??20000;
defaults.bootstrapMaxChars=Math.max(before,24000);
fs.writeFileSync(file,JSON.stringify(cfg,null,2)+'\n');
const backup=path.join(root,'config/backups/tools-md-migration');
fs.mkdirSync(backup,{recursive:true});
fs.chownSync(backup,1000,1000);
fs.chmodSync(backup,0o700);
console.log(JSON.stringify({bootstrapBefore:before,bootstrapAfter:defaults.bootstrapMaxChars,backupDirectoryOwner:'1000:1000',backupDirectoryMode:'0700'}));
