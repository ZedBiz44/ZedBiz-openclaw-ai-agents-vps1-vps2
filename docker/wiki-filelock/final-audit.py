"""Read back deployed images, persistent gates, recovery pins and shared lock identity."""
import hashlib,json,pathlib,subprocess
P=pathlib.Path;ROOT=P('/opt/openclaw/recovery/wiki-filelock-20261026');rows=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inventory=json.loads((ROOT/'inventory.json').read_text());images=json.loads((ROOT/'images.json').read_text())
archive=json.loads((ROOT/'archive.json').read_text())
with P(archive['archive']).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==archive['sha256'],'Recovery archive checksum changed'
for row in inventory:
 agent=row['agent'];base=P('/opt/openclaw/agents')/agent;image=next(i for i in images if i['agent']==agent)
 d=json.loads(subprocess.check_output(['docker','inspect',agent]))[0]
 assert d['Image']==image['id'] and d['State']['Health']['Status']=='healthy'
 assert any('post-start.sh &&' in arg for arg in d['Config']['Cmd']),'Startup command must gate gateway launch on post-start success'
 assert sha(base/'config/openclaw.json')==row['configSha'] and sha(P(row['wrapper']))==row['wrapperSha']
 assert 'filelock-fd-v2' in (base/'workspace/post-start.sh').read_text()
 m=json.loads(P(row['manifest']).read_text());a=json.loads((ROOT/'archive.json').read_text());assert m['archive']==a['archive'] and m['sha256']==a['sha256']
 assert any(i['id']==image['id'] and i['ref']==image['after'] for i in m['images'])
 for i in m['images']:assert json.loads(subprocess.check_output(['docker','image','inspect',i['ref']]))[0]['Id']==i['id']
 js="const fs=require('fs');const s=fs.statSync('/opt/openclaw/shared/knowledge/wiki/.openclaw-wiki/zedbiz-mutation.flock');console.log(JSON.stringify({dev:s.dev,ino:s.ino}));"
 lock=json.loads(subprocess.check_output(['docker','exec',agent,'node','-e',js]))
 assert lock=={'dev':2049,'ino':1059413},lock
 assert json.loads((ROOT/(agent+'-acceptance.json')).read_text())['passed']
 status=subprocess.run(['docker','exec',agent,'openclaw','channels','status','--json'],capture_output=True,text=True,timeout=90);assert status.returncode==0,agent+' channel check failed'
 accounts=json.loads(status.stdout[status.stdout.index('{'):]).get('channelAccounts',{});assert accounts
 checked={}
 for channel,values in accounts.items():
  active=[a for a in values if a.get('enabled') is not False and a.get('configured') is not False]
  assert all(a.get('running') is True and a.get('connected') is not False for a in active),(agent,channel,'configured channel not running/connected')
  checked[channel]=[{k:a.get(k) for k in ['running','connected']} for a in active]
 rows.append({'agent':agent,'healthy':True,'image':d['Image'],'sharedLock':lock,'persistentV2Gate':True,'recoveryPinsMatch':True,'configAndWrapperPreserved':True,'configuredChannels':checked})
proof={'passed':True,'agents':rows,'allAgentsShareOriginalLockInode':True,'liveLint':json.loads((ROOT/'live-lint-proof.json').read_text())}
(ROOT/'final-audit.json').write_text(json.dumps(proof,indent=2));print(json.dumps({'fleetPassed':True,'agents':len(rows),'sharedInodePreserved':True}),flush=True)
