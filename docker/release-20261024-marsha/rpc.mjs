// Lightweight read-only storage client; avoids starting a second plugin loader.
import fs from 'node:fs';
import {t as GatewayClient} from '/app/dist/client-CEQLDSRp.mjs';
const config=JSON.parse(fs.readFileSync('/home/node/.openclaw/openclaw.json','utf8'));
let token=config.gateway?.auth?.token;
if(typeof token==='string'&&token.startsWith('${'))token=process.env[token.slice(2,-1)];
const requests=JSON.parse(process.env.CODY_RPC_REQUESTS||'[["status",{}],["cron.list",{"includeDisabled":true}],["health",{}]]');
let client;
const timer=setTimeout(()=>{console.error('RPC deadline');process.exit(2)},45000);
client=new GatewayClient({url:`ws://${process.env.CODY_RPC_HOST||'marsha'}:${config.gateway.port}`,token,sharedStateMode:'read-only',clientName:'cli',mode:'cli',scopes:['operator.admin'],onConnectError:e=>{console.error(e.message);clearTimeout(timer);client.stop();process.exitCode=2;},onHelloOk:async()=>{
 try{const result={};for(const [method,params] of requests)result[method]=await client.request(method,params,{timeoutMs:30000});console.log(JSON.stringify(result));}
 catch(e){console.error(e.message);process.exitCode=2;}
 finally{await client.stopAndWait();clearTimeout(timer)}
}});client.start();

