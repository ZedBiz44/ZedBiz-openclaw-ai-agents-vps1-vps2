import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const cfg=JSON.parse(fs.readFileSync('/home/node/.openclaw/openclaw.json','utf8'));
const root='/app/dist';
const source=fs.readdirSync(root).find(x=>/^client-[^.]+\.mjs$/.test(x)&&fs.readFileSync(path.join(root,x),'utf8').includes('GatewayClient as t'));
const {t:GatewayClient}=await import(pathToFileURL(path.join(root,source)));
let token=cfg.gateway?.auth?.token;
if(typeof token==='string'&&token.startsWith('${'))token=process.env[token.slice(2,-1)];
if(typeof token!=='string')token=process.env.OPENCLAW_GATEWAY_TOKEN;
let client;
const timer=setTimeout(()=>{console.error('RPC deadline');process.exit(2)},45000);
client=new GatewayClient({url:`ws://127.0.0.1:${cfg.gateway.port}`,token,sharedStateMode:'read-only',clientName:'cli',mode:'cli',scopes:['operator.admin'],onConnectError:e=>{console.error(e.message);client.stop();clearTimeout(timer);process.exitCode=2;},onHelloOk:async()=>{
try{const result={};for(const [method,params] of [['status',{}],['cron.list',{includeDisabled:true}],['health',{}]])result[method]=await client.request(method,params,{timeoutMs:30000});console.log(JSON.stringify(result));}
catch(e){console.error(e.message);process.exitCode=2;}
finally{await client.stopAndWait();clearTimeout(timer)}
}});client.start();

