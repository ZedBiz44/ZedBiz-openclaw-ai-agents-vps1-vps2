"""Read-only, secret-safe runtime proof. Run on the Docker host."""
import json
import subprocess
import sys

agent = sys.argv[1]
js = r"""
const fs=require('fs');
const c=JSON.parse(fs.readFileSync('/home/node/.openclaw/openclaw.json'));
const port=c.gateway.port||18789;
const headers={'Content-Type':'application/json','Authorization':'Bearer '+c.gateway.auth.token};
(async()=>{
 const ready=await fetch('http://127.0.0.1:'+port+'/readyz');
 const r=await fetch('http://127.0.0.1:'+port+'/tools/invoke',{
 method:'POST',headers,body:JSON.stringify({tool:'wiki_search',args:{query:'ZedBiz',maxResults:1},sessionKey:'agent:main:main'})});
 const d=await r.json();
 console.log(JSON.stringify({ready:ready.status,http:r.status,ok:d.ok,result:d.result,error:d.error}));
})().catch(e=>{console.log(JSON.stringify({error:e.message}));process.exit(1)});
"""
guard = subprocess.run(['docker', 'exec', agent, 'python3', '/opt/zedbiz/wiki-lock/verify.py'], capture_output=True, text=True, timeout=30)
probe = subprocess.run(['docker', 'exec', agent, 'node', '-e', js], capture_output=True, text=True, timeout=150)
print(json.dumps({'agent':agent, 'guard':guard.returncode, 'wiki':probe.stdout.strip()}), flush=True)
try:
    channels = subprocess.run(['docker', 'exec', agent, 'openclaw', 'channels', 'status', '--json'], capture_output=True, text=True, timeout=60)
except subprocess.TimeoutExpired:
    print(json.dumps({'agent':agent,'discord':{'statusUnavailable':True,'reason':'startup or command timeout'}}), flush=True)
    sys.exit(1)
try:
    data = json.loads(channels.stdout[channels.stdout.index('{'):])
    discord = [{k: a.get(k) for k in ['running','connected','lifecycle','busy','activeRuns','lastError']} for a in data.get('channelAccounts',{}).get('discord',[])]
except (ValueError, KeyError):
    discord = {'statusUnavailable': True, 'exit': channels.returncode}
print(json.dumps({'agent':agent, 'discord':discord}), flush=True)
