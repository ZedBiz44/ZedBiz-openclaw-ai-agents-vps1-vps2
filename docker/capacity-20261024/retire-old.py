"""Exact-path retirement of user-approved centralized pre-October18 VPS1 backups."""
import pathlib,json,sys,os,subprocess,hashlib,shutil,time
P=pathlib.Path;os.umask(0o077)
W=P('/opt/openclaw/backups/retention-20261024');W.mkdir(mode=0o700,exist_ok=True)
targets=list(dict.fromkeys(json.loads(P('/tmp/cody-retention-targets-20261024.json').read_text())))
def run(a):return subprocess.check_output(a,text=True)
def digest(p):
 with P(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(n,v):(W/(n+'.json')).write_text(json.dumps(v,indent=2))
def snapshot():
 ids=run(['docker','ps','-aq']).split();ds=json.loads(run(['docker','inspect',*ids]))
 return {d['Name'].lstrip('/'):{'id':d['Id'],'image':d['Image'],'pid':d['State']['Pid'],'started':d['State']['StartedAt'],'restarts':d['RestartCount'],'health':d['State'].get('Health',{}).get('Status'),'mounts':[m['Source'] for m in d['Mounts']]} for d in ds if not (d['Config'].get('Labels') or {}).get('cody.retention-helper')}
def validate():
 ds=snapshot();recovery=[]
 for name in ['terry','edith','amanda','victor','vivian','wilma','gohzed','grogar','inga','maggie','marsha']:
  m=P('/opt/openclaw/recovery')/(name+'-20261018')/'manifest.json'
  if not m.exists():m=P('/opt/openclaw/recovery/fleet-20261018')/name/'manifest.json'
  j=json.loads(m.read_text());assert digest(j['wrapper'])==j['wrapper_sha256'];assert P(j['archive']).is_file()
  expected={x['id'] for x in j['images']};assert ds[name]['image'] in expected and ds[name+'-asana-mcp']['image'] in expected
  assert ds[name]['health']=='healthy' and ds[name+'-asana-mcp']['health']=='healthy'
  recovery.append({'agent':name,'manifest':str(m),'manifestSha':digest(m),'archive':j['archive'],'wrapperSha':digest(j['wrapper'])})
 return ds,recovery
if sys.argv[1]=='plan':
 assert not (W/'plan.json').exists(),'Preserve original plan'
 ds,recovery=validate();entries=[]
 for x in targets:
  p=P(x);assert p.exists() and not p.is_symlink() and str(p.resolve())==x
  assert p.parent in [P('/opt/openclaw/backups'),P('/home/jackadmin/openclaw-backups')]
  for container,d in ds.items():
   for src in d['mounts']:
    s=P(src).resolve()
    # File Browser exposes /opt for human file management; it does not boot from these backups.
    # Open-file dependency checks below still apply. No other ancestor mount is exempt.
    if (container,str(s)) in [('filebrowser','/opt'),('zedbiz-restart-api','/opt/openclaw')] and p.is_relative_to(s):continue
    assert not (s==p or s.is_relative_to(p) or p.is_relative_to(s)),('Mounted backup overlap',x,str(s))
  for j in recovery:assert not P(j['archive']).is_relative_to(p)
  # Reject any active process using a selected backup tree.
  for proc in P('/proc').iterdir():
   if not proc.name.isdigit():continue
   for link in [proc/'cwd',proc/'exe',*list((proc/'fd').glob('*'))]:
    try:
     s=link.resolve();assert not(s==p or s.is_relative_to(p)),('Active process dependency',x,str(s))
    except (OSError,RuntimeError):pass
  st=p.stat();entries.append({'path':x,'inode':st.st_ino,'mtimeNs':st.st_mtime_ns,'directory':p.is_dir(),'allocatedBytes':int(run(['du','-sx','-B1',x]).split()[0])})
 save('plan',{'targets':entries,'containers':ds,'recovery':recovery,'diskBefore':shutil.disk_usage('/')._asdict(),'authorization':'Jack explicitly approved deleting backups older than October18. October18 state and active boot recovery excluded.'})
 print(json.dumps({'planPassed':True,'targets':len(entries),'allocatedGiB':sum(e['allocatedBytes'] for e in entries)/2**30,'recoveryAgents':len(recovery)}))
elif sys.argv[1]=='apply':
 assert not (W/'result.json').exists(),'Do not repeat cleanup'
 plan=json.loads((W/'plan.json').read_text());ds,recovery=validate();assert ds==plan['containers'] and recovery==plan['recovery'],'Runtime changed since plan'
 for e in plan['targets']:
  p=P(e['path']);assert p.exists() and not p.is_symlink() and str(p.resolve())==e['path'];s=p.stat();assert s.st_ino==e['inode'] and s.st_mtime_ns==e['mtimeNs']
 done=[]
 for e in plan['targets']:
  p=P(e['path'])
  if e['directory']:shutil.rmtree(p)
  else:p.unlink()
  assert not p.exists();done.append(e['path']);save('progress',done)
 after,rec=validate();assert after==ds and rec==recovery,'Runtime changed during deletion'
 r={'removed':done,'removedAllocatedBytes':sum(e['allocatedBytes'] for e in plan['targets']),'diskBefore':plan['diskBefore'],'diskAfter':shutil.disk_usage('/')._asdict(),'containersUnchanged':True,'recoveryAgentsVerified':len(rec)};save('result',r);print(json.dumps(r))
else:raise SystemExit('Unknown action')

