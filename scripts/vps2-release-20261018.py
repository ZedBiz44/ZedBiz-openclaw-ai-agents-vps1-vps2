"""One-agent native VPS2 release stages; private captures, explicit operator gates."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.request

BASE = Path('/root/cody-vps2-20261018')
name, action, *extra = sys.argv[1:]
assert name in {'frank', 'harry', 'suzy'}
work = BASE/name
state = Path('/root/.openclaw-'+name)
program = Path('/opt/openclaw-'+name)
unit = 'openclaw-'+name+'.service'
original = work/'extracted'/str(state).lstrip('/')
stage = work/'rehearsal-state'
candidate = work/'candidate'
os.umask(0o077)

def emit(value):
    print(json.dumps(value), flush=True)

def save(filename, value):
    (work/filename).write_text(json.dumps(value, indent=2))

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def service():
    raw = subprocess.check_output(['systemctl','show',unit,'-p','ActiveState','-p','SubState','-p','MainPID','-p','NRestarts','-p','Result','-p','MemoryMax'],text=True)
    return dict(line.split('=',1) for line in raw.splitlines() if '=' in line)

def cli(mode, command, label, timeout=1200):
    env = os.environ.copy()
    env.update(HOME=str(state),OPENCLAW_STATE_DIR=str(state),OPENCLAW_CONFIG_PATH=str(state/'openclaw.json'),NODE_OPTIONS='--max-old-space-size=1536')
    env['OP_SERVICE_ACCOUNT_TOKEN'] = (state/'.op.token').read_text().strip()
    # Masking can replace numeric JSON fields with invalid unquoted text.
    # Capture unmasked output only in the private 0700/0600 evidence tree.
    prefix = ['op','run','--no-masking','--env-file='+str(state/'.env'),'--']
    if mode == 'rehearsal':
        args = prefix+['unshare','--mount','--propagation','private','python3',__file__,name,'namespace',*command]
    elif command == ['_mem0']:
        args = prefix+['python3',__file__,name,'mem0-inside']
    else:
        args = prefix+[str(program/'node_modules/.bin/openclaw'),*command]
    log = work/(label+'.log')
    with log.open('w') as out:
        r = subprocess.run(args,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=timeout)
    assert r.returncode == 0, 'CLI failed; inspect protected '+str(log)
    return log

def rpc(method, params=None, suffix='before'):
    args=['gateway','call',method,'--json']
    if params is not None: args += ['--params',json.dumps(params)]
    p=cli('live',args,method+'-'+suffix,120)
    text=p.read_text(); value=json.JSONDecoder().raw_decode(text[text.index('{'):])[0]
    save(method+'-'+suffix+'.json',value)
    return value

def integrity(root):
    files=[root/'state/openclaw.sqlite',*root.glob('agents/*/agent/openclaw-agent.sqlite')]
    for p in files:
        assert p.exists(), 'Database missing: '+str(p)
        with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as db:
            db.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True)
            assert db.execute('pragma quick_check').fetchall()==[('ok',)], 'Database failed: '+str(p)
    return len(files)

def cron_rows(root):
    with sqlite3.connect('file:'+str(root/'state/openclaw.sqlite')+'?mode=ro',uri=True) as db:
        return sorted(db.execute('select * from cron_jobs').fetchall())

if action == 'namespace':
    subprocess.run(['mount','-t','tmpfs','-o','mode=1777','tmpfs','/tmp'],check=True)
    subprocess.run(['mount','--bind',str(stage),str(state)],check=True)
    subprocess.run(['mount','--bind',str(candidate),str(program)],check=True)
    if extra == ['_mem0']:
        os.execv('/usr/bin/python3',['python3',__file__,name,'mem0-inside'])
    executable=str(program/'node_modules/.bin/openclaw')
    os.execv(executable,[executable,*extra])

elif action == 'backup':
    work.mkdir(mode=0o700,parents=True,exist_ok=True)
    assert not (work/'before.tar').exists(), 'Existing backup; inspect before retry'
    status=rpc('status')
    active=status.get('shutdownBudget',{}).get('activeWork')
    assert active is not None and all(v==0 for v in active.values()), 'Active/unknown work; wait before stopping'
    cron=rpc('cron.list',{'includeDisabled':True})
    assert not any(j.get('state',{}).get('runningAtMs') for j in cron['jobs']), 'Scheduled work active'
    rpc('health')
    baseline={'agent':name,'service':service(),'cronCount':len(cron['jobs']),'configSha256':sha(state/'openclaw.json'),'launcherSha256':sha(program/('start-'+name+'.sh'))}
    save('baseline.json',baseline)
    subprocess.run(['systemctl','stop',unit],check=True,timeout=300)
    assert service()['MainPID']=='0'
    emit({'agent':name,'stopped':True})
    paths=[str(state).lstrip('/'),str(program).lstrip('/'),'etc/systemd/system/'+unit]
    for p in ['/etc/systemd/system/'+unit+'.d','/etc/systemd/system.control/'+unit+'.d']:
        if Path(p).exists():paths.append(p.lstrip('/'))
    archive=work/'before.tar'
    subprocess.run(['tar','-C','/','--exclude='+str(state/'.op.token').lstrip('/'),'--exclude='+str(state/'.env.resolved').lstrip('/'),'-cf',str(archive),*paths],check=True,timeout=1200)
    baseline['archiveSha256']=sha(archive)
    subprocess.run(['tar','-tf',str(archive)],stdout=subprocess.DEVNULL,check=True)
    extracted=work/'extracted';extracted.mkdir()
    subprocess.run(['tar','-xf',str(archive),'-C',str(extracted)],check=True,timeout=1200)
    assert sha(original/'openclaw.json')==baseline['configSha256']
    baseline['databasesChecked']=integrity(original)
    shutil.copytree(original,stage,symlinks=True)
    shutil.copytree(program,candidate,symlinks=True,ignore=shutil.ignore_patterns('node_modules'))
    subprocess.run(['cp','-a',str(BASE/'core-candidate/node_modules'),str(candidate/'node_modules')],check=True)
    shutil.copy2(BASE/'core-candidate/package.json',candidate/'package.json')
    shutil.copy2(BASE/'core-candidate/package-lock.json',candidate/'package-lock.json')
    if name=='harry':
        result=subprocess.run(['python3',str(candidate/'patch-imap-notification-framing.py'),str(candidate/'node_modules/openclaw/dist/extensions/imap/index.js')],capture_output=True,text=True)
        (work/'imap-candidate.log').write_text(result.stdout+result.stderr)
        assert result.returncode==0,'IMAP custom patch requires review'
    save('baseline.json',baseline)
    emit(baseline)

elif action == 'doctor':
    mode=extra[0];assert mode in {'rehearsal','live'}
    assert service()['MainPID']=='0'
    cli(mode,['doctor','--fix','--non-interactive'],mode+'-doctor',1800)
    emit({'agent':name,'mode':mode,'doctorPassed':True})

elif action == 'compare':
    mode=extra[0];assert mode in {'rehearsal','live'}
    target=stage if mode=='rehearsal' else state
    before=json.loads((original/'openclaw.json').read_text());after=json.loads((target/'openclaw.json').read_text())
    assert cron_rows(original)==cron_rows(target),'Schedules changed'
    for key in ['model','models','modelPolicy','thinkingDefault','timeoutSeconds']:
        assert before['agents']['defaults'].get(key)==after['agents']['defaults'].get(key),'Model policy changed: '+key
    for key in ['mcp','tools','channels']:
        assert before.get(key)==after.get(key),'Access changed: '+key
    assert before.get('gateway',{}).get('auth')==after.get('gateway',{}).get('auth')
    assert before['plugins'].get('slots')==after['plugins'].get('slots')
    memory=before['plugins']['slots']['memory']
    assert before['plugins']['entries'][memory]==after['plugins']['entries'][memory]
    migrated_tools=False
    for leaf in ['AGENTS.md','SOUL.md','USER.md','IDENTITY.md']:
        old_file=original/'workspace'/leaf;new_file=target/'workspace'/leaf
        if old_file.read_bytes()!=new_file.read_bytes():
            assert leaf=='AGENTS.md' and (original/'workspace/TOOLS.md').exists(),'Unexpected core change: '+leaf
            expected=old_file.read_text().rstrip()+'\n\n## Tools\n\n### Local notes (migrated from TOOLS.md)\n\n'+(original/'workspace/TOOLS.md').read_text().strip()
            assert new_file.read_text().strip()==expected.strip(),'Unexpected AGENTS migration'
            migrated_tools=True
    result={'agent':name,'mode':mode,'preservationPassed':True,'toolsNotesFoldedExactly':migrated_tools,'databasesChecked':integrity(target),'cronCount':len(cron_rows(target)),'agentsCharacters':len((target/'workspace/AGENTS.md').read_text()),'bootstrapBudget':after['agents']['defaults'].get('bootstrapMaxChars',20000)}
    assert result['agentsCharacters']<=result['bootstrapBudget'],'Instruction allowance too small'
    save(mode+'-preservation.json',result);emit(result)

elif action == 'plugins':
    mode=extra[0];log=cli(mode,['plugins','list','--json'],mode+'-plugins',300)
    t=log.read_text();obj=json.loads(t[t.index('{'):]);result=[]
    for p in obj.get('plugins',[]):
        if p.get('enabled'):
            assert p.get('status') not in {'error','failed','blocked'},'Plugin failed: '+p['id']
            if str(p.get('version','')).startswith('2026.'):
                assert p['version']=='2026.10.4','Stale official plugin: '+p['id']
            result.append({k:p.get(k) for k in ['id','version','status']})
    assert result
    save(mode+'-plugin-gate.json',result);emit({'agent':name,'mode':mode,'pluginGatePassed':True,'plugins':result})

elif action == 'mem0':
    assert name=='harry' and extra[0] in {'rehearsal','live'}
    mode=extra[0]
    if mode=='live':assert (work/'rehearsal-mem0-passed.json').exists()
    cli(mode,['_mem0'],mode+'-mem0-compat',300)
    save(mode+'-mem0-passed.json',{'agent':name,'mode':mode,'passed':True})
    emit({'agent':name,'mode':mode,'mem0Passed':True})

elif action == 'mem0-inside':
    assert name=='harry'
    project=state/'npm/projects/mem0-openclaw-mem0-09729737ad__openclaw-generation__g-1e5cd6aa3ff70dae'
    manifest=project/'node_modules/@mem0/openclaw-mem0/openclaw.plugin.json'
    assert sha(manifest)=='b41def82737a590fe97633e2dbf1c95c1a4e2ad3019257bd16bd0e2b42122309'
    assert sha(manifest.parent/'dist/index.js')=='0e7205db54c8790c1aff7b09786ec0b7578db08181b5394a7137df4e530297c2'
    host=program/'node_modules/openclaw'
    assert json.loads((host/'package.json').read_text())['version']=='2026.10.4'
    assert json.loads((manifest.parent/'package.json').read_text())['version']=='1.2.1'
    js="""import fs from 'node:fs';
