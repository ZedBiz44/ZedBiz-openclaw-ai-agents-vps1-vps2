import json,pathlib,sys
j=json.loads(pathlib.Path(sys.argv[1]).read_text())
r=j.get('result',j);m=r.get('meta',{})
print(json.dumps({'status':j.get('status'),'runId':j.get('runId'),'trace':m.get('executionTrace'),'tools':m.get('toolSummary'),'reply':m.get('finalAssistantVisibleText'),'agentMeta':{k:v for k,v in m.get('agentMeta',{}).items() if k in ['provider','model','runtime','terminalReceipt']}},indent=2))
