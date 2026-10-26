"""Use each owning Gateway's real selected-provider tool; keep returned memories private."""
import pathlib,subprocess,json,time
P=pathlib.Path;W=P('/opt/openclaw/backups/shared-updates-20261026');assert json.loads((W/'update-hindsight/acceptance.json').read_text())['passed'];assert json.loads((W/'update-qdrant/acceptance.json').read_text())['passed'];A=W/'live-memory';A.mkdir(mode=0o700,exist_ok=True);code=P('/home/jackadmin/vps1-10-6-20261023/verify-live-memory-20261026.mjs').read_text();results=[]
for agent in ['terry','edith','marsha','gohzed','grogar','inga','maggie']:
 p=subprocess.run(['docker','exec','-i',agent,'node','--input-type=module'],input=code,capture_output=True,text=True,timeout=100);(A/(agent+'.private.json')).write_text(p.stdout+p.stderr);assert p.returncode==0,'Gateway memory tool process failed: '+agent;r=json.loads(p.stdout);assert r['status']==200 and r['body'].get('ok') is True,'Gateway memory tool failed: '+agent;payload=r['body']['result'];assert not payload.get('isError');details=payload.get('details',{});count=details.get('count');
 if count is None:
  if isinstance(details.get('results'),list):count=len(details['results'])
  elif isinstance(details.get('memories'),list):count=len(details['memories'])
 if count is None:
  for content in payload.get('content',[]):
   if content.get('type')!='text':continue
   try:
    body=json.loads(content['text']);count=len(body['results']) if isinstance(body.get('results'),list) else len(body['memories']) if isinstance(body.get('memories'),list) else body.get('count')
   except (ValueError,AttributeError):pass
 assert isinstance(count,int) and count>0,'Nonempty existing memories not established: '+agent
 row={'agent':agent,'passed':True,'provider':r['provider'],'tool':r['tool'],'existingMemoryCount':count,'ownGatewayToolUsed':True};results.append(row);(W/'vps1-live-memory-acceptance.json').write_text(json.dumps({'passed':len(results)==7,'agents':results},indent=2));print(json.dumps(row),flush=True)
