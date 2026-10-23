"""Sequential rollout runner; stops on failed verification. Run on VPS1."""
import json
import pathlib
import subprocess
import sys
import time

ROOT = '/opt/openclaw/recovery/wiki-lock-20261023'
ports = {'amanda':3000,'victor':3002,'wilma':3003,'inga':3004,'marsha':3005,'gohzed':3006,'grogar':3007,'maggie':3008,'vivian':3009,'terry':3010,'edith':3011}

def root_run(args):
    p = subprocess.run(['docker','run','--rm','--network','host','-v','/:/host','alpine','chroot','/host','python3',ROOT+'/deploy.py',*args],capture_output=True,text=True,timeout=600)
    print(p.stdout.strip(),flush=True)
    if p.returncode:
        print(p.stderr[-1200:],flush=True)
        raise SystemExit('Deployment stopped')

for agent in sys.argv[1:]:
    # Existing pilot and Grogar were activated interactively.
    if agent not in ['gohzed','grogar']:
        status = subprocess.run(['docker','exec',agent,'openclaw','channels','status','--json'],capture_output=True,text=True,timeout=90)
        data=json.loads(status.stdout[status.stdout.index('{'):])
        accounts=data.get('channelAccounts',{}).get('discord',[])
        if not accounts or any(a.get('busy') or a.get('activeRuns',0) for a in accounts):
            raise SystemExit(agent+': active work or unavailable channel status; stopped before replacement')
        root_run([agent,'stage'])
        root_run([agent,'activate'])
    for attempt in range(36):
        try:
            js = "fetch('http://127.0.0.1:"+str(ports[agent])+"/readyz',{signal:AbortSignal.timeout(5000)}).then(r=>console.log(r.status)).catch(()=>process.exit(1))"
            ready = subprocess.run(['docker','exec',agent,'node','-e',js],capture_output=True,text=True,timeout=10)
            if ready.returncode==0 and ready.stdout.strip()=='200':break
        except Exception:
            pass
        if attempt%3==0:print(agent,'waiting for startup',attempt*10,'seconds',flush=True)
        time.sleep(10)
    else:
        raise SystemExit(agent+': readiness did not pass; stopped rollout')
    p=subprocess.run(['python3','/tmp/zedbiz-wiki-lock-20261023/check-live.py',agent],capture_output=True,text=True,timeout=250)
    print(p.stdout,flush=True)
    if p.returncode:raise SystemExit(agent+': verification command failed; stopped rollout')
    rows=[json.loads(line) for line in p.stdout.splitlines() if line.startswith('{')]
    wiki=json.loads(rows[0]['wiki'])
    discord=rows[1]['discord']
    if rows[0]['guard']!=0 or wiki.get('ready')!=200 or not wiki.get('ok') or not isinstance(discord,list) or not discord or not all(a.get('connected') for a in discord):
        raise SystemExit(agent+': verification failed; stopped rollout')
    print(agent,'VERIFIED',flush=True)
