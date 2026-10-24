"""Verify the deployed Marsha artifacts, readiness, preservation and resource samples."""
import pathlib,subprocess,json,time,re,hashlib,urllib.request,os
P=pathlib.Path;os.umask(0o077);w=P('/opt/openclaw/backups/release-20261024-marsha');live=P('/opt/openclaw/agents/marsha');a=w/'activation';candidate=json.loads((w/'build.json').read_text());start=time.monotonic()
def inspect(n):return json.loads(subprocess.check_output(['docker','inspect',n]))[0]
def run(args):return subprocess.run(args,capture_output=True,text=True)
samples=[];readyAt=None
for _ in range(200):
 d=inspect('marsha');assert d['State']['Running'] and d['Image']==candidate['candidateId']
 p=run(['docker','logs','marsha']);log=p.stdout+p.stderr
 pid=d['State']['Pid'];root=P('/sys/fs/cgroup'+P('/proc/'+str(pid)+'/cgroup').read_text().strip().split('::')[-1]);stats={x[0]:int(x[1]) for line in (root/'memory.stat').read_text().splitlines() if len(x:=line.split())==2}
 samples.append({'elapsed':round(time.monotonic()-start,1),'anonMiB':round(stats['anon']/2**20,1),'workingMiB':round((int((root/'memory.current').read_text())-stats.get('inactive_file',0))/2**20,1),'swapMiB':round(int((root/'memory.swap.current').read_text())/2**20,1)})
 if d['State'].get('Health',{}).get('Status')=='healthy' and 'startup phase: sidecars.subagent-recovery' in log:
  readyAt=readyAt or time.monotonic()
  if time.monotonic()-readyAt>=30:break
 time.sleep(3)
else:raise RuntimeError('Marsha did not reach complete startup readiness')
assert d['RestartCount']==0 and not d['State']['OOMKilled']
side=inspect('marsha-asana-mcp');assert side['Image']=='sha256:7702a34a7cc329f7dc7422ba919c67263fe488d5633285d69ef602a52c530d6c' and side['State']['Health']['Status']=='healthy'
versions={}
for key,args in {'core':['node','/app/openclaw.mjs','--version'],'node':['node','--version'],'codex':['codex','--version'],'gemini':['gemini','--version'],'npm':['npm','--version'],'gog':['gog','--version'],'mcporter':['mcporter','--version'],'summarize':['summarize','--version']}.items():
 p=run(['docker','exec','marsha',*args]);assert p.returncode==0,key+' failed';versions[key]=p.stdout.strip().splitlines()[0]
assert versions['node']=='v24.22.1' and '2026.10.6' in versions['core']
assert '0.164.0' in versions['codex'] and '0.65.0' in versions['gemini']
assert run(['python3',str(w/'rpc-run.py'),'marsha','post-cutover']).returncode==0
r=json.loads((w/'post-cutover-rpc.json').read_text());assert r['health']['ok']
before=json.loads((w/'pre-cutover-rpc.json').read_text())['cron.list']['jobs'];after=r['cron.list']['jobs']
retired={j['id'] for j in before if j.get('name') in ['skill-collection-review-mail_reader','skill-collection-review-main']}
keys=['id','name','description','enabled','agentId','schedule','payload','sessionTarget','wakeMode','deleteAfterRun','delivery','failureAlert']
norm=lambda jobs:{j['id']:{k:j.get(k) for k in keys} for j in jobs if j['id'] not in retired}
assert norm(before)==norm(after),'User schedule definitions changed'
manifest=json.loads(P('/opt/openclaw/recovery/fleet-20261018/marsha/manifest.json').read_text());assert manifest['archive']=='/opt/openclaw/recovery/release-20261024-marsha/images.tar.gz'
for f in manifest['images']:assert inspect(f['ref'])['Id']==f['id']
for tool in ['gog','mcporter','summarize']:
 assert any(m['Source']=='/opt/openclaw/shared/tools-20261023/bin/'+tool+'-wrapper' for m in d['Mounts'])
# Check the already-built Marsha-only patch against its retained image manifest.
code="""const fs=require('fs'),crypto=require('crypto');const m=JSON.parse(fs.readFileSync('/opt/zedbiz/marsha-10-6-originals/manifest.json','utf8'));console.log(JSON.stringify({passed:m.every(x=>crypto.createHash('sha256').update(fs.readFileSync('/app/'+x.file)).digest('hex')===x.after)}))"""
p=run(['docker','exec','marsha','node','-e',code]);assert p.returncode==0 and json.loads(p.stdout)['passed']
cfg=json.loads((live/'config/openclaw.json').read_text());original=json.loads((w/'config-before.json').read_text());memory=cfg['plugins']['entries']['hindsight-openclaw']['config'];assert all(memory.get(k)==v for k,v in original['plugins']['entries']['hindsight-openclaw']['config'].items()) and memory['allowKnowledgeDelete'] is False
phases=[{'phase':m[1],'ms':float(m[2]),'totalMs':float(m[3])} for m in re.finditer(r'startup phase: (\S+) ([\d.]+)ms total=([\d.]+)ms',log)]
ports=[]
for values in d['NetworkSettings']['Ports'].values():
 for b in values or []:
  if b['HostIp'] in ['0.0.0.0','127.0.0.1']:
   try:
    with urllib.request.urlopen('http://127.0.0.1:'+b['HostPort']+'/healthz',timeout=5) as resp:ports.append({'port':b['HostPort'],'status':resp.status})
   except Exception:pass
assert any(p['status']==200 for p in ports),'Published gateway health route failed'
with (a/'gateway-first-start.log').open('w') as f:f.write(log)
proof={'passed':True,'versions':versions,'gatewayId':d['Image'],'sidecarId':side['Image'],'restarts':d['RestartCount'],'oom':d['State']['OOMKilled'],'retainedSchedules':len(after),'retiredBuiltinReviewJobs':len(retired),'protectedScheduleDefinitionsPreserved':True,'marshaSchedulingPatchVerified':True,'productionMemoryPolicyPreserved':True,'publishedHealth':ports,'phases':phases,'resourceSamples':samples,'activeWorkAtSample':r['status'].get('shutdownBudget',{}).get('activeWork')}
(w/'live-runtime-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)

