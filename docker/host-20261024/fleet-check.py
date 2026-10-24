"""Check actual gateway work/health and preserve schedule definitions privately."""
import pathlib,subprocess,json,time,os,sys
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/host-20261024');label=sys.argv[1];before=json.loads((W/'before.json').read_text());names=[n for n in before['containers'] if (P('/opt/openclaw/agents')/n/'config/openclaw.json').is_file()];assert len(names)==11
out=[];deadline=time.monotonic()+900
for n in names:
 while True:
  d=json.loads(subprocess.check_output(['docker','inspect',n]))[0]
  assert d['State']['Running'] and d['Image']==before['containers'][n]['image'] and not d['State']['OOMKilled'] and d['RestartCount']==0
  p=subprocess.run(['docker','exec','-i',n,'node','--input-type=module'],input=(W/'fleet-rpc.mjs').read_text(),capture_output=True,text=True,timeout=60)
  (W/(label+'-'+n+'.log')).write_text(p.stdout+p.stderr)
  if p.returncode==0:break
  assert time.monotonic()<deadline,n+' RPC readiness deadline';time.sleep(10)
 r=json.loads(p.stdout);(W/(label+'-'+n+'.json')).write_text(json.dumps(r,indent=2));assert r['health']['ok']
 active=r['status'].get('shutdownBudget',{}).get('activeWork');running=sum(bool(j.get('state',{}).get('runningAtMs')) for j in r['cron.list']['jobs'])
 row={'agent':n,'healthOk':True,'dockerHealth':d['State'].get('Health',{}).get('Status'),'activeWork':active,'runningSchedules':running,'scheduleCount':len(r['cron.list']['jobs']),'configuredChannels':{k:{'configured':v.get('configured'),'connected':v.get('connected'),'running':v.get('running'),'lastError':v.get('lastError')} for k,v in r['health'].get('channels',{}).items()}}
 out.append(row);print(json.dumps(row),flush=True)
(W/(label+'-fleet.json')).write_text(json.dumps(out,indent=2))

