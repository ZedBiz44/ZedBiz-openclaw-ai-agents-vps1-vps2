import os, sys, json, subprocess, time, signal, shutil, hashlib, urllib.request
from pathlib import Path
B=Path('/root/cody-vps2-followup-20261023'); B.mkdir(exist_ok=True,mode=0o700); os.umask(0o077)
action=sys.argv[1]
def emit(x): print(json.dumps(x),flush=True)
def run(args,**kw): return subprocess.run(args,check=True,**kw)
def context(n):
 s=Path('/root/.openclaw-'+n); e=os.environ.copy();e.update(HOME=str(s),OPENCLAW_STATE_DIR=str(s),OPENCLAW_CONFIG_PATH=str(s/'openclaw.json'),OP_SERVICE_ACCOUNT_TOKEN=(s/'.op.token').read_text().strip(),NODE_OPTIONS='--max-old-space-size=1536')
 return e,['op','run','--no-masking','--env-file='+str(s/'.env'),'--']
def oc(n,args,label,timeout=300):
 e,p=context(n); f=B/(n+'-'+label+'.log')
 with f.open('w') as o:run(p+['/opt/openclaw-'+n+'/node_modules/.bin/openclaw',*args],env=e,stdout=o,stderr=subprocess.STDOUT,timeout=timeout)
 return f
def obj(p):
 t=p.read_text();return json.JSONDecoder().raw_decode(t[t.index('{'):])[0]
def idle(n):
 port={'frank':4300,'harry':4100,'suzy':4200}[n]
 for _ in range(84):
  try:
   if urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/healthz',timeout=3).status==200:break
  except Exception:time.sleep(5)
 else:raise RuntimeError('Gateway readiness deadline')
 for _ in range(60):
  d=obj(oc(n,['gateway','call','status','--json'],'idle'))
  a=d.get('shutdownBudget',{}).get('activeWork');assert a is not None,'Unknown work state: '+n
  if all(v==0 for v in a.values()):return
  time.sleep(10)
 raise RuntimeError('Active work did not drain: '+n)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def verify_asana(n,url,root):
 p=root/'verify-followup.mjs'
 t=(root/'verify-vps2-agent.mjs').read_text().replace('me.email !== expectedEmail','me.gid !== expectedEmail')
 p.write_text(t)
 e,pre=context(n);gid={'frank':'1215596271715682','harry':'1215559750337835','suzy':'1215557534470003'}[n]
 f=B/(n+'-asana-'+('pilot' if '4917' in url else 'live')+'.json')
 with f.open('w') as out:run(pre+['node',str(p),n,url,gid],env=e,stdout=out,stderr=subprocess.STDOUT,timeout=120)
 emit(obj(f))
if action=='asana-pilot':
 root=B/'asana-candidate';e,p=context('frank')
 with (B/'asana-pilot.log').open('w') as out:
  proc=subprocess.Popen(p+['env','PORT=4917','MCP_BIND_HOST=127.0.0.1','node',str(root/'dist/index.js')],env=e,stdout=out,stderr=subprocess.STDOUT,start_new_session=True)
  try:
   for _ in range(30):
    try:
     if urllib.request.urlopen('http://127.0.0.1:4917/healthz').status==200:break
    except Exception:time.sleep(1)
   else:raise RuntimeError('pilot did not start')
   verify_asana('frank','http://127.0.0.1:4917/mcp',root)
  finally:
   os.killpg(proc.pid,signal.SIGTERM);proc.wait(timeout=30)
elif action=='asana-install':
 assert obj(B/'frank-asana-pilot.json')['ok']
 for n in ['frank','harry','suzy']:idle(n)
 root=Path('/opt/zedbiz-asana-http-mcp');candidate=B/'asana-candidate'
 for leaf in ['node_modules','dist']:
  (root/leaf).rename(B/('asana-old-'+leaf));shutil.copytree(candidate/leaf,root/leaf,symlinks=True)
 for leaf in ['package.json','package-lock.json']:shutil.copy2(candidate/leaf,root/leaf)
 for n,port in [('frank',4310),('harry',4110),('suzy',4210)]:
  run(['systemctl','restart','zedbiz-asana-mcp@'+n]);time.sleep(2)
  # Resolve the existing MCP URL from configuration; do not invent routing.
  c=json.loads(Path('/root/.openclaw-'+n+'/openclaw.json').read_text())
  servers=c.get('mcp',{}).get('servers',{});s=servers.get('asana',{})
  url=s.get('url') or s.get('serverUrl')
  assert url,'Missing Asana URL'
  verify_asana(n,url,root)
elif action=='accept':
 n=sys.argv[2]
 port={'frank':4300,'harry':4100,'suzy':4200}[n]
 for _ in range(84):
  try:
   if urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/healthz',timeout=3).status==200:break
  except Exception:time.sleep(5)
 else:raise RuntimeError('Gateway readiness deadline')
 prompt='Read-only maintenance verification. Use your memory to recall one existing ZedBiz fact (Harry: explicitly use mem0_search; Frank/Suzy: use supplied Hindsight memory). Get your own Asana identity, fetch Notion page ee1a3e33d58183948bd58119d92c7d01, and list 3 Google Drive items using your existing gog account routing; report only count. Run version checks for gog, gh, ntn, summarize, mcporter, codex and gemini. Do not send messages, modify files, explicitly store memories or delegate. Report failures plainly.'
 started=int(time.time());d=obj(oc(n,['agent','--agent','main','--session-key','agent:main:webchat:direct:cody-followup-20261023','--message',prompt,'--timeout','240','--json'],'acceptance',300))
 r=d['result']['meta']['agentMeta']['terminalReceipt'];assert r['rerouted'] is False and r['effective']['model']=='gpt-6.1-sol'
 names=r['successfulToolNames'];assert any('asana_get_user' in v for v in names) and any('notion' in v and 'fetch' in v for v in names)
 if n=='harry':assert any('mem0_search' in v for v in names)
 else:
  logs=subprocess.check_output(['journalctl','-u','openclaw-'+n,'--since','@'+str(started),'-o','cat','--no-pager'],text=True)
  assert any('hindsight' in l.lower() and 'inject' in l.lower() for l in logs.splitlines()),'No Hindsight injection'
 result={'accepted':True,'agent':n,'receipt':r,'payloads':d['result'].get('payloads')};(B/(n+'-accepted.json')).write_text(json.dumps(result,indent=2));emit(result)
else:raise ValueError(action)
