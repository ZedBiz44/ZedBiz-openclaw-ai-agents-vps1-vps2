import subprocess,sys,json,concurrent.futures,pathlib
names=sys.argv[1:]
assert names and all(n in ['amanda','edith','gohzed','grogar','inga','maggie','victor','vivian','wilma'] for n in names)
root=pathlib.Path('/opt/openclaw/builds/2026.9.8-terry-20261003')
pilot=json.loads((root/'terry-oauth-sol-summary.json').read_text())
assert pilot['trace']['winnerModel']=='gpt-6.1-sol' and pilot['trace']['fallbackUsed'] is False
assert pilot['apiProfileRotationExcluded'] and pilot['tools']['failures']==0 and 'mem0_search' in pilot['tools']['tools']
for n in names:
 subprocess.run(['docker','cp','/tmp/apply-sol-oauth.mjs',n+':/tmp/apply-sol-oauth.mjs'],check=True)
 r=subprocess.run(['docker','exec',n,'node','/tmp/apply-sol-oauth.mjs',n],capture_output=True,text=True,check=True)
 (root/(n+'-oauth-apply.json')).write_text(r.stdout)
 print(r.stdout,flush=True)
def proof(n):
 p=subprocess.run(['python3','/tmp/vps1-oauth-proof.py',n],capture_output=True,text=True)
 print(json.dumps({'agent':n,'proofExit':p.returncode,'summary':p.stdout,'error':p.stderr[-800:]}),flush=True)
 return p.returncode
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(proof,names))
raise SystemExit(0 if all(x==0 for x in results) else 2)
