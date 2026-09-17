import assert from 'node:assert/strict';
const url='http://127.0.0.1:8080/mcp';
const headers={'Content-Type':'application/json',Accept:'application/json, text/event-stream',Authorization:'Bearer isolated-test-only'};
const body=JSON.stringify({jsonrpc:'2.0',id:1,method:'tools/list',params:{}});
for(const method of ['POST','GET','DELETE']) {
  for(const [session,expected] of [[null,400],['expired-or-unknown',404]]) {
    const r=await fetch(url,{method,headers:{...headers,...(session?{'Mcp-Session-Id':session}:{})},...(method==='POST'?{body}:{}),signal:AbortSignal.timeout(5000)});
    assert.equal(r.status,expected);await r.text();
    console.log(`${method} ${session?'unknown':'missing'} session: ${expected}`);
  }
  const r=await fetch(url,{method,headers:{...headers,Authorization:'Bearer wrong'},...(method==='POST'?{body}:{}),signal:AbortSignal.timeout(5000)});
  assert.equal(r.status,401);await r.text();
}
const init=await fetch(url,{method:'POST',headers,body:JSON.stringify({jsonrpc:'2.0',id:2,method:'initialize',params:{protocolVersion:'2024-11-05',capabilities:{},clientInfo:{name:'expiry-test',version:'1'}}}),signal:AbortSignal.timeout(5000)});
assert.equal(init.status,200);const sid=init.headers.get('mcp-session-id');assert.ok(sid);await init.text();
const list=await fetch(url,{method:'POST',headers:{...headers,'Mcp-Session-Id':sid},body,signal:AbortSignal.timeout(5000)});
assert.equal(list.status,200);assert.match(await list.text(),/asana_get_user/);
await new Promise(r=>setTimeout(r,6500));
const stale=await fetch(url,{method:'POST',headers:{...headers,'Mcp-Session-Id':sid},body,signal:AbortSignal.timeout(5000)});
assert.equal(stale.status,404);await stale.text();
console.log('PASS initialization, authenticated catalog, expiry, missing ID and auth boundaries');
