import pathlib,subprocess,sys,json,concurrent.futures
b=pathlib.Path('/opt/openclaw/builds/vps1-email-20261003');names=sys.argv[1:]
def one(n):
 with (b/n/'rollout.log').open('w') as f:
  for args in [['python3',str(b/'activate-himalaya-v2.py'),n],['python3','/tmp/test-himalaya-v2.py','live',n],['python3',str(b/'email-agent-proof.py'),n]]:
   p=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
   if p.returncode:print(json.dumps({'agent':n,'success':False,'step':pathlib.Path(args[1]).name}),flush=True);return False
 print(json.dumps({'agent':n,'success':True}),flush=True);return True
for i in range(0,len(names),2):
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(one,names[i:i+2]))
 if not all(results):raise SystemExit('Paused rollout after a failed agent; inspect logs')
