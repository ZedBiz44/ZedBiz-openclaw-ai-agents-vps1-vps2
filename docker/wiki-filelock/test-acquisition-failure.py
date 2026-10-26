"""A failed/killed acquisition helper must never admit the writer."""
import json,pathlib,subprocess,sys,time
P=pathlib.Path;ROOT=P(__file__).resolve().parent;image=sys.argv[1]
fixture=ROOT/('acquisition-faults-'+str(int(time.time())));fixture.mkdir();fixture.chmod(0o777)
js="import {acquireWikiLock} from '/opt/zedbiz/wiki-lock/lock.mjs'; try {const release=await acquireWikiLock('/fixture'); await release(); console.log('UNSAFE-ENTRY'); process.exitCode=2;} catch(e) {console.log('REJECTED');}"
proof={}
for kind,code in [('failure','raise SystemExit(1)'),('killed','import os,signal;os.kill(os.getpid(),signal.SIGKILL)')]:
 stub=fixture/(kind+'.py');stub.write_text(code+'\n')
 p=subprocess.run(['docker','run','--rm','--network','none','-v',str(fixture)+':/fixture','-v',str(stub)+':/opt/zedbiz/wiki-lock/acquire-lock.py:ro','--entrypoint','node',image,'--input-type=module','-e',js],capture_output=True,text=True,timeout=30)
 assert p.returncode==0 and p.stdout.strip()=='REJECTED',(kind,p.stdout,p.stderr)
 proof[kind+'HelperRejectedBeforeEntry']=True
(ROOT/'acquisition-failure-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))
