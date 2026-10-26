"""Run as host root: preserve rollback, refuse drift, cut over one idle gateway."""
import hashlib,json,os,pathlib,shutil,subprocess,sys,time
P=pathlib.Path;ROOT=P('/opt/openclaw/recovery/wiki-filelock-20261026')
INVENTORY=json.loads((ROOT/'inventory.json').read_text())
IMAGES=json.loads((ROOT/'images.json').read_text())
GUARD='python3 -I -B -c \'import json; assert json.load(open("/opt/zedbiz/wiki-lock/integrity.json"))["version"] == "filelock-fd-v2"\' && python3 -I -B /opt/zedbiz/wiki-lock/verify.py || exit $? # shared-wiki-upgrade-gate'
OLD_GUARD='python3 /opt/zedbiz/wiki-lock/verify.py || exit $? # shared-wiki-upgrade-gate'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def inspect(name):return json.loads(subprocess.check_output(['docker','inspect',name]))[0]
def run(args,label,timeout=300):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 (ROOT/(label+'.private.log')).write_text(p.stdout+p.stderr)
 assert p.returncode==0,label+' failed; see private log'
 return p.stdout
def atomic(p,content):
 st=p.stat();temp=p.with_name(p.name+'.wiki-v2.tmp');assert not temp.exists()
 temp.write_text(content);os.chown(temp,st.st_uid,st.st_gid);os.chmod(temp,st.st_mode&0o7777);os.replace(temp,p)
def channels(agent):
 text=run(['docker','exec',agent,'openclaw','channels','status','--json'],agent+'-channels',90)
 data=json.loads(text[text.index('{'):]);accounts=data.get('channelAccounts',{})
 assert accounts and accounts.get('discord'),agent+' channel state unavailable'
 return accounts
def idle(agent):
 for attempt in range(20):
  data=channels(agent)
  if not any(a.get('busy') or a.get('activeRuns',0) for values in data.values() for a in values):return data
  print(agent+' waiting for active work',flush=True);time.sleep(15)
 raise RuntimeError(agent+' remains busy; no replacement')
PROBE=r'''
const fs=require('fs');const c=JSON.parse(fs.readFileSync('/home/node/.openclaw/openclaw.json'));
(async()=>{const base='http://127.0.0.1:'+(c.gateway.port||18789);
const ready=await fetch(base+'/readyz',{signal:AbortSignal.timeout(5000)});
const r=await fetch(base+'/tools/invoke',{method:'POST',signal:AbortSignal.timeout(120000),headers:{'Content-Type':'application/json',Authorization:'Bearer '+c.gateway.auth.token},body:JSON.stringify({tool:'wiki_search',args:{query:'ZedBiz',maxResults:1},sessionKey:'agent:main:main'})});
const d=await r.json();console.log(JSON.stringify({ready:ready.status,http:r.status,ok:d.ok,isError:d.result?.isError===true}));})().catch(()=>process.exit(1));
'''
def verify(agent,row,image,asana):
 for attempt in range(36):
  d=inspect(agent)
  if d['State'].get('Health',{}).get('Status')=='healthy':break
  time.sleep(5)
 else:raise RuntimeError(agent+' unhealthy after startup')
 assert d['Image']==image['id']
 run(['docker','exec',agent,'python3','-I','-B','/opt/zedbiz/wiki-lock/verify.py'],agent+'-gate',40)
 result=json.loads(run(['docker','exec',agent,'node','-e',PROBE],agent+'-wiki',150))
 assert result=={'ready':200,'http':200,'ok':True,'isError':False},result
 account=channels(agent)
 assert all(a.get('connected') and a.get('running') for a in account['discord'])
 if agent=='marsha':assert account.get('slack') and all(a.get('running') for a in account['slack'])
 assert sha(row['wrapper'])==row['wrapperSha']
 assert sha(P('/opt/openclaw/agents')/agent/'config/openclaw.json')==row['configSha']
 current=inspect(agent+'-asana-mcp');assert current['Id']==asana['Id'] and current['Image']==asana['Image'],'Asana service changed'
 proof={'passed':True,'agent':agent,'image':d['Image'],'healthy':True,'wikiSearch':result,'channels':{k:[{n:a.get(n) for n in ['running','connected','busy','activeRuns']} for a in v] for k,v in account.items()},'wrapperAndAgentConfigUnchanged':True,'asanaContainerUnchanged':True}
 (ROOT/(agent+'-acceptance.json')).write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
def deploy(agent):
 row=next(r for r in INVENTORY if r['agent']==agent);image=next(r for r in IMAGES if r['agent']==agent)
 base=P('/opt/openclaw/agents')/agent;compose=base/'docker-compose.yml';post=base/'workspace/post-start.sh';manifest=P(row['manifest'])
 assert inspect(agent)['Image']==row['image']
 for file,key in [(compose,'composeSha'),(post,'postStartSha'),(base/'config/openclaw.json','configSha'),(P(row['wrapper']),'wrapperSha')]:assert sha(file)==row[key],str(file)+' drifted'
 m=json.loads(manifest.read_text());assert m['images']==row['images'] and m['archive']==row['archive'] and m['sha256']==row['sha256']
 archive=json.loads((ROOT/'archive.json').read_text());assert P(archive['archive']).is_file()
 assert json.loads((ROOT/'cold-restore-proof.json').read_text())['passed']
 idle(agent);asana=inspect(agent+'-asana-mcp');backup=ROOT/'rollback'/agent;backup.mkdir(parents=True)
 for file in [compose,post,manifest]:shutil.copy2(file,backup/file.name)
 text=compose.read_text();assert text.count(row['imageRef'])==1
 script=post.read_text();assert script.count(OLD_GUARD)==1
 selected=[i for i in m['images'] if i['ref']==row['imageRef']];assert len(selected)==1
 selected[0].update(ref=image['after'],id=image['id']);m.update(archive)
 try:
  atomic(compose,text.replace(row['imageRef'],image['after']));atomic(post,script.replace(OLD_GUARD,GUARD));atomic(manifest,json.dumps(m,indent=2)+'\n')
  run(['docker','stop','--time','330',agent],agent+'-stop',350)
  run([row['wrapper'],'up'],agent+'-start',240)
  verify(agent,row,image,asana)
 except Exception:
  print(agent+' failed; restoring this gateway to its previous image and files',flush=True)
  run(['docker','stop','--time','330',agent],agent+'-rollback-stop',350)
  for file in [compose,post,manifest]:shutil.copy2(backup/file.name,file)
  run([row['wrapper'],'up'],agent+'-rollback-start',240)
  raise
if __name__=='__main__':
 os.umask(0o077)
 for agent in sys.argv[1:]:deploy(agent)
