"""One idle agent: preserve state, activate proven tools image, verify recovery identity."""
import hashlib,json,os,shutil,sqlite3,subprocess,sys,time,urllib.request
from pathlib import Path
name=sys.argv[1]
assert name in {'amanda','victor','wilma','vivian','inga','maggie','gohzed','grogar','terry','edith','marsha'}
os.umask(0o077)
live=Path('/opt/openclaw/agents')/name
work=Path('/opt/openclaw/backups/components-20261018')/name
work.mkdir(parents=True,exist_ok=True)
catalog=json.loads(Path('/opt/openclaw/recovery/components-20261018/catalog.json').read_text())
proof=json.loads(Path('/opt/openclaw/recovery/components-20261018/archive-proof.json').read_text())
assert proof['allImageIdsVerified'] and proof['archiveSha256']==catalog['sha256']
def rpc(method,params=None):
    args=['docker','exec','-u','node',name,'node','/app/openclaw.mjs','gateway','call',method,'--json']
    if params is not None:args+=['--params',json.dumps(params)]
    r=subprocess.run(args,capture_output=True,text=True,timeout=120)
    assert r.returncode==0,'RPC failed: '+method
    return json.loads(r.stdout[r.stdout.index('{'):])
active=rpc('status').get('shutdownBudget',{}).get('activeWork')
assert active and all(v==0 for v in active.values()),'Active work; retry later without interrupting it'
for method,params in [('health',None),('cron.list',{'includeDisabled':True})]:
    value=rpc(method,params);(work/(method+'-before.json')).write_text(json.dumps(value))
    if method=='cron.list':assert not any(j.get('state',{}).get('runningAtMs') for j in value['jobs'])
d=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
old=d['Config']['Image'];new='zedbiz/'+(name if name in {'amanda','victor','grogar','marsha'} else 'openclaw-base')+':2026.10.4-components-20261018'
assert old!=new,'Already activated; verify instead of repeating'
manifest=(Path('/opt/openclaw/recovery')/(name+'-20261018')/'manifest.json') if name in {'amanda','victor'} else Path('/opt/openclaw/recovery/fleet-20261018')/name/'manifest.json'
assert manifest.exists()
shutil.copy2(manifest,work/'manifest-before.json');shutil.copy2(live/'docker-compose.yml',work/'compose-before.yml')
(work/'baseline.json').write_text(json.dumps({'image':d['Image'],'ref':old,'containerId':d['Id']}))
subprocess.run(['systemctl','stop','openclaw-'+name+'.service'],check=True,timeout=600)
assert subprocess.run(['docker','inspect',name],capture_output=True).returncode!=0
previous_gateway_stopped=time.monotonic()
# Only mutable runtime state is changing age; program/plugins are unchanged by this tools-only image.
subprocess.run(['tar','-C',str(live),'--exclude=config/backups','--exclude=config/npm','--exclude=config/.openclaw-private-update-capture','-cf',str(work/'state-before.tar'),'config','agents'],check=True,timeout=600)
subprocess.run(['tar','-tf',str(work/'state-before.tar')],check=True,stdout=subprocess.DEVNULL)
for p in [live/'config/state/openclaw.sqlite',* (live/'agents').glob('*/agent/openclaw-agent.sqlite')]:
    if p.exists():
        with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as db:
            db.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True)
            assert db.execute('pragma quick_check').fetchall()==[('ok',)]
text=(live/'docker-compose.yml').read_text();assert text.count(old)==1
text=text.replace(old,new)
assert text.count('&& openclaw gateway run')==1
text=text.replace('&& openclaw gateway run','&& exec openclaw gateway run')
text=text.replace('start_period: 30s','start_period: 120s',1)
lines=text.splitlines();idx=next(i for i,line in enumerate(lines) if '&& exec openclaw gateway run' in line)
lines.insert(idx,'    stop_grace_period: 330s')
(live/'docker-compose.yml').write_text('\n'.join(lines)+'\n')
refs=subprocess.check_output(['docker','compose','--env-file','.env','config','--images'],cwd=live,text=True).split()
ids={i['ref']:i['id'] for i in catalog['images']};assert new in refs and set(refs)<=ids.keys()
m=json.loads(manifest.read_text());m.update(archive=catalog['archive'],sha256=catalog['sha256'],images=[{'ref':r,'id':ids[r],'automatic':True} for r in sorted(set(refs))]);manifest.write_text(json.dumps(m,indent=2))
# A replacement container has a different PID namespace. OpenClaw requires the previous owner heartbeat to expire (90 seconds).
time.sleep(max(0,95-(time.monotonic()-previous_gateway_stopped)))
config=json.loads((live/'config/openclaw.json').read_text())
if config.get('plugins',{}).get('slots',{}).get('memory')=='hindsight-openclaw':
    subprocess.run(['tar','-C',str(live),'-cf',str(work/'plugins-before.tar'),'npm'],check=True,timeout=600)
    env=os.environ.copy();env['OP_SERVICE_ACCOUNT_TOKEN']=(live/'.op.token').read_text().strip()
    service=d['Config']['Labels']['com.docker.compose.service']
    with (work/'hindsight-install.log').open('w') as out:
        subprocess.run(['op','run','--env-file','.env','--','docker','compose','run','--rm','--no-deps','--user','node','--entrypoint','node',service,'/app/openclaw.mjs','plugins','install','@vectorize-io/hindsight-openclaw@1.0.0','--pin','--force','--no-enable'],cwd=live,env=env,stdout=out,stderr=subprocess.STDOUT,check=True,timeout=600)
    after=json.loads((live/'config/openclaw.json').read_text())
    assert config['plugins']['entries']['hindsight-openclaw']['config']==after['plugins']['entries']['hindsight-openclaw']['config']
subprocess.run(['systemctl','start','openclaw-'+name+'.service'],check=True,timeout=1510)
for _ in range(84):
    d=json.loads(subprocess.check_output(['docker','inspect',name],text=True))[0]
    if d['State'].get('Health',{}).get('Status')=='healthy':break
    time.sleep(5)
else:raise RuntimeError('Readiness deadline')
assert d['Image']==ids[new] and d['RestartCount']==0 and not d['State']['OOMKilled']
v=subprocess.check_output(['docker','exec',name,'node','--version'],text=True).strip();assert v=='v24.22.0'
(work/'activation.json').write_text(json.dumps({'agent':name,'image':new,'id':d['Image'],'node':v,'stateArchive':str(work/'state-before.tar')}))
print(json.dumps({'agent':name,'activated':True,'node':v,'image':new}),flush=True)
