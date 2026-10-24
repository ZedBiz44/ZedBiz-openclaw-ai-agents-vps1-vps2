import sys
sys.argv=['accept','maintenance']
exec(open('/root/cody-vps2-followup-20261023/followup.py').read().split('if action==')[0])
B=Path('/root/cody-harry-mem0-20261024')
idle('harry')
plugins=obj(oc('harry',['plugins','list','--json'],'plugins'));mem=next(p for p in plugins['plugins'] if p['id']=='openclaw-mem0');assert mem['status']=='loaded'
prompt='Read-only memory verification after maintenance. Use mem0_search to recall one existing ZedBiz operational fact and briefly report whether it succeeded. Do not send messages, write files, explicitly add memories or delegate.'
d=obj(oc('harry',['agent','--agent','main','--session-key','agent:main:webchat:direct:cody-mem0-luna-20261024','--message',prompt,'--timeout','240','--json'],'agent-accept',300))
r=d['result']['meta']['agentMeta']['terminalReceipt'];assert not r['rerouted'] and r['effective']['model']=='gpt-6.1-sol' and 'mem0_search' in r['successfulToolNames']
health=obj(oc('harry',['gateway','call','health','--json'],'health'));assert health['ok']
assert urllib.request.urlopen('https://harry.zbiz.ca/healthz',timeout=15).status==200
result={'passed':True,'memoryPluginVersion':mem['version'],'receipt':r,'payloads':d['result'].get('payloads'),'health':health['ok']}
(B/'accept-result.json').write_text(json.dumps(result,indent=2));emit(result)
