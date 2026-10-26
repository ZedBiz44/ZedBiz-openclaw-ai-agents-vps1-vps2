"""Read back final runtime/resource/channel state without printing credentials."""
import pathlib,subprocess,json,time,os,hashlib
P=pathlib.Path;os.umask(0o077);w=P('/opt/openclaw/backups/release-20261024-marsha')
def inspect(n):return json.loads(subprocess.check_output(['docker','inspect',n]))[0]
d=inspect('marsha');pid=d['State']['Pid'];root=P('/sys/fs/cgroup'+P('/proc/'+str(pid)+'/cgroup').read_text().strip().split('::')[-1]);s=dict((x,int(y)) for x,y in (line.split() for line in (root/'memory.stat').read_text().splitlines()))
assert d['State']['Health']['Status']=='healthy' and d['RestartCount']==0 and not d['State']['OOMKilled']
assert subprocess.run(['python3',str(w/'rpc-run.py'),'marsha','final'],capture_output=True).returncode==0
r=json.loads((w/'final-rpc.json').read_text());assert r['health']['ok']
skills=json.loads((w/'skills-before.json').read_text());base=P('/opt/openclaw/agents/marsha');assert all(hashlib.sha256((base/p).read_bytes()).hexdigest()==h for p,h in skills.items())
fleet=[]
for n in ['terry','edith','amanda','victor','vivian','wilma','gohzed','grogar','inga','maggie','marsha']:
 x=inspect(n);fleet.append({'agent':n,'image':x['Config']['Image'],'health':x['State'].get('Health',{}).get('Status'),'restarts':x['RestartCount'],'oom':x['State']['OOMKilled']})
fixtures=[]
for n in ['cody-marsha-hindsight-1-0','release-20261023-hindsight-rehearsal-api','release-20261023-hindsight-rehearsal-db']:
 x=inspect(n);fixtures.append({'name':n,'running':x['State']['Running']})
result={'passed':True,'timeUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'anonMiB':round(s['anon']/2**20,1),'workingMiB':round((int((root/'memory.current').read_text())-s.get('inactive_file',0))/2**20,1),'totalMiB':round(int((root/'memory.current').read_text())/2**20,1),'swapMiB':round(int((root/'memory.swap.current').read_text())/2**20,1),'activeWork':r['status'].get('shutdownBudget',{}).get('activeWork'),'customSkillFilesPreserved':len(skills),'channels':r['health'].get('channels'),'fleet':fleet,'fixtures':fixtures,'disk':subprocess.check_output(['df','-h','/'],text=True),'hostMemory':subprocess.check_output(['free','-m'],text=True)}
(w/'final-proof.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)

