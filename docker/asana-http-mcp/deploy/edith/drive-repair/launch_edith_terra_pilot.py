"""One explicitly requested Edith pilot session; no restart or successor loop."""
import fcntl, json, os, sqlite3, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path('/home/node/.openclaw')
def now():return datetime.now(timezone.utc).isoformat()
def main():
    label=sys.argv[1]
    assert label in ('a','b')
    receipt=ROOT/'private/edith-dispatch'/('terra-pilot-'+label+'-20260918.json')
    assert not receipt.exists(), 'Inspect the existing pilot receipt before another launch'
    db=sqlite3.connect('file:'+str(ROOT/'agents/main/agent/openclaw-agent.sqlite')+'?mode=ro',uri=True)
    assert not db.execute("select session_key from session_nodes where status='running'").fetchall(), 'Another Edith session is active'
    with (ROOT/'private/edith-dispatch/worker.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=ROOT/'private/folder-cleanup/laughs-and-fun/execution-state.json'
        def counts():
            d=json.loads(state.read_text());return {'proofs':len(d['copies']),'unique':len({x['active_id'] for x in d['copies'].values()}),'archived':len(d['archived'])}
        key='agent:main:edith-terra-pilot-'+label+'-20260918'
        r={'started':now(),'status':'running','session_key':key,'model':'openai/gpt-5.6-terra','thinking':'medium','timeout':0,'before':counts(),'pid':os.getpid(),'automatic_restart':False}
        receipt.write_text(json.dumps(r,indent=2))
        with receipt.with_suffix('.result.json').open('w') as out,receipt.with_suffix('.stderr.log').open('w') as err:
            process=subprocess.Popen(['openclaw','agent','--agent','main','--session-key',key,'--model','openai/gpt-5.6-terra','--thinking','medium','--timeout','0','--message-file',str(ROOT/'workspace/scripts'/('edith-terra-pilot-'+label+'.md')),'--json'],stdout=out,stderr=err)
            r['client_pid']=process.pid;receipt.write_text(json.dumps(r,indent=2))
            code=process.wait()
        r.update(status='returned',exit_code=code,ended=now(),after=counts());receipt.write_text(json.dumps(r,indent=2))
        print(json.dumps(r))
if __name__=='__main__':main()

