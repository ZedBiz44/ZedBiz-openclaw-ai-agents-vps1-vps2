"""Validate actual returned memories and stored schedule definitions after live tool acceptance."""
import pathlib,json,subprocess,sqlite3,os,re,sys
P=pathlib.Path;os.umask(0o077);agent=sys.argv[1];A=P('/opt/openclaw/backups/fleet-10-6-20261024')/agent;M=P('/opt/openclaw/backups/mem0-repair-20261024-r2');proof=json.loads((A/'acceptance.json').read_text());assert proof['passed'];slot=proof['memoryProvider']
before=json.loads((A/'cron-before.json').read_text());columns=before['columns'];di=columns.index('declaration_key');ji=columns.index('job_id');pj=columns.index('job_json')
def definition(text):return json.dumps({k:v for k,v in json.loads(text).items() if k not in ['state','updatedAtMs']},sort_keys=True)
old=sorted((r[ji],definition(r[pj])) for r in before['rows'] if not str(r[di]).startswith('skill-collection-review:'))
db=sqlite3.connect('file:/opt/openclaw/agents/'+agent+'/config/state/openclaw.sqlite?mode=ro',uri=True)
try:current=sorted((i,definition(j)) for i,j in db.execute('select job_id,job_json from cron_jobs'))
finally:db.close()
assert current==old,'Stored user schedule definitions differ after startup'
key='agent:main:main' if slot=='hindsight-openclaw' else 'agent:main:cody-upgrade-live-20261024';req={'method':'chat.history','params':{'sessionKey':key,'limit':60}}
p=subprocess.run(['docker','exec','-i','-e','CODY_RPC_REQUEST='+json.dumps(req),agent,'node','--input-type=module'],input=(M/'rpc.mjs').read_text(),capture_output=True,text=True,timeout=90);assert p.returncode==0,'Maintenance history unavailable';o=json.loads(p.stdout);(A/'live-acceptance/history.private.json').write_text(p.stdout)
messages=o.get('messages',[])
def userText(m):
 c=m.get('content','');return c if isinstance(c,str) else '\n'.join(x.get('text','') for x in c if isinstance(x,dict))
starts=[i for i,m in enumerate(messages) if m.get('role')=='user' and 'Read-only upgrade acceptance.' in userText(m)];assert starts,'Maintenance turn not located';messages=messages[starts[-1]+1:];end=next((i for i,m in enumerate(messages) if m.get('role')=='user'),len(messages));messages=messages[:end]
tools=[m for m in messages if m.get('role')=='toolResult'];tool='hindsight_recall' if slot=='hindsight-openclaw' else 'mem0_search' if slot=='openclaw-mem0' else 'memory_recall';results=[]
for m in tools:
 if m.get('toolName')!=tool or m.get('isError'):continue
 text='\n'.join(x.get('text','') for x in m.get('content',[]) if isinstance(x,dict))
 if slot=='hindsight-openclaw':count=len(re.findall(r'(?m)^\d+\.\s+\S',text))
 else:
  found=re.search(r'Found\s+(\d+)\s+(?:relevant\s+)?memor',text,re.I);count=int(found.group(1)) if found else 0
 if count>0:results.append((count,text))
assert results,'Successful memory call did not yet prove a nonempty existing-memory read'
count,text=results[-1]
if slot=='openclaw-mem0':
 ids=set(re.findall(r'[a-f0-9]{8}-[a-f0-9-]{27,}',text));gets=[m for m in tools if m.get('toolName')=='mem0_get' and not m.get('isError')];assert gets
 assert any(ids&set(re.findall(r'[a-f0-9]{8}-[a-f0-9-]{27,}','\n'.join(x.get('text','') for x in m.get('content',[]) if isinstance(x,dict)))) for m in gets),'Get did not read a searched memory identifier'
proof.update(actualMemoryResultValidated=True,recalledExistingMemories=count,storedScheduleDefinitionsCompared=True);(A/'acceptance.json').write_text(json.dumps(proof,indent=2));print(json.dumps({'agent':agent,'actualMemoryResultValidated':True,'recalledExistingMemories':count,'storedScheduleDefinitionsPreserved':len(current)}),flush=True)
