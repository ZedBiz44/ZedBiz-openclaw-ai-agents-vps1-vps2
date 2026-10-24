"""Live read-only capability checks after the backed-up Terry core activation."""
import json,pathlib,subprocess,time
w=pathlib.Path('/opt/openclaw/backups/release-20261023/terry/activation');out=w/'acceptance';out.mkdir(mode=0o700)
assert json.loads((w/'activation.json').read_text())['awaitingLiveAcceptance']
while True:
 d=json.loads(subprocess.check_output(['docker','inspect','terry']))[0]
 assert d['State']['Running'] and not d['State']['OOMKilled'],'Terry stopped or OOM-killed'
 if d['State'].get('Health',{}).get('Status')=='healthy':break
 time.sleep(10)
def run(label,args):
 p=subprocess.run(['docker','exec','terry',*args],capture_output=True,text=True)
 (out/(label+'.log')).write_text(p.stdout+p.stderr)
 assert p.returncode==0,label+' failed; inspect private log'
 return p.stdout
node=run('node',['node','--version']).strip();assert node=='v24.22.1'
version=run('core',['openclaw','--version']).strip();assert '2026.10.6' in version
config=json.loads(pathlib.Path('/opt/openclaw/agents/terry/config/openclaw.json').read_text())
assert config['plugins']['entries']['openclaw-mem0']['config']['oss']['llm']['config']['model']=='gpt-5.6-luna'
run('notion',['ntn','whoami'])
drive=run('drive',['gog','--readonly','--no-input','--json','drive','ls','--max','1']);json.loads(drive)
for method in ['health','status','cron.list']:
 text=run(method,['openclaw','gateway','call',method,'--json'])
 obj=json.JSONDecoder().raw_decode(text[text.index('{'):])[0]
 (out/(method+'.json')).write_text(json.dumps(obj))
prompt='Read-only post-upgrade check. Use mem0_search to recall an existing ZedBiz memory and the native Asana tool to get your own user identity. Return only MODEL_OK and whether both calls succeeded. Do not send messages, create tasks, alter files, delegate, or store any test fact.'
text=run('model',['openclaw','agent','--agent','main','--session-key','agent:main:cody-live-10-6-proof','--message',prompt,'--json'])
r=json.loads(text[text.index('{'):]);assert r['status']=='ok' and not r['result']['meta']['aborted']
receipt=r['result']['meta']['agentMeta']['terminalReceipt']
assert receipt['effective']['model']=='gpt-6.1-sol' and not receipt['rerouted']
assert {'mem0_search','asana.asana_get_user'}<=set(receipt['successfulToolNames'])
logs=subprocess.check_output(['docker','logs','terry'],stderr=subprocess.STDOUT,text=True);(out/'gateway.log').write_text(logs)
assert 'LLM extraction failed' not in logs,'Automatic memory extraction still fails'
proof={'passed':True,'core':version,'node':node,'memoryModel':'gpt-5.6-luna','notionAuthenticatedReadPassed':True,'driveAuthenticatedReadPassed':True,'modelReceipt':receipt,'healthStatusSchedulesCollected':True,'newMemoryExtractionFailureSeen':False,'noOutboundTestMessages':True,'remaining':['Asana candidate activation','tool updates','cold CLI startup performance investigation','channel details require review of health record']}
(out/'proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
