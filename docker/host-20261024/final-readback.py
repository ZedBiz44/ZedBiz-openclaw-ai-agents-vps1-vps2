"""Compare schedules, public routes and startup measurements after the real host reboot."""
import pathlib,json,subprocess,re,datetime,urllib.request,os
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/host-20261024');fleet=json.loads((W/'after-reboot-fleet.json').read_text());before=json.loads((W/'before.json').read_text());results=[]
keys=['id','name','description','enabled','agentId','schedule','payload','sessionTarget','wakeMode','deleteAfterRun','delivery','failureAlert']
norm=lambda jobs:{j['id']:{k:j.get(k) for k in keys} for j in jobs}
for row in fleet:
 n=row['agent'];old=json.loads((W/('before-reboot-'+n+'.json')).read_text());new=json.loads((W/('after-reboot-'+n+'.json')).read_text());assert norm(old['cron.list']['jobs'])==norm(new['cron.list']['jobs']),n+' schedule definitions changed'
 with urllib.request.urlopen('https://'+n+'.zbiz.ca/healthz',timeout=20) as response:status=response.status
 assert status==200,n+' public health failed'
 d=json.loads(subprocess.check_output(['docker','inspect',n]))[0];p=subprocess.run(['docker','logs',n],capture_output=True,text=True);log=p.stdout+p.stderr;(W/('post-reboot-'+n+'.log')).write_text(log)
 ready=re.search(r'^(\S+) \[gateway\] startup phase: ready .*?total=([\d.]+)ms',log,re.M);seconds=None
 if ready:
  parse=lambda s:datetime.datetime.fromisoformat(s.replace('Z','+00:00'));seconds=round((parse(ready[1])-parse(d['State']['StartedAt'])).total_seconds(),1)
 pid=d['State']['Pid'];root=P('/sys/fs/cgroup'+P('/proc/'+str(pid)+'/cgroup').read_text().strip().split('::')[-1]);s=dict((x,int(y)) for x,y in (line.split() for line in (root/'memory.stat').read_text().splitlines()))
 result={'agent':n,'publicHealth':status,'schedulesPreserved':True,'scheduleCount':len(new['cron.list']['jobs']),'wallSecondsToReady':seconds,'internalReadySeconds':round(float(ready[2])/1000,1) if ready else None,'restarts':d['RestartCount'],'oom':d['State']['OOMKilled'],'workingMiB':round((int((root/'memory.current').read_text())-s.get('inactive_file',0))/2**20,1),'anonMiB':round(s['anon']/2**20,1),'swapMiB':round(int((root/'memory.swap.current').read_text())/2**20,1),'channels':row['configuredChannels']};results.append(result)
 assert all(not c['configured'] or c['connected'] is not False for c in row['configuredChannels'].values()),n+' channel disconnected'
result={'passed':True,'timeUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'fleet':results,'maintenanceScope':'host packages and activation only; unchanged OpenClaw/shared-service images','comparisonLimit':'Post-reboot timings include a simultaneous fleet start; not controlled against the earlier isolated Marsha start'}
(W/'final-readback.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)

