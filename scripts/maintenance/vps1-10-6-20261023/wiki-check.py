"""Exercise 10.6 Wiki coordination on a disposable vault, never live Wiki data."""
import json,os,pathlib,subprocess
root=pathlib.Path('/opt/openclaw/recovery/release-20261023-core/wiki-proof');root.mkdir(mode=0o700,parents=True,exist_ok=True)
os.chown(root,1000,1000)
image='zedbiz/openclaw-base:2026.10.6-core-20261023'
base=['docker','run','--rm','--network','none','--memory','768m','--entrypoint','node','-v',str(root)+':/proof','-v','/home/jackadmin/vps1-10-6-20261023/wiki-lock/probe.mjs:/opt/zedbiz/wiki-lock/probe.mjs:ro',image,'/opt/zedbiz/wiki-lock/probe.mjs','/proof']
def call(action):
 p=subprocess.run(base+[action],capture_output=True,text=True)
 (root/(action+'.log')).write_text(p.stdout+p.stderr)
 return p
assert call('nested').returncode==0
assert call('throw').returncode!=0
assert call('nested').returncode==0,'Exception did not release lock'
(root/'counter').write_text('0');os.chown(root/'counter',1000,1000)
processes=[subprocess.Popen(base+['increment'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True) for _ in range(4)]
events=[]
for i,p in enumerate(processes):
 out,err=p.communicate();(root/('parallel-'+str(i)+'.log')).write_text(out+err);assert p.returncode==0
 entered=int(next(x.split()[1] for x in out.splitlines() if x.startswith('ENTER ')))
 left=int(next(x.split()[1] for x in out.splitlines() if x.startswith('LEAVE ')))
 events.append((entered,left))
events.sort();assert all(events[i][1]<=events[i+1][0] for i in range(len(events)-1))
assert (root/'counter').read_text()=='4'
result={'nested':True,'exceptionRelease':True,'fourContainerSerialization':True,'counter':4,'intervals':events,'vault':str(root)}
(root/'proof.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
