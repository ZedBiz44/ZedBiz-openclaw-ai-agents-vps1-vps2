"""One observed native Edith turn; no successor, loop or periodic LLM checks."""
import fcntl, importlib.util, json, os, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT=Path('/home/node/.openclaw/private/edith-dispatch')
SCRIPTS=Path('/home/node/.openclaw/workspace/scripts')
GID='1218611177927226'
SESSION='agent:main:edith-uninterrupted-test-20260917'
def now():return datetime.now(timezone.utc).isoformat()
def main():
    receipt=ROOT/'natural-test-20260917.json'
    assert not receipt.exists(), 'Inspect prior test; never launch a duplicate'
    with (ROOT/'worker.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        spec=importlib.util.spec_from_file_location('natural_test_transport',SCRIPTS/'edith-project-dispatch.py')
        d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
        d.connect();t=d.get_task(GID)
        assert t['assignee']['gid']==d.EDITH and not t['completed']
        assert d.eligible(t,d.EDITH,lambda dep:d.call('asana_get_task',{'task_id':dep,'opt_fields':'completed,resource_subtype,approval_status'}))=='eligible'
        assert d.get_task('1218611357802915')['completed'], 'Old backup must stay cancelled'
        assert (ROOT/'production-paused-by-jack.json').exists(), 'Old dispatcher must remain disabled'
        state=Path('/home/node/.openclaw/private/folder-cleanup/laughs-and-fun/execution-state.json')
        before=json.loads(state.read_text())
        r={'started':now(),'status':'running','task':GID,'session_key':SESSION,'supervisor_pid':os.getpid(),
           'before':{'copies':len(before['copies']),'archived':len(before['archived']),'folders':len(before['folders'])},
           'scheduled_successor':None,'automatic_restart':False,'cli_ceiling_seconds':7200}
        receipt.write_text(json.dumps(r,indent=2))
        with (ROOT/'natural-test-20260917.result.json').open('w') as out, (ROOT/'natural-test-20260917.stderr.log').open('w') as err:
            p=subprocess.Popen(['openclaw','agent','--agent','main','--session-key',SESSION,
                '--message-file',str(SCRIPTS/'edith-natural-test-prompt.txt'),'--timeout','7200','--json'],stdout=out,stderr=err)
            r['client_pid']=p.pid;receipt.write_text(json.dumps(r,indent=2))
            code=p.wait()
        after=json.loads(state.read_text())
        r.update(status='returned',exit_code=code,ended=now(),after={'copies':len(after['copies']),'archived':len(after['archived']),'folders':len(after['folders'])})
        receipt.write_text(json.dumps(r,indent=2))
if __name__=='__main__':main()

