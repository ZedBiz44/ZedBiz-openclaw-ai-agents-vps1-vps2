import os,sys,json,subprocess,pathlib,hashlib,time
raise SystemExit('Retired rollout: paid defaults were not authorized. Use the reviewed OAuth migration in issue #436. No changes performed.')
name=sys.argv[1]
assert name in ['amanda','edith','gohzed','grogar','inga','maggie','victor','vivian','wilma']
base=pathlib.Path('/opt/openclaw/builds/2026.9.8-terry-20261003');work=base/('fleet-'+name);work.mkdir(exist_ok=True)
backup=pathlib.Path('/opt/openclaw/backups')/(name+'-20261003-pre-9.8')
if backup.exists():raise SystemExit('Backup directory already exists; inspect before continuing')
subprocess.run(['docker','run','--rm','-v','/opt/openclaw/backups:/backup','alpine:3.22','sh','-c','mkdir -m 700 /backup/'+backup.name+' && chown 1001:1001 /backup/'+backup.name],check=True)
image='zedbiz/openclaw-victor:2026.9.8-20261003-imapfix' if name=='victor' else 'zedbiz/openclaw-base:2026.9.8-terry-20261003-imapfix'
subprocess.run(['docker','image','inspect',image],check=True,stdout=subprocess.DEVNULL)
c=json.loads(subprocess.check_output(['docker','inspect',name]))[0]
(backup/'previous-image.txt').write_text(c['Config']['Image']+'\n')
cfg=subprocess.check_output(['docker','exec',name,'cat','/home/node/.openclaw/openclaw.json'])
(backup/'config-before.json').write_bytes(cfg);os.chmod(backup/'config-before.json',0o600)
for label,command in [('cron',['openclaw','cron','list','--json']),('skills',['openclaw','skills','check','--agent','main','--json'])]:
 r=subprocess.run(['docker','exec',name,*command],capture_output=True,timeout=90)
 (work/(label+'-before.json')).write_bytes(r.stdout)
 if r.returncode:raise SystemExit(label+' baseline failed before stop')
subprocess.run(['docker','stop','-t','330',name],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['docker','run','--rm','-v',f'/opt/openclaw/agents/{name}:/source:ro','-v',str(backup)+':/backup','alpine:3.22','sh','-c','umask 077; tar -cf /backup/state.tar -C /source . && chown 1001:1001 /backup/state.tar'],check=True)
subprocess.run(['sha256sum',str(backup/'state.tar')],check=True,stdout=open(backup/'state.sha256','w'))
print(name,'BACKUP_COMPLETE',flush=True)
env=os.environ.copy();args=['docker','run','--rm','--name','cody-upgrade-'+name,'--network','openclaw','--volumes-from',name,'--user','node']
for item in c['Config']['Env']:
 k,v=item.split('=',1)
 if k in ('PATH','NODE_VERSION','YARN_VERSION'):continue
 env[k]=v;args+=['-e',k]
def cli(command,log):
 with open(work/log,'w') as f:
  p=subprocess.run([*args,'--entrypoint','openclaw',image,*command],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=900)
 return p.returncode
rc=cli(['doctor','--fix','--non-interactive','--yes'],'doctor.log')
print(name,'DOCTOR_COMPLETE',rc,flush=True)
if rc:
 log=(work/'doctor.log').read_text()
 errors=[line for line in log.splitlines() if line.startswith('[error]')]
 if not errors or any('Retained native directory does not resolve' not in line for line in errors):
  raise SystemExit('Doctor failed; agent remains stopped with backup preserved')
subprocess.run([*args,'-v',str(base)+':/maintenance:ro','--entrypoint','node',image,'/maintenance/repair-native-host-peers.mjs'],env=env,check=True)
# Preserve existing skill flags and fallback/thinking settings while retaining migrations.
fix='''import fs from 'node:fs';
const p='/home/node/.openclaw/openclaw.json';const c=JSON.parse(fs.readFileSync(p));const before=JSON.parse(fs.readFileSync('/backup/config-before.json'));
c.skills=before.skills;
c.agents.defaults.model.fallbacks=before.agents.defaults.model.fallbacks;
c.agents.defaults.thinkingDefault=before.agents.defaults.thinkingDefault;
const a='/home/node/.openclaw/workspace/AGENTS.md';const n=fs.existsSync(a)?fs.readFileSync(a,'utf8').length:0;
c.agents.defaults.bootstrapMaxChars=Math.max(before.agents.defaults.bootstrapMaxChars||20000,n+1000);
fs.writeFileSync(p,JSON.stringify(c,null,2)+'\\n',{mode:0o600});
console.log('Original skills/fallbacks/thinking retained; merged instructions fit');'''
(work/'finish.mjs').write_text(fix)
subprocess.run([*args,'--user','root','-v',str(backup)+':/backup:ro','-v',str(work)+':/maintenance:ro','--entrypoint','node',image,'/maintenance/finish.mjs'],env=env,check=True)
subprocess.run([*args,'-v',str(base)+':/maintenance:ro','--entrypoint','node',image,'/maintenance/set-sol-default.mjs'],env=env,check=True)
if cli(['config','validate'],'config-validation.log'):raise SystemExit('Config validation failed')
if name=='amanda':
 subprocess.run([*args,'-v',str(base)+':/maintenance:ro','--entrypoint','python3',image,'/maintenance/install-amanda-startup-fix.py'],env=env,check=True)
if name=='grogar':
 subprocess.run([*args,'-v',str(base)+':/maintenance:ro','--entrypoint','python3',image,'/maintenance/prepare-grogar-startup.py'],env=env,check=True)
compose=pathlib.Path('/opt/openclaw/agents')/name/'docker-compose.yml';text=compose.read_text();old=c['Config']['Image']
if text.count('image: '+old)!=1:raise SystemExit('Expected unique Compose image pin')
compose.write_text(text.replace('image: '+old,'image: '+image,1))
wrapper=compose.parent/('op-start-'+name+'.sh')
subprocess.run([str(wrapper),'up'],check=True,stdout=open(work/'activation.log','w'),stderr=subprocess.STDOUT)
print(name,'ACTIVATED',flush=True)
