"""Detached host maintenance. Never launch apt from a Docker-owned process."""
import concurrent.futures, json, os, shutil, signal, subprocess, time
from pathlib import Path
os.umask(0o077)
names=['wilma','vivian','inga','maggie','gohzed','grogar','terry','edith','marsha','amanda','victor']
base=Path('/opt/openclaw/backups/components-20261018');work=base/'host'
assert shutil.disk_usage(base).free>10*1024**3, 'Host maintenance requires at least 10 GiB free'
def run(args,timeout=180,**kw):
    return subprocess.run(args,check=True,timeout=timeout,**kw)
def emit(message):print(message,flush=True)
def inspect(name):return json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
def rpc(name,method):
    p=run(['docker','exec','-u','node',name,'node','/app/openclaw.mjs','gateway','call',method,'--json'],120,capture_output=True,text=True)
    return json.loads(p.stdout[p.stdout.index('{'):])
for name in names:
    assert (base/name/'acceptance.json').exists() and (base/name/'asana-acceptance.json').exists(), name+' incomplete acceptance'
    d=inspect(name);assert d['State']['Health']['Status']=='healthy' and d['RestartCount']==0
    active=rpc(name,'status').get('shutdownBudget',{}).get('activeWork')
    assert active and all(v==0 for v in active.values()),name+' busy; retry without stopping active work'
emit('All eleven gateways idle and accepted before host maintenance')
containers=json.loads(subprocess.check_output(['docker','inspect',*subprocess.check_output(['docker','ps','-q'],text=True).split()],text=True))
shared=[d['Name'].lstrip('/') for d in containers if d['Name'].lstrip('/') not in names+[n+'-asana-mcp' for n in names] and d['HostConfig']['RestartPolicy']['Name'] not in {'','no'}]
assert 'hindsight-db' in shared and 'caddy' in shared and '1password-connect-api' in shared
(work/'running-shared-before.json').write_text(json.dumps(shared))
for name in names:
    live=Path('/opt/openclaw/agents')/name
    shutil.copy2(live/'docker-compose.yml',work/(name+'-compose-before.yml'))
    s=(live/'docker-compose.yml').read_text()
    if '&& openclaw gateway run' in s:
        assert name=='wilma';s=s.replace('&& openclaw gateway run','&& exec openclaw gateway run')
    if 'stop_grace_period:' not in s:
        lines=s.splitlines();i=next(i for i,x in enumerate(lines) if '&& exec openclaw gateway run' in x);lines.insert(i,'    stop_grace_period: 330s');s='\n'.join(lines)+'\n'
    s=s.replace('start_period: 30s','start_period: 120s',1)
    (live/'docker-compose.yml').write_text(s)
    drop=Path('/etc/systemd/system')/('openclaw-'+name+'.service.d')/'shutdown-budget.conf'
    if drop.exists():shutil.copy2(drop,work/(name+'-shutdown-budget-before.conf'))
    drop.parent.mkdir(exist_ok=True);drop.write_text('[Service]\nTimeoutStopSec=360\n')
run(['systemctl','daemon-reload'])
stopped=[];apt_ok=False
try:
    # The older Wilma container still has a shell between init and gateway.
    # Signal the verified gateway directly after disabling automatic restart.
    d=inspect('wilma')
    if '&& openclaw gateway run' in ' '.join(d['Config']['Cmd']):
        run(['docker','update','--restart=no','wilma'],capture_output=True)
        rows=subprocess.check_output(['docker','top','wilma','-eo','pid,comm'],text=True).splitlines()[1:]
        pids=[int(x.split()[0]) for x in rows if x.split()[-1]=='openclaw-gatewa'];assert len(pids)==1
        os.kill(pids[0],signal.SIGTERM)
        for _ in range(330):
            if not inspect('wilma')['State']['Running']:break
            time.sleep(1)
        else:raise RuntimeError('Wilma did not drain; host update not started')
    for name in names:
        # Recheck each remaining gateway immediately before its managed stop.
        if name!='wilma':
            active=rpc(name,'status').get('shutdownBudget',{}).get('activeWork');assert active and all(v==0 for v in active.values()),name+' became busy'
        run(['systemctl','stop','openclaw-'+name+'.service'],420);stopped.append(name);emit('Stopped cleanly: '+name)
    # Stop API before its database, then the remaining shared containers.
    first=[x for x in ['hindsight','mem0-dev-qdrant-1'] if x in shared]
    for group in [first,[x for x in shared if x not in first]]:
        if group:run(['docker','stop','-t','60',*group],180,stdout=subprocess.DEVNULL)
    env=os.environ.copy();env.update(DEBIAN_FRONTEND='noninteractive',NEEDRESTART_MODE='a')
    with (work/'apt-upgrade.log').open('w') as out:
        run(['apt-get','-y','-o','Dpkg::Options::=--force-confold','upgrade'],1800,env=env,stdout=out,stderr=subprocess.STDOUT)
    apt_ok=True;emit('Host package upgrade finished')
finally:
    run(['systemctl','start','docker'],180)
    for group in [['hindsight-db','1password-connect-api','1password-connect-sync'],[x for x in shared if x not in {'hindsight-db','1password-connect-api','1password-connect-sync'}]]:
        run(['docker','start',*group],180,stdout=subprocess.DEVNULL)
    time.sleep(15)
    for name in stopped:
        run(['systemctl','start','openclaw-'+name+'.service'],1510);emit('Managed start: '+name)
        if name==stopped[0]:
            for _ in range(84):
                d=inspect(name)
                if d['State'].get('Health',{}).get('Status')=='healthy':break
                time.sleep(5)
            else:raise RuntimeError('First post-Docker gateway failed readiness; inspect before proceeding')
            assert d['RestartCount']==0 and not d['State']['OOMKilled']
            emit('First post-Docker gateway healthy without restart/OOM')
        else:time.sleep(5)
    # If Wilma failed before the stop list was populated, restore its restart policy.
    if 'wilma' not in stopped:
        run(['docker','update','--restart=unless-stopped','wilma'],capture_output=True)
        if not inspect('wilma')['State']['Running']:run(['docker','start','wilma'],capture_output=True)
result={'aptSucceeded':apt_ok,'agentsRestarted':stopped,'sharedRestarted':shared,'rebootRequired':Path('/var/run/reboot-required').exists(),'docker':subprocess.check_output(['docker','version','--format','{{.Server.Version}}'],text=True).strip(),'containerd':subprocess.check_output(['containerd','--version'],text=True).strip()}
(work/'activation.json').write_text(json.dumps(result,indent=2));emit(json.dumps(result))
