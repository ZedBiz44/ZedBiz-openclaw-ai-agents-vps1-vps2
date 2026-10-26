"""Host-side tests: actual shipped bundle in independent Docker PID namespaces."""
import json, pathlib, subprocess, time, sys
P=pathlib.Path
ROOT=P(__file__).resolve().parent
IMAGE=sys.argv[1]
OLD=sys.argv[2]
OUT=ROOT/('test-results-'+str(int(time.time())));OUT.mkdir()
def call(args,**kw):return subprocess.run(args,capture_output=True,text=True,timeout=90,**kw)
def setup(name):
 p=OUT/name;p.mkdir();p.chmod(0o777);return p
def start(vault,id,action='hold',duration=150,image=IMAGE):
 name='wiki-v2-test-'+id
 args=['docker','run','--rm','--network','none','--name',name,'-v',str(ROOT)+':/fixture','--entrypoint','node',image,'/fixture/test-worker.mjs','/fixture/'+OUT.name+'/'+vault.name,id,action,str(duration)]
 return subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True),name
def rows(v):return [json.loads(x) for x in (v/'events').read_text().splitlines()] if (v/'events').exists() else []
def entered(v,id):
 until=time.monotonic()+45
 while not any(x['id']==id and x['kind']=='ENTER' for x in rows(v)):
  assert time.monotonic()<until,'worker did not enter';time.sleep(.1)
def finish(job,code=0):
 p,name=job;out,err=p.communicate(timeout=75)
 assert p.returncode==code,(name,p.returncode,err[-2000:])
def serial(v):
 held=None
 for row in rows(v):
  if row['kind']=='ENTER':assert held is None,rows(v);held=row['id']
  if row['kind']=='LEAVE':assert held==row['id'];held=None
 assert held is None
if '--holder-only' in sys.argv:
 proof=json.loads((ROOT/'test-proof.json').read_text())
else:
 proof={}
 v=setup('concurrent');a=start(v,'a',duration=20000);entered(v,'a')
 jobs=[start(v,str(i),'nested' if i==0 else 'hold') for i in range(3)]
 finish(a)
 for j in jobs:finish(j)
 serial(v);assert (v/'counter').read_text()=='4';proof['fourContainersAndNested']=True
 v=setup('timeout');a=start(v,'holder',duration=20000);entered(v,'holder');finish(start(v,'timeout','timeout'),2);finish(a)
 assert [r['kind'] for r in rows(v) if r['id']=='timeout']==['TIMEOUT'];proof['timeoutNoEntry']=True
 v=setup('exception');finish(start(v,'throw','throw'),2);finish(start(v,'afterthrow'));assert (v/'counter').read_text()=='1';proof['exceptionRelease']=True
 v=setup('crash');a=start(v,'crash',duration=60000);entered(v,'crash')
 assert call(['docker','kill',a[1]]).returncode==0;finish(a,137);finish(start(v,'aftercrash'));assert (v/'counter').read_text()=='1';proof['parentCrashRelease']=True
 for generation,first,second in [('old-new',OLD,IMAGE),('new-old',IMAGE,OLD)]:
  v=setup(generation);a=start(v,generation+'a',duration=20000,image=first);entered(v,generation+'a');b=start(v,generation+'b',image=second);finish(a);finish(b);serial(v);assert (v/'counter').read_text()=='2';proof[generation]=True
 (ROOT/'test-proof.json').write_text(json.dumps(proof,indent=2))
v=setup('no-helper');a=start(v,'nohelper',duration=20000);entered(v,'nohelper')
p=call(['docker','top',a[1],'-eo','pid,args']);assert p.returncode==0 and 'acquire-lock.py' not in p.stdout and 'hold-lock.py' not in p.stdout,(p.returncode,p.stdout,p.stderr);finish(a);proof['noHolderHelperAfterAcquisition']=True
(ROOT/'test-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
