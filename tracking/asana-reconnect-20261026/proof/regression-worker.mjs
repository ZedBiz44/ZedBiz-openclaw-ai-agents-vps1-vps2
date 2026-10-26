import {ln as initSecureTemp,un as resolveSecureTempRoot} from '/app/dist/worker/worker-chunk-BubafzsH.mjs';
import {i as registerSealedRuntime} from '/app/dist/worker/worker-chunk-CdQdj6U8.mjs';
import json5 from '/app/node_modules/json5/lib/index.js';
initSecureTemp();registerSealedRuntime({json5,resolveSecureTempRoot});
import assert from 'node:assert/strict';
import http from 'node:http';
import {Client} from '/app/node_modules/@modelcontextprotocol/sdk/dist/esm/client/index.js';
import {createSessionMcpRuntime} from '/app/dist/worker/worker-chunk-D6AJSTHa.mjs';
import {n as withSignal} from '/app/dist/agent-bundle-mcp-request-context-905XWHsu.mjs';
let expired=false, toolFail=false, slowLists=false, connections=0, calls=0, capturedClient;
const connect=Client.prototype.connect;
Client.prototype.connect=async function(...args){capturedClient=this;return connect.apply(this,args);};
const server=http.createServer(async(req,res)=>{
 if(req.method==='GET'){res.writeHead(405);res.end();return;}
 if(req.method==='DELETE'){res.writeHead(200);res.end();return;}
 let body='';for await(const c of req)body+=c;let q;try{q=JSON.parse(body);}catch{res.writeHead(400);res.end();return;}
 const send=(result,error)=>{res.writeHead(200,{'content-type':'application/json'});res.end(JSON.stringify({jsonrpc:'2.0',id:q.id,...(error?{error}:{result})}));};
 if(q.method==='initialize'){connections++;await new Promise(r=>setTimeout(r,100));res.setHeader('mcp-session-id','fixture-'+connections);send({protocolVersion:'2025-03-26',capabilities:{tools:{}},serverInfo:{name:'fixture',version:'1'}});return;}
 if(q.method==='notifications/initialized'){res.writeHead(202);res.end();return;}
 if(q.method==='tools/list'){if(slowLists)await new Promise(r=>setTimeout(r,150));send({tools:[{name:'identity',description:'Fixture',inputSchema:{type:'object',properties:{}}}]});return;}
 if(q.method==='tools/call'){
  calls++;
  if(expired){expired=false;res.writeHead(404,{'content-type':'application/json'});res.end(JSON.stringify({jsonrpc:'2.0',id:q.id,error:{code:-32001,message:'Session not found'}}));return;}
  if(toolFail){toolFail=false;send(null,{code:-32603,message:'fixture tool failure'});return;}
  send({content:[{type:'text',text:'pass'}]});return;
 }
 res.writeHead(400);res.end();
});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const cfg={mcp:{servers:{fixture:{transport:'streamable-http',url:`http://127.0.0.1:${server.address().port}/mcp`}}}};
const runtime=createSessionMcpRuntime({cfg,sessionId:'isolated-regression',sessionKey:'agent:main:main',workspaceDir:'/tmp',agentDir:'/tmp'});
const passed=[];
try{
 await runtime.getCatalog();await runtime.callTool('fixture','identity',{});assert.equal(calls,1);passed.push('connected call passes');
 expired=true;await assert.rejects(runtime.callTool('fixture','identity',{}),/Session not found/);assert.equal(calls,2);passed.push('expired tool request fails once without replay');
 await runtime.callTool('fixture','identity',{});assert.equal(calls,3);assert.equal(connections,2);passed.push('next requested call awaits reconnect and executes once');
 toolFail=true;await assert.rejects(runtime.callTool('fixture','identity',{}),/fixture tool failure/);await new Promise(r=>setTimeout(r,150));assert.equal(calls,4);passed.push('ordinary tool failure remains failed without replay');
 const signal=AbortSignal.abort(new Error('fixture cancellation'));await assert.rejects(withSignal(signal,()=>runtime.callTool('fixture','identity',{})),/fixture cancellation/);assert.equal(calls,4);passed.push('already-aborted caller never dispatches');
 slowLists=true;expired=true;await assert.rejects(runtime.callTool('fixture','identity',{}),/Session not found/);assert.equal(calls,5);
 const first=runtime.callTool('fixture','identity',{});await new Promise(r=>setTimeout(r,130));const second=runtime.callTool('fixture','identity',{});await Promise.all([first,second]);assert.equal(calls,7);assert.equal(connections,3);passed.push('parallel callers during slow reconnect catalog await full metadata and dispatch exactly once each');
 // Direct transport-close SDK capture is covered in readable runtime; worker bundles its own SDK.
 console.log(JSON.stringify({passed:passed.length,tests:passed,toolCalls:calls,connections,noLiveChange:true},null,2));
}finally{Client.prototype.connect=connect;await runtime.dispose();server.closeAllConnections();await new Promise(r=>server.close(r));}
