import fs from 'node:fs';
import {createSessionMcpRuntime} from '/app/dist/agents/agent-bundle-mcp-runtime.js';
const started=Date.now();
const record=x=>console.log(JSON.stringify({...x,elapsedMs:Date.now()-started,time:new Date().toISOString()}));
const deadline=setTimeout(()=>{record({phase:'outer-deadline',status:'failed'});process.exit(124);},1040000);
const cfg=JSON.parse(fs.readFileSync('/home/node/.openclaw/openclaw.json','utf8'));
const servers={asana:{...cfg.mcp.servers.asana,requestTimeoutMs:20000}};
servers.asana.headers=Object.fromEntries(Object.entries(servers.asana.headers??{}).map(([k,v])=>[k,v.replace(/\$\{([^}]+)\}/g,(_,n)=>process.env[n]??'')]));
const root=fs.mkdtempSync('/tmp/cody-bounded-idle-');
const r=createSessionMcpRuntime({cfg:{mcp:{servers}},workspaceDir:root,agentDir:root,sessionId:'cody-bounded-idle-20260917',sessionKey:'cody-bounded-idle-20260917',loaded:{mcpServers:servers,diagnostics:[],prepareDataDirsByServer:{}}});
const bound=async(label,fn,ms)=>{
 record({phase:label,status:'started'});
 let timer;
 try {const v=await Promise.race([fn(),new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error(label+' deadline exceeded')),ms);})]);record({phase:label,status:'returned'});return v;}
 finally{clearTimeout(timer);}
};
let passed=false;
try{
 const c=await bound('initial-catalog',()=>r.getCatalog(),30000);
 if(!c.tools.length)throw new Error('No authenticated tools');
 record({phase:'idle-start',tools:c.tools.length,seconds:970});
 await new Promise(resolve=>setTimeout(resolve,970000));
 const c2=await bound('post-expiry-list',()=>r.listTools('asana',{}),30000);
 if(!c2.tools.length)throw new Error('No tools after expiry');
 record({phase:'post-expiry-result',tools:c2.tools.length});
 passed=true;
}catch(e){record({phase:'failure',error:e.message});}
try{await bound('cleanup',async()=>{await r.dispose();await r.joinCleanup();},10000);}
catch(e){passed=false;record({phase:'cleanup-failure',error:e.message});}
clearTimeout(deadline);record({phase:'final',passed});process.exit(passed?0:1);
