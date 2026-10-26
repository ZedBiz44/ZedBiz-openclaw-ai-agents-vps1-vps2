"""Check expanded tools on Terry's restored state; no inbound work or memory writes."""
import json,os,pathlib,subprocess,sys,time
os.umask(0o077)
w=pathlib.Path('/opt/openclaw/backups/release-20261023/terry');stage=w/'rehearsal'
out=w/'tools-rehearsal';out.mkdir(exist_ok=True)
name='release-20261023-terry-tools';action=sys.argv[1]
config=stage/'config/openclaw.json';saved=out/'config-before.json'
if action=='start':
 assert not saved.exists(),'Inspect existing rehearsal before repeating'
 for cid in subprocess.check_output(['docker','ps','-q'],text=True).split():
  d=json.loads(subprocess.check_output(['docker','inspect',cid]))[0]
  assert not any(m['Source'].startswith(str(stage)+'/') for m in d['Mounts'])
 saved.write_bytes(config.read_bytes());c=json.loads(config.read_text())
 c.setdefault('cron',{})['enabled']=False;c.setdefault('hooks',{})['enabled']=False
 c['hooks'].setdefault('internal',{})['enabled']=False
 c['agents']['defaults'].setdefault('heartbeat',{})['every']='0m'
 for a in [*c['agents'].get('list',[]),*c['agents'].get('entries',{}).values()]:a.setdefault('heartbeat',{})['every']='0m'
 c['plugins']['entries']['openclaw-mem0']['config']['autoCapture']=False
 config.write_text(json.dumps(c,indent=2)+'\n')
 args=['docker','run','-d','--name',name,'--network','openclaw','--network','mem0-dev_mem0_network','--memory','3g','--env-file',str(w/'runtime.env'),'--user','node','--entrypoint','node']
 for key in ['OPENCLAW_SKIP_CHANNELS','OPENCLAW_SKIP_CRON','OPENCLAW_SKIP_GMAIL_WATCHER','OPENCLAW_DISABLE_BONJOUR']:args+=['-e',key+'=1']
 live='/opt/openclaw/agents/terry/'
 for m in json.loads((w/'mounts-before.json').read_text()):
  src=m['Source'];dst=m['Destination']
  if src in ['/var/run/docker.sock','/dev/shm']:continue
  if src.startswith(live):src=str(stage/src[len(live):]);mode='' if m['RW'] else ':ro'
  else:mode=':ro'
  if src in ['/opt/openclaw/shared/bin/'+x for x in ['gog','mcporter','summarize']]:src='/opt/openclaw/shared/tools-20261023/bin/'+pathlib.Path(src).name+'-wrapper'
  args+=['-v',src+':'+dst+mode]
 args+=['-v',str(w/'gateway-wiki')+':/opt/openclaw/shared/knowledge/wiki','zedbiz/openclaw-base:2026.10.6-tools-full-20261023','/app/openclaw.mjs','gateway','run','--port','3010','--bind','loopback']
 subprocess.run(args,check=True,stdout=subprocess.DEVNULL);print('Started isolated tools gateway',flush=True)
elif action=='probe':
 d=json.loads(subprocess.check_output(['docker','inspect',name]))[0];assert d['State']['Health']['Status']=='healthy'
 def run(label,argv):
  p=subprocess.run(['docker','exec',name,*argv],capture_output=True,text=True)
  (out/(label+'.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed; inspect private log'
  return p.stdout
 for tool in ['codex','gemini','gog','mcporter','summarize']:run(tool,[tool,'--version'])
 run('drive',['gog','--readonly','--no-input','--json','drive','ls','--max','1'])
 prompt='Read-only tools upgrade rehearsal. Through your Codex connection use Notion fetch to read page 37ba3e33d581816584cdf6b622a0d944, use native Asana to get your own user identity, and mem0_search to recall one existing memory. Return only tool names and success. Do not send messages, edit files or pages, create tasks, store memories, or delegate.'
 t=run('model',['node','/app/openclaw.mjs','agent','--agent','main','--session-key','agent:main:cody-tools-proof','--message',prompt,'--json'])
 r=json.loads(t[t.index('{'):]);receipt=r['result']['meta']['agentMeta']['terminalReceipt']
 assert r['status']=='ok' and not r['result']['meta']['aborted'] and not receipt['rerouted']
 assert {'codex_apps.notion.fetch','asana.asana_get_user','mem0_search'}<=set(receipt['successfulToolNames'])
 (out/'proof.json').write_text(json.dumps({'passed':True,'receipt':receipt,'memoryCaptureDisabledForReadOnlyFixture':True,'geminiAuthenticatedInferenceStillPending':True},indent=2));print('Tools read/model proof passed',flush=True)
elif action=='stop':
 with (out/'gateway.log').open('w') as f:subprocess.run(['docker','logs',name],stdout=f,stderr=subprocess.STDOUT,check=True)
 subprocess.run(['docker','stop',name],check=True,stdout=subprocess.DEVNULL);subprocess.run(['docker','rm',name],check=True,stdout=subprocess.DEVNULL)
 config.write_bytes(saved.read_bytes());print('Stopped tools fixture and restored its saved config',flush=True)
else:raise SystemExit('Expected start, probe, stop')
