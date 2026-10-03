import {loadAuthProfileStoreForRuntime} from '/opt/openclaw-harry/node_modules/openclaw/dist/plugin-sdk/agent-runtime.js';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawn} from 'node:child_process';
import readline from 'node:readline';
const store=await loadAuthProfileStoreForRuntime('/root/.openclaw-harry/agents/main/agent');
const p=store.profiles['openai:jzedbiz@gmail.com'];
if(p?.type!=='oauth'||!p.access||!p.accountId)throw Error('Expected existing OAuth profile');
const home=fs.mkdtempSync('/tmp/sol-oauth-probe-');
const env={PATH:process.env.PATH,HOME:home,CODEX_HOME:home,LANG:'C.UTF-8'};
const command=process.argv[2]||'/usr/bin/codex';
const child=spawn(command,['-c','cli_auth_credentials_store="ephemeral"','app-server','--listen','stdio://'],{env,cwd:home,stdio:['pipe','pipe','pipe']});
const pending=new Map();let id=0,completed;const done=new Promise(r=>completed=r);const events=[];
const clean=s=>String(s).replaceAll(p.access,'[REDACTED]').replaceAll(p.refresh||'NEVER_MATCH_REFRESH','[REDACTED]');
readline.createInterface({input:child.stdout}).on('line',line=>{try{const m=JSON.parse(line);if(m.id!=null&&pending.has(m.id)){const q=pending.get(m.id);pending.delete(m.id);m.error?q.reject(Error(clean(m.error.message))):q.resolve(m.result);}else if(m.method==='turn/completed'){events.push({method:m.method,status:m.params.turn.status,error:m.params.turn.error});completed();}else if(m.method==='item/completed'&&m.params.item.type==='agentMessage'){events.push({method:m.method,text:m.params.item.text});}else if(m.method==='error'){events.push({method:m.method,error:m.params.error});}else if(m.id!=null&&m.method){child.stdin.write(JSON.stringify({id:m.id,error:{code:-32601,message:'Probe does not permit tools or credential refresh'}})+'\n');}}catch{}});
child.stderr.resume();
function rpc(method,params){return new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});child.stdin.write(JSON.stringify({id:n,method,params})+'\n');setTimeout(()=>{if(pending.delete(n))reject(Error('Timed out '+method));},30000).unref();});}
const deadline=setTimeout(()=>{completed();child.kill();},90000);
try{
 const init=await rpc('initialize',{clientInfo:{name:'harry_oauth_diagnostic',title:'VPS1 OAuth diagnostic',version:'1.0.0'},capabilities:{experimentalApi:true}});
 child.stdin.write(JSON.stringify({method:'initialized'})+'\n');
 const login=await rpc('account/login/start',{type:'chatgptAuthTokens',accessToken:p.access,chatgptAccountId:p.accountId,chatgptPlanType:p.chatgptPlanType});
 const account=await rpc('account/read',{refreshToken:false});
 const models=await rpc('model/list',{includeHidden:true});
 const found=(models.data||[]).filter(m=>(m.model||m.id||'').includes('6.1'));
 console.log(JSON.stringify({command,server:init.userAgent,authType:account.account?.type,loginType:login.type,models:found.map(m=>({id:m.id,model:m.model}))}));
 const thread=await rpc('thread/start',{model:'gpt-6.1-sol',cwd:home,approvalPolicy:'never',sandbox:'read-only',ephemeral:true});
 console.log(JSON.stringify({threadModel:thread.model,provider:thread.modelProvider}));
 await rpc('turn/start',{threadId:thread.thread.id,model:'gpt-6.1-sol',effort:'low',input:[{type:'text',text:'Reply exactly OAUTH_SOL_OK. Do not use tools.'}]});
 await done;
 console.log(clean(JSON.stringify({events})));
}catch(e){console.log(JSON.stringify({error:clean(e.message)}));process.exitCode=1;}
finally{clearTimeout(deadline);child.kill();await new Promise(r=>setTimeout(r,500));fs.rmSync(home,{recursive:true,force:true});}
