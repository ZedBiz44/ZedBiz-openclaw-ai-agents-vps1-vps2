import {readFileSync,writeFileSync,copyFileSync,statSync} from 'node:fs';
const [config,entry]=process.argv.slice(2);
const data=JSON.parse(readFileSync(config,'utf8'));
const old=data.mcp?.servers?.['gemini-video'];
if(!old) throw new Error('Expected existing Gemini connection; inspect this runtime before adding.');
const backup=config+'.before-gemini-files-20260921';
try {writeFileSync(backup,readFileSync(config),{flag:'wx',mode:statSync(config).mode});}catch(e){if(e.code!=='EEXIST')throw e;}
old.args=[entry];old.requestTimeoutMs=600000;
old.toolFilter={...old.toolFilter,include:['analyze_youtube_video','analyze_media_file']};
writeFileSync(config,JSON.stringify(data,null,2)+'\n');
console.log(JSON.stringify({config,entry,tools:old.toolFilter.include,backup}));
