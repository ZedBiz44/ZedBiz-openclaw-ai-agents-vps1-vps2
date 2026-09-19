"""One explicit untimed deliverable; never schedules a successor or retries a run."""
from pathlib import Path
from datetime import datetime,timezone
import json,sqlite3,fcntl,subprocess,sys,re
ROOT=Path('/home/node/.openclaw')
def main():
 label,brief=sys.argv[1:]
 assert re.fullmatch('[a-z0-9-]+',label)
 brief=Path(brief).resolve();assert brief.parent==ROOT/'workspace/scripts' and brief.is_file()
 out=ROOT/'private/edith-dispatch'/('authorized-'+label+'.json')
 assert not out.exists(),'Existing attempt must be reconciled; no automatic retry'
 with (out.parent/'worker.lock').open('a+') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  db=sqlite3.connect('file:'+str(ROOT/'agents/main/agent/openclaw-agent.sqlite')+'?mode=ro',uri=True)
  assert not db.execute("select session_key from session_nodes where status='running'").fetchall(),'Existing Edith run active'
  key='agent:main:authorized-'+label
  record={'started':datetime.now(timezone.utc).isoformat(),'status':'running','session_key':key,'model':'openai/gpt-5.6-terra','reasoning':'medium','timeout':0,'automatic_restart':False}
  out.write_text(json.dumps(record,indent=2))
  with out.with_suffix('.result.json').open('w') as result,out.with_suffix('.stderr.log').open('w') as err:
   r=subprocess.run(['openclaw','agent','--agent','main','--session-key',key,'--model','openai/gpt-5.6-terra','--thinking','medium','--timeout','0','--message-file',str(brief),'--json'],cwd=str(ROOT/'workspace'),stdin=subprocess.DEVNULL,stdout=result,stderr=err)
  record.update(status='returned',exit_code=r.returncode,ended=datetime.now(timezone.utc).isoformat());out.write_text(json.dumps(record,indent=2));print(json.dumps(record))
if __name__=='__main__':main()

