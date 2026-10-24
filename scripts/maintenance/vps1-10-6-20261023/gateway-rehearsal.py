"""Exercise production's warm gateway path on restored state without inbound work."""
import json,os,pathlib,shutil,subprocess,sys
os.umask(0o077)
work=pathlib.Path('/opt/openclaw/backups/release-20261023/terry');stage=work/'rehearsal'
live=pathlib.Path('/opt/openclaw/agents/terry');name='release-20261023-terry-gateway'
config=stage/'config/openclaw.json';saved=work/'gateway-rehearsal-config-before.json'
action=sys.argv[1]
if action=='start':
 assert not saved.exists(),'Rehearsal already prepared; inspect existing phase'
 shutil.copy2(config,saved);c=json.loads(config.read_text())
 c.setdefault('cron',{})['enabled']=False
 c.setdefault('hooks',{})['enabled']=False
 c['hooks'].setdefault('internal',{})['enabled']=False
 c['agents']['defaults'].setdefault('heartbeat',{})['every']='0m'
 for agent in [*c['agents'].get('list',[]),*c['agents'].get('entries',{}).values()]:agent.setdefault('heartbeat',{})['every']='0m'
 config.write_text(json.dumps(c,indent=2)+'\n')
 wiki=work/'gateway-wiki';assert not wiki.exists()
 subprocess.run(['cp','-a','/opt/openclaw/shared/knowledge/wiki',str(wiki)],check=True)
 assert not any(p.is_symlink() for p in wiki.rglob('*')),'Review Wiki links before isolated writes'
 args=['docker','run','-d','--name',name,'--network','mem0-dev_mem0_network','--network','openclaw','--memory','3g','--env-file',str(work/'runtime.env'),'--user','node','--entrypoint','node']
 for key in ['OPENCLAW_SKIP_CHANNELS','OPENCLAW_SKIP_CRON','OPENCLAW_SKIP_GMAIL_WATCHER','OPENCLAW_DISABLE_BONJOUR','OPENCLAW_PLUGIN_LOAD_DEBUG']:args+=['-e',key+'=1']
 for m in json.loads((work/'mounts-before.json').read_text()):
  src=m['Source'];dst=m['Destination']
  if src in ['/var/run/docker.sock','/dev/shm']:continue
  if src.startswith(str(live)+'/'):
   src=str(stage/src[len(str(live))+1:]);mode='' if m['RW'] else ':ro'
  else:mode=':ro'
  args+=['-v',src+':'+dst+mode]
 args+=['-v',str(wiki)+':/opt/openclaw/shared/knowledge/wiki','zedbiz/openclaw-base:2026.10.6-core-20261023','/app/openclaw.mjs','gateway','run','--port','3010','--bind','loopback']
 subprocess.run(args,check=True,stdout=subprocess.DEVNULL)
 print(json.dumps({'started':name,'restoredStateOnly':True,'channelsCronHooksHeartbeatsDisabled':True,'wikiIsolated':True,'hostPortsPublished':False}),flush=True)
elif action=='probe':
 d=json.loads(subprocess.check_output(['docker','inspect',name]))[0];assert d['State']['Health']['Status']=='healthy','Wait for gateway readiness'
 prompt='Read-only upgrade rehearsal. Use mem0_search to recall an existing ZedBiz memory, then use the native Asana MCP tool to get your own user identity. Return only MODEL_OK, the names of the tools used, and whether both calls succeeded. Do not send messages, create memories, modify files, create tasks, or delegate.'
 with (work/'gateway-rehearsal-model.log').open('w') as out:
  p=subprocess.run(['docker','exec',name,'node','/app/openclaw.mjs','agent','--agent','main','--session-key','agent:main:cody-10-6-rehearsal','--message',prompt,'--json'],stdout=out,stderr=subprocess.STDOUT)
 (work/'gateway-rehearsal-probe-receipt.json').write_text(json.dumps({'exit':p.returncode,'privateLog':str(work/'gateway-rehearsal-model.log')}));print('Probe exit',p.returncode,flush=True)
 sys.exit(p.returncode)
elif action=='stop':
 if subprocess.run(['docker','inspect',name],capture_output=True).returncode==0:
  with (work/'gateway-rehearsal.log').open('w') as out:subprocess.run(['docker','logs',name],stdout=out,stderr=subprocess.STDOUT,check=True)
  subprocess.run(['docker','stop',name],check=True,stdout=subprocess.DEVNULL)
  subprocess.run(['docker','rm',name],check=True,stdout=subprocess.DEVNULL)
 assert saved.exists();shutil.copy2(saved,config)
 print('Isolated gateway stopped; original rehearsal configuration restored',flush=True)
else:raise SystemExit('Expected start, probe, stop')
