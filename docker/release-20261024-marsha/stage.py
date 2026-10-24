"""Prepare an isolated, consistent restored Marsha copy; never write live state."""
import pathlib,subprocess,json,sqlite3,os,shutil,hashlib,sys,time
P=pathlib.Path;os.umask(0o077)
live=P('/opt/openclaw/agents/marsha');w=P('/opt/openclaw/backups/release-20261024-marsha');stage=w/'rehearsal'
def run(a,**kw):return subprocess.run(a,capture_output=True,text=True,**kw)
d=json.loads(run(['docker','inspect','marsha']).stdout)[0]
assert d['State']['Health']['Status']=='healthy'
assert not stage.exists(),'Inspect existing stage instead of overwriting'
(w/'runtime.env').write_text('\n'.join(d['Config']['Env'])+'\n')
(w/'mounts.json').write_text(json.dumps(d['Mounts']))
(w/'container-before.json').write_text(json.dumps({'id':d['Id'],'imageId':d['Image'],'ref':d['Config']['Image'],'restartCount':d['RestartCount']}))
shutil.copy2(live/'docker-compose.yml',w/'compose-before.yml')
shutil.copy2('/opt/openclaw/recovery/fleet-20261018/marsha/manifest.json',w/'manifest-before.json')
def ignore(directory,names):return {'tmp','cache'}&set(names) if P(directory)==live/'config' else set()
shutil.copytree(live,stage,symlinks=True,ignore=ignore)
databases=[]
for src in [live/'config/state/openclaw.sqlite',*(live/'agents').glob('*/agent/openclaw-agent.sqlite')]:
 dst=stage/src.relative_to(live)
 for p in [dst,P(str(dst)+'-wal'),P(str(dst)+'-shm')]:
  if p.exists():p.unlink()
 with sqlite3.connect('file:'+str(src)+'?mode=ro',uri=True) as old,sqlite3.connect(dst) as new:
  old.backup(new);new.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True)
  assert new.execute('pragma quick_check').fetchall()==[('ok',)]
 databases.append(str(src.relative_to(live)))
for directory,dirs,files in os.walk(live,followlinks=False):
 for src in [P(directory),*[P(directory)/n for n in dirs+files]]:
  dst=stage/src.relative_to(live)
  if dst.exists() or dst.is_symlink():st=src.lstat();os.chown(dst,st.st_uid,st.st_gid,follow_symlinks=False)
shutil.copy2(stage/'config/openclaw.json',w/'config-before.json')
# Copy a second consistent baseline for migration comparison before test-only settings.
ref=w/'comparison-original';(ref/'config/state').mkdir(parents=True)
shutil.copy2(stage/'config/openclaw.json',ref/'config/openclaw.json')
shutil.copy2(stage/'config/state/openclaw.sqlite',ref/'config/state/openclaw.sqlite')
for r in ['AGENTS.md','SOUL.md','USER.md','IDENTITY.md','MEMORY.md','TOOLS.md']:
 p=stage/'workspace'/r
 if p.exists():(ref/'workspace').mkdir(exist_ok=True);shutil.copy2(p,ref/'workspace'/r)
skills={}
for root in [stage/'skills',stage/'workspace/skills']:
 for p in root.rglob('*'):
  if p.is_file():skills[str(p.relative_to(stage))]=hashlib.sha256(p.read_bytes()).hexdigest()
(w/'skills-before.json').write_text(json.dumps(skills))
c=json.loads((stage/'config/openclaw.json').read_text());c.setdefault('cron',{})['enabled']=False;c.setdefault('hooks',{})['enabled']=False;c['hooks'].setdefault('internal',{})['enabled']=False
c['agents']['defaults'].setdefault('heartbeat',{})['every']='0m'
for a in [*c['agents'].get('list',[]),*c['agents'].get('entries',{}).values()]:a.setdefault('heartbeat',{})['every']='0m'
c['plugins']['entries']['hindsight-openclaw']['config']['autoRetain']=False
cfg=stage/'config/openclaw.json';cfg.write_text(json.dumps(c,indent=2)+'\n');os.chown(cfg,1000,1000)
wiki=w/'wiki';shutil.copytree('/opt/openclaw/shared/knowledge/wiki',wiki)
assert not any(p.is_symlink() for p in wiki.rglob('*'))
subprocess.run(['chown','-R','1000:1000',str(wiki)],check=True)
# Only copied leases are released; source stays untouched.
with sqlite3.connect(stage/'config/state/openclaw.sqlite') as db:
 leases=db.execute('select count(*) from state_leases').fetchone()[0]
 assert leases<=1
 db.execute('delete from agent_database_leases');db.execute("delete from state_leases where scope='gateway-owner' and lease_key='global'")
result={'consistentDatabases':databases,'customSkillFiles':len(skills),'productionContainerUnchanged':json.loads(run(['docker','inspect','marsha']).stdout)[0]['Id']==d['Id'],'copiedStateOnly':True}
(w/'stage.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)

