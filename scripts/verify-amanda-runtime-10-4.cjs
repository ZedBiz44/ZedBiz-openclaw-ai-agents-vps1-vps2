const fs=require('node:fs');
if(JSON.parse(fs.readFileSync('/app/package.json')).version!=='2026.10.4')throw Error('Wrong runtime version');
const text=fs.readFileSync('/app/dist/diagnostic-stuck-session-recovery.runtime-C6gH1-h4.mjs','utf8');
if(!text.includes('active_work_no_elapsed_cutoff'))throw Error('Active-work protection missing');
const memory=fs.readFileSync('/app/dist/diagnostic-DxMcmqTS.mjs','utf8');
if(!memory.includes('options?.processMemoryLimitBytes ?? process.constrainedMemory()'))throw Error('Dynamic memory limit patch missing');
console.log('Amanda 10.4 startup safeguards verified');
