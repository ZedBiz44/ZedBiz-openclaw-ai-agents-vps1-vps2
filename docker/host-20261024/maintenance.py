"""VPS1 host-only package maintenance; preserve running containers across patch update."""
import pathlib,subprocess,json,os,sys,time,re,hashlib,shutil,fcntl
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/host-20261024');W.mkdir(parents=True,exist_ok=True,mode=0o700)
action=sys.argv[1];env=os.environ.copy();env.update(DEBIAN_FRONTEND='noninteractive',NEEDRESTART_MODE='l')
def run(args,label=None,check=True,timeout=1200,cwd=None):
 p=subprocess.run(args,capture_output=True,text=True,env=env,timeout=timeout,cwd=cwd)
 if label:(W/(label+'.log')).write_text(p.stdout+p.stderr)
 if check and p.returncode:raise RuntimeError((label or args[0])+' failed; inspect protected log')
 return p
def save(n,v): (W/(n+'.json')).write_text(json.dumps(v,indent=2))
def read(n):return json.loads((W/(n+'.json')).read_text())
def digest(p):
 with P(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def containers():
 ids=run(['docker','ps','-q']).stdout.split()
 return {x['Name'].lstrip('/'):{'id':x['Id'],'pid':x['State']['Pid'],'image':x['Image'],'ref':x['Config']['Image'],'health':x['State'].get('Health',{}).get('Status'),'restarts':x['RestartCount'],'oom':x['State']['OOMKilled'],'started':x['State']['StartedAt']} for x in json.loads(run(['docker','inspect',*ids]).stdout) if (x['Config'].get('Labels') or {}).get('cody.host-maintenance-helper')!='true'}
def versions():return {k:run(a,check=False).stdout.strip() for k,a in {'docker':['docker','version','--format','{{.Server.Version}}'],'compose':['docker','compose','version','--short'],'containerd':['containerd','--version'],'tailscale':['tailscale','version'],'op':['op','--version'],'kernel':['uname','-r'],'liveRestore':['docker','info','--format','{{.LiveRestoreEnabled}}']}.items()}
def unchanged(before,after):
 assert set(before)<=set(after),'A pre-existing running container disappeared'
 for n,x in before.items():
  y=after[n];assert all(x[k]==y[k] for k in ['id','pid','image','restarts','started']),n+' restarted or changed identity'
  assert not y['oom'],n+' OOM'
def plan(label='plan'):
 p=run(['apt-get','-s','upgrade','--with-new-pkgs'],'simulation');assert not re.search(r'^Remv ',p.stdout,re.M),'Package removals require diagnosis'
 packages=[]
 for line in p.stdout.splitlines():
  if not line.startswith('Inst '):continue
  m=re.match(r'Inst (\S+)(?: \[([^\]]+)\])? \((\S+)',line);assert m,line
  name,old,new=m.groups();packages.append({'name':name,'old':old,'new':new})
 for x in packages:
  if x['name'] in ['docker-ce','docker-ce-cli','docker-ce-rootless-extras']:assert x['new'].split(':')[-1].startswith('29.9.'),'Docker beyond approved patch series'
  if x['name']=='containerd.io':assert x['new'].startswith('2.4.2-'),'containerd beyond approved packaging revision'
 save(label,packages);return packages
if action=='preflight':
 assert not (W/'before.json').exists(),'Preserve existing baseline'
 b={'timeUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'containers':containers(),'versions':versions(),'disk':run(['df','-h','/']).stdout,'memory':run(['free','-m']).stdout,'failedUnits':run(['systemctl','--failed','--no-legend','--plain']).stdout,'rebootRequired':P('/var/run/reboot-required').exists()}
 b['packageInventory']=run(['dpkg-query','-W','-f=${binary:Package}\t${Version}\n']).stdout
 b['held']=run(['apt-mark','showhold']).stdout;b['dpkgAudit']=run(['dpkg','--audit']).stdout;assert not b['dpkgAudit']
 assert shutil.disk_usage('/').free>15*2**30,'Insufficient host maintenance reserve'
 for name,x in b['containers'].items():
  if name.endswith('-asana-mcp') or name in ['terry','edith','amanda','victor','vivian','wilma','gohzed','grogar','inga','maggie','marsha']:assert x['health']=='healthy'
 # Current exact images and credential-injecting wrappers must remain recoverable.
 recovery=[]
 for name in ['terry','edith','amanda','victor','vivian','wilma','gohzed','grogar','inga','maggie','marsha']:
  m=P('/opt/openclaw/recovery')/(name+'-20261018')/'manifest.json'
  if not m.exists():m=P('/opt/openclaw/recovery/fleet-20261018')/name/'manifest.json'
  j=json.loads(m.read_text());assert digest(j['wrapper'])==j['wrapper_sha256'];assert P(j['archive']).is_file()
  expected={x['id'] for x in j['images']};assert b['containers'][name]['image'] in expected and b['containers'][name+'-asana-mcp']['image'] in expected
  for x in j['images']:assert run(['docker','image','inspect','--format','{{.Id}}',x['ref']]).stdout.strip()==x['id']
  recovery.append({'agent':name,'manifest':str(m),'archive':j['archive'],'sha256':j['sha256']})
 b['recovery']=recovery;save('before',b)
 print(json.dumps({'preflightPassed':True,'runningContainers':len(b['containers']),'versions':b['versions'],'heldPackages':b['held'],'rebootRequired':b['rebootRequired']}),flush=True)
elif action=='exclude-first-operator-helper':
 b=read('before');x=b['containers'].get('friendly_pascal');assert x and x['ref']=='alpine'
 assert run(['docker','inspect',x['id']],check=False).returncode!=0
 save('excluded-operator-helper',{'name':'friendly_pascal','container':x,'reason':'Transient Alpine/nsenter preflight operator; not a managed VPS1 service'})
 del b['containers']['friendly_pascal'];save('before',b);unchanged(b['containers'],containers());print('Transient preflight operator excluded; all40 managed containers still match')
elif action=='refresh':
 run(['apt-get','update'],'apt-refresh');items=plan();print(json.dumps({'refreshed':True,'packages':items}),flush=True)
elif action=='prepare':
 b=read('before');unchanged(b['containers'],containers());items=read('plan');assert items
 paths=[p for p in ['etc/docker','etc/containerd','etc/apt','etc/systemd/system','var/lib/dpkg/status','etc/needrestart'] if P('/'+p).exists()]
 run(['tar','-czf',str(W/'host-config-before.tar.gz'),'-C','/',*paths],'config-backup');run(['tar','-tzf',str(W/'host-config-before.tar.gz')],'config-backup-list')
 old=W/'old-debs';old.mkdir(exist_ok=True,mode=0o700);recovery=[]
 for x in items:
  if not x['old']:continue
  p=run(['apt-get','download',x['name']+'='+x['old']],'old-'+x['name'].replace(':','-'),check=False,cwd=old)
  recovery.append({'name':x['name'],'version':x['old'],'downloaded':p.returncode==0})
  if x['name'] in ['docker-ce','docker-ce-cli','containerd.io']:assert p.returncode==0,'Critical old package unavailable'
 run(['apt-get','-y','--download-only','--no-remove','install',*[x['name']+'='+x['new'] for x in items]],'download-new')
 save('prepared',{'passed':True,'configArchiveSha256':digest(W/'host-config-before.tar.gz'),'oldPackages':recovery,'oldDebs':[{'name':p.name,'sha256':digest(p)} for p in old.glob('*.deb')]})
 print(json.dumps({'packagesDownloaded':len(items),'oldPackageRecovery':recovery,'configBackupVerified':True}),flush=True)
elif action=='enable-live-restore':
 assert read('prepared')['passed'];before=containers();p=P('/etc/docker/daemon.json');exists=p.exists();s=p.stat() if exists else None;raw=p.read_bytes() if exists else b'{}'
 (W/'daemon-before.json').write_bytes(raw);save('daemon-before-meta',{'existed':exists,'mode':s.st_mode&0o777 if s else 0o644})
 cfg=json.loads(raw);cfg['live-restore']=True;proposed=W/'daemon-proposed.json';proposed.write_text(json.dumps(cfg,indent=2)+'\n')
 run(['dockerd','--validate','--config-file',str(proposed)],'daemon-validation')
 try:
  p.parent.mkdir(exist_ok=True);p.write_bytes(proposed.read_bytes());os.chmod(p,s.st_mode&0o777 if s else 0o644)
  run(['systemctl','reload','docker'],'docker-reload')
  assert versions()['liveRestore']=='true';unchanged(before,containers())
 except BaseException:
  if exists:p.write_bytes(raw)
  else:p.unlink(missing_ok=True)
  run(['systemctl','reload','docker'],'docker-reload-rollback',check=False);raise
 save('live-restore',{'passed':True,'allContainerProcessesPreserved':True,'daemonConfigSha256':digest(p)})
 print(json.dumps(read('live-restore')),flush=True)
elif action=='apply':
 lock=(W/'lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 assert read('live-restore')['passed'] and versions()['liveRestore']=='true';items=read('plan');before=containers();save('immediate-before',before)
 try:
  run(['apt-get','-y','--no-remove','-o','Dpkg::Options::=--force-confold','install',*[x['name']+'='+x['new'] for x in items]],'package-upgrade',timeout=2400)
  for _ in range(60):
   if run(['docker','info'],check=False).returncode==0:break
   time.sleep(2)
  else:raise RuntimeError('Docker did not recover after package installation')
  unchanged(before,containers());assert versions()['liveRestore']=='true'
  installed={x['name']:run(['dpkg-query','-W','-f=${Version}',x['name']]).stdout for x in items};assert all(installed[x['name']]==x['new'] for x in items)
  audit=run(['dpkg','--audit']).stdout;assert not audit
  save('applied',{'passed':True,'installed':installed,'versions':versions(),'containersUninterrupted':True,'rebootRequired':P('/var/run/reboot-required').exists()})
 except BaseException as e:
  save('failure',{'phase':'apply','error':str(e)});raise
elif action=='verify':
 applied=read('applied');assert applied['passed'];before=read('before');after=containers();unchanged(before['containers'],after)
 pending=plan('remaining-plan');assert not pending,'Further installable updates remain after refreshed plan'
 for n,x in before['containers'].items():
  if x['health']=='healthy':assert after[n]['health']=='healthy',n+' lost health'
 services={n:run(['systemctl','is-active',n],check=False).stdout.strip() for n in ['docker','containerd','tailscaled','ssh']};assert all(v=='active' for v in services.values())
 failed=run(['systemctl','--failed','--no-legend','--plain']).stdout;assert failed==before['failedUnits'],'New failed service'
 checks={k:run(a,check=False).returncode==0 for k,a in {'tailscaleSelf':['tailscale','status','--json'],'aptCheck':['apt-get','check']}.items()};assert all(checks.values())
 need=run(['needrestart','-b','-r','l'],'needrestart',check=False)
 result={'passed':True,'timeUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'versions':versions(),'services':services,'allRunningContainersPreserved':len(after),'allPriorHealthyContainersHealthy':True,'pendingPackages':pending,'heldPackages':run(['apt-mark','showhold']).stdout,'rebootRequired':P('/var/run/reboot-required').exists(),'needrestartExit':need.returncode,'needrestartSummary':[line for line in need.stdout.splitlines() if line.startswith('NEEDRESTART-')],'disk':run(['df','-h','/']).stdout,'memory':run(['free','-m']).stdout}
 save('verified',result);print(json.dumps(result),flush=True)
else:raise SystemExit('Unknown maintenance action')

