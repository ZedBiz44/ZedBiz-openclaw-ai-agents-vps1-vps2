"""Invoke a verification tool inside one live agent without exposing credentials."""
import json
import subprocess
import sys
import time

agent, tool = sys.argv[1:3]
args = json.loads(sys.argv[3]) if len(sys.argv)>3 else {}
js = r"""
const fs=require('fs');
const c=JSON.parse(fs.readFileSync('/home/node/.openclaw/openclaw.json'));
(async()=>{
 const r=await fetch('http://127.0.0.1:'+(c.gateway.port||18789)+'/tools/invoke',{
 method:'POST',signal:AbortSignal.timeout(120000),headers:{'Content-Type':'application/json',Authorization:'Bearer '+c.gateway.auth.token},
 body:JSON.stringify({tool:process.argv[1],args:JSON.parse(process.argv[2]),sessionKey:'agent:main:main'})});
 const d=await r.json();console.log(JSON.stringify({http:r.status,...d}));
})().catch(e=>{console.log(JSON.stringify({error:e.message}));process.exit(1)});
"""
started=time.time()
p=subprocess.run(['docker','exec',agent,'node','-e',js,tool,json.dumps(args)],capture_output=True,text=True,timeout=140)
try:
    result=json.loads(p.stdout)
except ValueError:
    result={'parseFailed':True,'exit':p.returncode}
print(json.dumps({'agent':agent,'tool':tool,'started':started,'finished':time.time(),'result':result}),flush=True)
