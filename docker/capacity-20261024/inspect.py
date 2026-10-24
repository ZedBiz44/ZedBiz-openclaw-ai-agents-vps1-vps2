"""Read-only VPS1 disk and RAM attribution; writes protected diagnostic receipts only."""
import pathlib,subprocess,json,time,os,sys
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/capacity-20261024');W.mkdir(mode=0o700,exist_ok=True);action=sys.argv[1]
def cmd(a,timeout=900):
 p=subprocess.run(a,capture_output=True,text=True,timeout=timeout);assert p.returncode==0,(a[0]+' failed: '+p.stderr[:200]);return p.stdout
def kv(p):return {x[0].rstrip(':'):int(x[1]) for line in P(p).read_text().splitlines() if len(x:=line.split())>=2 and x[1].isdigit()}
def save(n,r):(W/(n+'.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if action=='ram':
 ids=cmd(['docker','ps','-q']).split();ds=json.loads(cmd(['docker','inspect',*ids]));rows=[]
 for d in ds:
  if (d['Config'].get('Labels') or {}).get('cody.capacity-helper')=='true':continue
  pid=d['State']['Pid'];root=P('/sys/fs/cgroup'+P('/proc/'+str(pid)+'/cgroup').read_text().strip().split('::')[-1]);s=kv(root/'memory.stat');procs=[]
  for file in root.rglob('cgroup.procs'):
   for num in file.read_text().split():
    pp=P('/proc')/num
    try:
     status=kv(pp/'status');sm=kv(pp/'smaps_rollup');name=(pp/'comm').read_text().strip();procs.append({'pid':int(num),'name':name,'pssKiB':sm.get('Pss',0),'privateKiB':sm.get('Private_Clean',0)+sm.get('Private_Dirty',0)})
    except (OSError,ProcessLookupError):pass
  unique={p['pid']:p for p in procs};procs=sorted(unique.values(),key=lambda p:-p['pssKiB'])
  rows.append({'name':d['Name'].lstrip('/'),'image':d['Config']['Image'],'started':d['State']['StartedAt'],'anonBytes':s.get('anon',0),'fileBytes':s.get('file',0),'kernelBytes':s.get('kernel',0),'currentBytes':int((root/'memory.current').read_text()),'workingBytes':int((root/'memory.current').read_text())-s.get('inactive_file',0),'swapBytes':int((root/'memory.swap.current').read_text()),'pssBytes':sum(x['pssKiB'] for x in procs)*1024,'processCount':len(procs),'topProcesses':procs[:5]})
 m=kv('/proc/meminfo');r={'timeUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'hostMeminfoKiB':{k:m.get(k) for k in ['MemTotal','MemFree','MemAvailable','Buffers','Cached','SReclaimable','SUnreclaim','Shmem','AnonPages','Slab','SwapTotal','SwapFree']},'free':cmd(['free','-m']),'pressure':P('/proc/pressure/memory').read_text(),'containers':sorted(rows,key=lambda x:-x['anonBytes']),'totals':{k:sum(x[k] for x in rows) for k in ['anonBytes','fileBytes','kernelBytes','currentBytes','workingBytes','pssBytes']},'sysstatFiles':[{'name':p.name,'bytes':p.stat().st_size,'mtime':p.stat().st_mtime} for p in P('/var/log/sysstat').glob('*') if p.is_file()]};save('ram',r)
elif action=='disk':
 r={'timeUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'df':cmd(['df','-B1','/']),'driver':cmd(['docker','info','--format','{{json .DriverStatus}}']),'du':{}}
 for label,roots,depth in [('openclaw',['/opt/openclaw'],2),('varlib',['/var/lib'],1),('home',['/home/jackadmin'],1),('varlog',['/var/log'],1)]:
  output=cmd(['nice','-n','19','ionice','-c','3','du','-x','-B1','--max-depth='+str(depth),*roots]);(W/('du-'+label+'.txt')).write_text(output);r['du'][label]=sorted([{'bytes':int(a),'path':b} for line in output.splitlines() for a,b in [line.split('\t',1)]],key=lambda x:-x['bytes'])[:40]
 r['dockerSystemDf']=cmd(['docker','system','df']);r['imageRows']=[json.loads(x) for x in cmd(['docker','images','--format','{{json .}}']).splitlines()];r['buildCache']=cmd(['docker','builder','du'],timeout=300)[-6000:];save('disk',r)
else:raise SystemExit('Unknown action')

