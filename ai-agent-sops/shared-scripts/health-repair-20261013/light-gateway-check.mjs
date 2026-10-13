import fs from 'node:fs';
const root=process.argv[2];
const cfg=JSON.parse(fs.readFileSync((process.env.OPENCLAW_CONFIG_PATH||root+'/openclaw.json'),'utf8'));
const ws=new WebSocket('ws://127.0.0.1:'+(cfg.gateway.port||18789));
let started=false;
const connectionTimer=setTimeout(()=>{console.error('Gateway connection response deadline exceeded');process.exitCode=1;ws.close();},15000);
const pending=new Map();let seq=0;
function request(method,params){return new Promise((resolve,reject)=>{const id=String(++seq);const timer=setTimeout(()=>{pending.delete(id);reject(new Error('Response deadline exceeded for '+method));},15000);pending.set(id,{resolve,reject,timer});ws.send(JSON.stringify({type:'req',id,method,params}));});}
ws.onmessage=async ({data})=>{const m=JSON.parse(data);if(m.type==='res'){const p=pending.get(m.id);if(p){clearTimeout(p.timer);pending.delete(m.id);m.ok?p.resolve(m.payload):p.reject(new Error(m.error?.message||'request rejected'));}return;}
if(m.event==='connect.challenge'&&!started)try{
 started=true;clearTimeout(connectionTimer);
 await request('connect',{minProtocol:3,maxProtocol:4,client:{id:'cli',version:'2026.9.8',platform:'linux',mode:'cli'},role:'operator',scopes:['operator.read'],auth:{token:cfg.gateway.auth.token}});
 const selected=process.argv[3];if(!['health','channels'].includes(selected))throw new Error('Only health or channels are supported');const result=await request(selected==='health'?'health':'channels.status',selected==='health'?{}:{probe:true,timeoutMs:10000});console.log(JSON.stringify(result));ws.close();
}catch(e){console.error(e.message);process.exitCode=1;ws.close();}};
ws.onerror=()=>{clearTimeout(connectionTimer);console.error('Gateway WebSocket connection failed');process.exitCode=1;};
ws.onclose=()=>{clearTimeout(connectionTimer);for(const p of pending.values()){clearTimeout(p.timer);p.reject(new Error('Gateway connection closed before its response'));}pending.clear();};
