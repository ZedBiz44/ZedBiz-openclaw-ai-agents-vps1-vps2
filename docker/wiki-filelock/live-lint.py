"""Invoke the real lint transaction concurrently through three live gateways."""
import concurrent.futures,json,pathlib,subprocess,time
ROOT=pathlib.Path('/opt/openclaw/recovery/wiki-filelock-20261026')
JS=r'''
const fs=require('fs');const c=JSON.parse(fs.readFileSync('/home/node/.openclaw/openclaw.json'));
(async()=>{const r=await fetch('http://127.0.0.1:'+(c.gateway.port||18789)+'/tools/invoke',{method:'POST',signal:AbortSignal.timeout(300000),headers:{'Content-Type':'application/json',Authorization:'Bearer '+c.gateway.auth.token},body:JSON.stringify({tool:'wiki_lint',args:{},sessionKey:'agent:main:main'})});
const d=await r.json();const counts=[];
function walk(x){if(!x||typeof x!=='object')return;for(const [k,v] of Object.entries(x)){if(k==='issueCount')counts.push(v);else if(k==='text'&&typeof v==='string'){try{walk(JSON.parse(v))}catch{}}else if(typeof v==='object')walk(v)}}walk(d.result);
console.log(JSON.stringify({http:r.status,ok:d.ok,isError:d.result?.isError===true,issueCounts:counts}));})().catch(()=>process.exit(1));
'''
def probe(agent):
 start=time.time();p=subprocess.run(['docker','exec',agent,'node','-e',JS],capture_output=True,text=True,timeout=320)
 assert p.returncode==0,agent+' lint request failed';d=json.loads(p.stdout);assert d['http']==200 and d['ok'] and not d['isError'],d
 return {'agent':agent,'started':start,'finished':time.time(),**d}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(probe,['gohzed','grogar','inga']))
(ROOT/'live-lint-proof.json').write_text(json.dumps({'passed':True,'concurrentGatewayInvocations':3,'results':rows},indent=2));print(json.dumps(rows),flush=True)