const [root,host]=process.argv.slice(1);
const {a:linkHost}=await import(host+'/dist/plugin-peer-link-D9lvYxJ1.mjs');
const r=await linkHost({installedDir:root,peerDependencies:{openclaw:'2026.10.4'},hostRoot:host,logger:console});
if(r.skipped||fs.realpathSync(root+'/node_modules/openclaw')!==host)throw Error('Host peer repair failed');
console.log('Verified Mem0 peer matches native 10.4 host');"""
    subprocess.run(['node','--input-type=module','-e',js,str(project),str(host)],check=True)
    subprocess.run(['bash',str(program/'ensure-mem0-110-compat.sh'),str(project)],check=True,timeout=180)
    before=json.loads((state/'openclaw.json').read_text())
    subprocess.run([str(program/'node_modules/.bin/openclaw'),'plugins','enable','openclaw-mem0','--accept-capabilities'],check=True,timeout=180)
    after=json.loads((state/'openclaw.json').read_text())
    assert before['plugins']==after['plugins'],'Unexpected plugin policy change'
    with sqlite3.connect('file:'+str(state/'state/openclaw.sqlite')+'?mode=ro',uri=True) as db:
        index=json.loads(db.execute("select value_json from config_machine_state where state_key='plugins.installedIndex'").fetchone()[0])['index']
        accepted=index['installRecords']['openclaw-mem0']['acceptedSurface']
    expected=set(json.loads(manifest.read_text())['contracts']['tools'])
    assert set(accepted['tools'])==expected
    assert not any(accepted.get(k) for k in ['channels','providers','hooks','mcpServers','cliCommands','cliBackends','dangerousConfigFlags'])
    assert sha(manifest.parent/'dist/index.js')=='0e7205db54c8790c1aff7b09786ec0b7578db08181b5394a7137df4e530297c2'
    emit({'retainedMem0Source':True,'acceptedExistingTools':sorted(expected),'hostPeerVerified':True})

elif action == 'install':
    if extra == ['proven']:
        assert name=='suzy' and json.loads((BASE/'frank/acceptance.json').read_text())['accepted']
        frank=BASE/'frank/extracted/root/.openclaw-frank'
        relative='npm/projects/vectorize-io-hindsight-openclaw-c23cf52a67__openclaw-generation__g-989ed928a8fa24e4/node_modules/@vectorize-io/hindsight-openclaw'
        for leaf in ['package.json','openclaw.plugin.json','dist/index.js']:
            assert sha(original/relative/leaf)==sha(frank/relative/leaf),'Unproved Hindsight cohort'
        fp=BASE/'frank/extracted/opt/openclaw-frank'
        assert json.loads((program/'package.json').read_text())==json.loads((fp/'package.json').read_text())
        assert (program/'start-suzy.sh').read_text().replace('suzy','frank').replace('4200','4300')==(fp/'start-frank.sh').read_text(),'Unproved startup difference'
        save('proven-cohort.json',{'pilot':'frank','hindsightSourceAndManifestMatch':True,'packagePolicyMatches':True,'launcherMatchesExceptIdentityPort':True})
    else:
        assert not extra
        assert (work/'rehearsal-preservation.json').exists() and (work/'rehearsal-plugin-gate.json').exists()
    assert service()['MainPID']=='0'
    assert not (work/'old-node_modules').exists()
    (program/'node_modules').rename(work/'old-node_modules')
    subprocess.run(['cp','-a',str(candidate/'node_modules'),str(program/'node_modules')],check=True)
    for p in ['package.json','package-lock.json']:shutil.copy2(candidate/p,program/p)
    emit({'agent':name,'installed':True,'version':json.loads((program/'node_modules/openclaw/package.json').read_text())['version']})

elif action == 'start':
    assert (work/'live-preservation.json').exists() and (work/'live-plugin-gate.json').exists()
    config=state/'openclaw.json';before=json.loads(config.read_text());after=json.loads(config.read_text())
    after.setdefault('mcp',{}).setdefault('sessionIdleTtlMs',600000)
    assert after['mcp']['sessionIdleTtlMs']==600000
    config.write_text(json.dumps(after,indent=2)+'\n')
    save('idle-cleanup.json',{'before':before.get('mcp',{}).get('sessionIdleTtlMs'),'after':600000})
    subprocess.run(['systemctl','start',unit],check=True,timeout=300)
    emit({'agent':name,'startRequested':True})

elif action == 'accept':
    port={'frank':4300,'harry':4100,'suzy':4200}[name]
    deadline=time.monotonic()+420
    while time.monotonic()<deadline:
        try:
            if urllib.request.urlopen('http://127.0.0.1:'+str(port)+'/healthz',timeout=5).status==200:break
        except Exception:pass
        time.sleep(5)
    else:raise RuntimeError('HTTP readiness deadline exceeded')
    health=rpc('health',suffix='after');assert health.get('ok') is True
    old=json.loads((work/'health-before.json').read_text())
    for channel,details in old.get('channels',{}).items():
        for account,values in details.get('accounts',{}).items():
            now=health.get('channels',{}).get(channel,{}).get('accounts',{}).get(account,{})
            for field in ['running','connected']:
                if values.get(field) is True:assert now.get(field) is True,'Channel regression: '+channel
    cron=rpc('cron.list',{'includeDisabled':True},'after')
    keys=['id','name','enabled','schedule','sessionTarget','wakeMode','payload','delivery']
    normalize=lambda o:sorted([{k:j.get(k) for k in keys} for j in o['jobs']],key=lambda j:j['id'])
    assert normalize(cron)==normalize(json.loads((work/'cron.list-before.json').read_text()))
    memory='mem0_search' if name=='harry' else 'agent_knowledge_recall'
    prompt='Read-only upgrade acceptance. Use '+memory+' explicitly to recall one existing ZedBiz memory from your configured backend, not local Markdown. Get your own Asana user identity and fetch Notion page ee1a3e33d58183948bd58119d92c7d01. Check availability of gog, himalaya, ffmpeg, ntn and gh using a harmless shell command. Return only memory tool and short recalled fact, Asana name/GID, Notion title and binary availability. Report any failure. Do not send messages, create tasks, change files, write memories or delegate.'
    log=cli('live',['agent','--agent','main','--session-key','agent:main:cody-vps2-10-4-acceptance','--message',prompt,'--timeout','240','--json'],'capability',300)
    t=log.read_text();obj=json.loads(t[t.index('{'):]);receipt=obj.get('result',{}).get('meta',{}).get('agentMeta',{}).get('terminalReceipt',{})
    assert receipt.get('rerouted') is False and receipt['effective']['model']=='gpt-6.1-sol','Actual route/fallback failed'
    names=receipt.get('successfulToolNames',[])
    assert any(memory in n for n in names) and any('asana_get_user' in n for n in names) and any('notion' in n and 'fetch' in n for n in names),'Required tool absent'
    current=service();assert current['ActiveState']=='active' and current['Result']=='success' and current['NRestarts']=='0'
    assert json.loads((program/'node_modules/openclaw/package.json').read_text())['version']=='2026.10.4'
    result={'agent':name,'accepted':True,'service':current,'cronCount':len(cron['jobs']),'receipt':receipt,'payloads':obj['result'].get('payloads'),'channels':{k:{a:{f:v.get(f) for f in ['running','connected','lastError']} for a,v in d.get('accounts',{}).items()} for k,d in health.get('channels',{}).items()}}
    save('acceptance.json',result);emit(result)
elif action == 'final':
    accepted=json.loads((work/'acceptance.json').read_text());current=service()
    assert accepted['accepted'] and current['MainPID']==accepted['service']['MainPID']
    assert current['NRestarts']=='0' and current['ActiveState']=='active' and current['Result']=='success'
    assert subprocess.check_output(['systemctl','is-enabled',unit],text=True).strip()=='enabled'
    assert json.loads((program/'node_modules/openclaw/package.json').read_text())['version']=='2026.10.4'
    assert urllib.request.urlopen('https://'+name+'.zbiz.ca/healthz',timeout=15).status==200
    c=json.loads((state/'openclaw.json').read_text());assert c['mcp']['sessionIdleTtlMs']==600000
    assert sha(program/('start-'+name+'.sh'))==json.loads((work/'baseline.json').read_text())['launcherSha256']
    diagnostic=program/'node_modules/openclaw/dist/diagnostic-B-cJgPjo.mjs'
    assert sha(diagnostic)=='5a90246ba060c9293360fa67d042e7694de207739bc1600a6c76d39a4dea9d6f'
    for saved in (work/'extracted/etc').rglob('*'):
        if saved.is_file():assert saved.read_bytes()==(Path('/etc')/saved.relative_to(work/'extracted/etc')).read_bytes(),'Service definition drift'
    cg=Path('/sys/fs/cgroup/system.slice')/unit
    stats=dict(line.split() for line in (cg/'memory.stat').read_text().splitlines())
    usage=int((cg/'memory.current').read_text());pss=0
    for pid in (cg/'cgroup.procs').read_text().split():
        try:
            for line in Path('/proc/'+pid+'/smaps_rollup').read_text().splitlines():
                if line.startswith('Pss:'):pss+=int(line.split()[1])*1024
        except (FileNotFoundError,ProcessLookupError):pass
    result={'agent':name,'finalPassed':True,'service':current,'version':'2026.10.4','publicHttp':200,'launcherPreserved':True,'serviceDefinitionsPreserved':True,'diagnosticModuleSha256':sha(diagnostic),'packageLockSha256':sha(program/'package-lock.json'),'memoryCurrent':usage,'memoryMinusInactiveFile':usage-int(stats.get('inactive_file',0)),'processPss':pss,'memoryEvents':dict(line.split() for line in (cg/'memory.events').read_text().splitlines())}
    save('final.json',result);emit(result)
else:
    raise ValueError('Unknown stage')
