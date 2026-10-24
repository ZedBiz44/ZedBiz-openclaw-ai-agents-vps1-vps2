import pathlib,subprocess,json,os,sys
os.umask(0o077);P=pathlib.Path;w=P('/opt/openclaw/backups/release-20261024-marsha')
name=sys.argv[1];label=sys.argv[2]
assert name in ['marsha','cody-marsha-10-6-rehearsal']
d=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
env=w/(label+'-rpc-runtime.env');env.write_text('\n'.join(d['Config']['Env'])+'\n')
a=['docker','run','--rm','-i','--pid=container:'+name,'--network','container:'+name,'--memory','512m','--user','node','--env-file',str(env),'--entrypoint','node','-e','CODY_RPC_HOST=127.0.0.1']
for m in d['Mounts']:
 if m['Destination'].startswith('/home/node/.openclaw'):a+=['-v',m['Source']+':'+m['Destination']+':ro']
a+=['zedbiz/openclaw-base:2026.10.6-core-20261023','--input-type=module']
p=subprocess.run(a,input=(w/'rpc.mjs').read_text(),capture_output=True,text=True);(w/(label+'-rpc.log')).write_text(p.stdout+p.stderr)
assert p.returncode==0,'Gateway RPC failed; inspect private log'
r=json.loads(p.stdout);(w/(label+'-rpc.json')).write_text(json.dumps(r))
print(json.dumps({'agent':name,'activeWork':r['status'].get('shutdownBudget',{}).get('activeWork'),'jobs':[{'id':j.get('id'),'name':j.get('name'),'enabled':j.get('enabled'),'running':bool(j.get('state',{}).get('runningAtMs'))} for j in r['cron.list']['jobs']],'healthOk':r['health'].get('ok')}))

