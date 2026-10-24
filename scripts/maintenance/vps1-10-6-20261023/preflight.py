"""Private live baseline; stdout contains only selected non-secret fields."""
import hashlib,json,os,pathlib,subprocess,time
ROOT=pathlib.Path('/opt/openclaw/backups/release-20261023')
os.umask(0o077);ROOT.mkdir(mode=0o700,parents=True,exist_ok=True)
names='terry edith amanda victor vivian wilma gohzed grogar inga maggie marsha'.split()
def run(args):
 p=subprocess.run(args,capture_output=True,text=True)
 return p
rows=[]
for name in names:
 p=pathlib.Path('/opt/openclaw/agents')/name
 c=json.loads((p/'config/openclaw.json').read_text())
 d=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
 s=json.loads(subprocess.check_output(['docker','inspect',name+'-asana-mcp']))[0]
 m=pathlib.Path('/opt/openclaw/recovery')/(name+'-20261018')/'manifest.json'
 if not m.exists():m=pathlib.Path('/opt/openclaw/recovery/fleet-20261018')/name/'manifest.json'
 recovery=json.loads(m.read_text())
 row={'agent':name,'image':d['Config']['Image'],'imageId':d['Image'],'sidecarImage':s['Config']['Image'],'sidecarId':s['Image'],
 'healthy':d['State'].get('Health',{}).get('Status'),'restarts':d['RestartCount'],'oom':d['State']['OOMKilled'],
 'memoryLimit':d['HostConfig']['Memory'],'memoryProvider':c.get('plugins',{}).get('slots',{}).get('memory'),
 'enabledPlugins':sorted(k for k,v in c.get('plugins',{}).get('entries',{}).items() if v.get('enabled')),
 'recoveryManifest':str(m),'wrapperHashMatches':hashlib.sha256(pathlib.Path(recovery['wrapper']).read_bytes()).hexdigest()==recovery['wrapper_sha256']}
 rows.append(row)
(ROOT/'fleet-before.json').write_text(json.dumps(rows,indent=2))
print(json.dumps({'fleet':rows}),flush=True)
work=ROOT/'terry';work.mkdir(mode=0o700,exist_ok=True)
for method,params in [('status',None),('cron.list',{'includeDisabled':True}),('health',None)]:
 args=['docker','exec','terry','openclaw','gateway','call',method,'--json']
 if params:args+=['--params',json.dumps(params)]
 p=run(args);(work/(method+'-before.log')).write_text(p.stdout+p.stderr)
 assert p.returncode==0,'RPC failed; inspect private capture '+method
 d=json.JSONDecoder().raw_decode(p.stdout[p.stdout.index('{'):])[0]
 (work/(method+'-before.json')).write_text(json.dumps(d,indent=2))
 if method=='status':print(json.dumps({'terryActiveWork':d.get('shutdownBudget',{}).get('activeWork')}),flush=True)
 if method=='cron.list':print(json.dumps({'terryJobs':len(d['jobs']),'runningJobs':sum(bool(j.get('state',{}).get('runningAtMs')) for j in d['jobs'])}),flush=True)
p=run(['docker','exec','terry','openclaw','doctor','--lint','--json']);(work/'doctor-before.log').write_text(p.stdout+p.stderr)
try:
 d=json.JSONDecoder().raw_decode(p.stdout[p.stdout.index('{'):])[0]
 (work/'doctor-before.json').write_text(json.dumps(d,indent=2))
 print(json.dumps({'doctorExit':p.returncode,'doctorKeys':list(d)}),flush=True)
except ValueError:print(json.dumps({'doctorExit':p.returncode,'doctorJson':False}),flush=True)

