// Calls the running Gateway; avoids preparing a second complete plugin runtime.
import fs from 'node:fs';
import {t as GatewayClient} from '/app/dist/client-CEQLDSRp.mjs';
const config=JSON.parse(fs.readFileSync('/home/node/.openclaw/openclaw.json','utf8'));
let token=config.gateway?.auth?.token;
if(typeof token==='string'&&token.startsWith('${'))token=process.env[token.slice(2,-1)];
const request=JSON.parse(process.env.CODY_RPC_REQUEST);
const timer=setTimeout(()=>{console.error('RPC deadline');process.exit(2)},750000);
let client;
client=new GatewayClient({url:`ws://127.0.0.1:${config.gateway.port}`,token,sharedStateMode:'read-only',clientName:'cli',mode:'cli',scopes:['operator.admin'],onConnectError:async e=>{console.error(e.message);clearTimeout(timer);await client.stopAndWait();process.exitCode=2;},onHelloOk:async()=>{
 try{console.log(JSON.stringify(await client.request(request.method,request.params??{},{timeoutMs:650000,...request.options})));}
 catch(e){console.error(e.message);process.exitCode=2;}
 finally{await client.stopAndWait();clearTimeout(timer);}
}});client.start();
