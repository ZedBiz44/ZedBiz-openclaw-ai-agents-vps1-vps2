import json,pathlib,subprocess,time,sys
name=sys.argv[1]
attempt_suffix=sys.argv[2] if len(sys.argv)>2 else ''
assert name in ['amanda','edith','gohzed','grogar','inga','maggie','terry','victor','vivian','wilma']
w=pathlib.Path('/opt/openclaw/builds/2026.9.8-terry-20261003');stable=0
c=json.loads(subprocess.check_output(['docker','exec',name,'cat','/home/node/.openclaw/openclaw.json']))
assert c['agents']['defaults']['model']['primary']=='openai/gpt-6.1-sol@openai:jzedbiz@gmail.com'
assert c['auth']['order']['openai']==['openai:jzedbiz@gmail.com']
assert c['plugins']['entries']['codex']['config']['appServer']['command']=='/usr/local/bin/codex'
port=c['gateway']['port']
for _ in range(80):
 p=subprocess.run(['docker','exec',name,'curl','-fsS','--max-time','3',f'http://127.0.0.1:{port}/healthz'],capture_output=True)
 stable=stable+1 if p.returncode==0 else 0
 if stable>=3:break
 time.sleep(5)
else:raise SystemExit('Gateway did not settle')
prompt=w/(name+'-proof-message.txt')
memory_tool='agent_knowledge_recall' if name in ['gohzed','grogar','inga','maggie'] else 'mem0_search' if name in ['terry','edith'] else 'memory_recall'
prompt.write_text('Run a harmless shell tool to read /etc/os-release. Then use '+memory_tool+' for a short read-only lookup of VPS1 in your external memory. Do not send messages, create memories, or change files. Report the OS and whether the memory lookup succeeded. Use actual tools, not a description of intended calls.')
subprocess.run(['docker','cp',str(prompt),name+':/tmp/cody-sol-proof.txt'],check=True)
with open(w/(name+'-oauth-sol-default.json'),'w') as out,open(w/(name+'-oauth-sol-default.stderr'),'w') as err:
 p=subprocess.run(['docker','exec',name,'openclaw','agent','--agent','main','--session-key','agent:main:cody-oauth-sol-20261003-9-8-'+memory_tool+attempt_suffix,'--message-file','/tmp/cody-sol-proof.txt','--timeout','180','--json'],stdout=out,stderr=err,timeout=240)
j=json.loads((w/(name+'-oauth-sol-default.json')).read_text());m=j.get('result',{}).get('meta',{})
trace=m.get('executionTrace',{});tool=m.get('toolSummary',{})
result={'agent':name,'configuredAuthProfile':'openai:jzedbiz@gmail.com','apiProfileRotationExcluded':True,'cliExit':p.returncode,'runId':j.get('runId'),'status':j.get('status'),'trace':trace,'tools':tool,'reply':m.get('finalAssistantVisibleText'),'receipt':m.get('agentMeta',{}).get('terminalReceipt')}
(w/(name+'-oauth-sol-summary.json')).write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
if p.returncode!=0 or trace.get('winnerModel')!='gpt-6.1-sol' or trace.get('fallbackUsed') is not False or tool.get('failures')!=0 or tool.get('calls',0)<2 or memory_tool not in tool.get('tools',[]):raise SystemExit(2)
