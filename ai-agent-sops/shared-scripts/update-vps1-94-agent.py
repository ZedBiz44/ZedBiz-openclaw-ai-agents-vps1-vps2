#!/usr/bin/env python3
"""One authorized VPS1 agent per invocation. Private backups retain credentials."""
import pathlib, json, subprocess, sys, os, time, hashlib, re
NAMES={'edith','vivian','maggie','inga','gohzed','grogar','wilma','victor','marsha','amanda'}
name=sys.argv[1]; assert name in NAMES
image=sys.argv[2]
root=pathlib.Path('/opt/openclaw/agents')/name
base=pathlib.Path('/home/jackadmin/openclaw-backups/fleet94-20260912')
base.mkdir(mode=0o700,exist_ok=True)
b=base/name; b.mkdir(mode=0o700)
stage=b/'stage'; stage.mkdir()
def run(cmd, log=None):
    r=subprocess.run(cmd,text=True,capture_output=True)
    if log: (b/log).write_text(r.stdout+r.stderr)
    if r.returncode: raise RuntimeError('Command failed; inspect '+str(b/log) if log else 'Command failed: '+cmd[0])
    return r.stdout
info=json.loads(run(['docker','inspect',name]))[0]
(b/'inspect.private.json').write_text(json.dumps(info));os.chmod(b/'inspect.private.json',0o600)
env=b/'runtime.private.env'
env.write_text('\n'.join(x for x in info['Config']['Env'] if not x.startswith('HOSTNAME='))+'\n');os.chmod(env,0o600)
def maintenance(args,log,entry='node',network='openclaw',user=None):
    cmd=['docker','run','--rm','--network',network,'--memory','2g','--env-file',str(env),'--entrypoint',entry]
    if user: cmd+=['--user',user]
    for m in info['Mounts']:
        src=m['Source'];dst=m['Destination']
        if src in ['/var/run/docker.sock','/dev/shm']: continue
        if src.startswith(str(root)+'/'): src=str(stage)+src[len(str(root)):]; ro='' if m['RW'] else ':ro'
        else: ro=':ro'
        cmd+=['-v',src+':'+dst+ro]
    cmd+=['-v',str(base)+'/archive-empty-workshop-backups.mjs:/tmp/archive-empty-workshop-backups.mjs:ro',image]+args
    return run(cmd,log)
run(['docker','image','inspect',image])
run(['docker','stop','--time','60',name],'stop.log')
promoted=False
try:
    # Offline full-state archive, independently extracted to the rehearsal copy.
    run(['docker','run','--rm','-v',str(root)+':/source:ro','-v',str(b)+':/backup','alpine','sh','-ec',
        'umask 077; tar -cf /backup/full-state.tar -C /source .; tar -xf /backup/full-state.tar -C /backup/stage; cmp /source/config/openclaw.json /backup/stage/config/openclaw.json; chown 1001:1001 /backup/full-state.tar'],'backup.log')
    h=hashlib.file_digest(open(b/'full-state.tar','rb'),'sha256').hexdigest();(b/'backup.sha256').write_text(h+'\n')
    print(name+' BACKUP_RESTORED '+h,flush=True)
    js="""const fs=require('fs');const {DatabaseSync}=require('node:sqlite');
const p='/home/node/.openclaw/openclaw.json';const c=JSON.parse(fs.readFileSync(p));
const db=new DatabaseSync('/home/node/.openclaw/state/openclaw.sqlite',{readOnly:true});
if(db.prepare('pragma integrity_check').get().integrity_check!=='ok')throw Error('Database integrity failed');db.close();
c.tools??={};c.tools.sessions??={};c.tools.sessions.visibility??='tree';c.tools.swarm??=false;c.tools.agentToAgent??={enabled:false};
c.agents.defaults.subagents??={};c.agents.defaults.subagents.maxSpawnDepth??=1;
fs.writeFileSync(p,JSON.stringify(c,null,2)+'\\n');console.log('POLICY_AND_DATABASE_OK');"""
    maintenance(['-e',js],'policy.log',network='none')
    raw=maintenance(['/app/openclaw.mjs','plugins','list','--json'],'plugins-before.json')
    j=json.loads(raw[raw.index('{'):])
    external=[p for p in j['plugins'] if p.get('origin')=='global']
    for p in external:
        source=p['source']; match=re.search(r'/node_modules/(@[^/]+/[^/]+)/',source)
        assert match, 'Cannot resolve package '+p['id']
        pkg=match.group(1)
        if pkg.startswith('@openclaw/'):
            maintenance(['/app/openclaw.mjs','plugins','update',pkg+'@2026.9.4'],'update-'+p['id']+'.log')
        elif p['id'] in ['openclaw-mem0','hindsight-openclaw']:
            maintenance(['/app/openclaw.mjs','plugins','enable',p['id'],'--accept-capabilities'],'enable-'+p['id']+'.log')
        else: raise RuntimeError('Unreviewed external plugin '+p['id'])
        print(name+' PLUGIN '+p['id'],flush=True)
    maintenance(['/tmp/archive-empty-workshop-backups.mjs','/home/node/.openclaw'],'workshop.log',user='root')
    maintenance(['/app/openclaw.mjs','config','validate'],'validate.log')
    raw=maintenance(['/app/openclaw.mjs','doctor','--post-upgrade','--json'],'post-upgrade.json')
    j=json.loads(raw[raw.index('{'):]); assert not j['findings'], 'Post-upgrade findings'
    if name=='victor':
        run(['docker','run','--rm','-v',str(base/'Dockerfile.victor')+':/source:ro','-v',str(stage)+':/stage','alpine','sh','-ec','cat /source > /stage/Dockerfile.victor'],'victor-build-source.log')
    # Update only the selected image reference in the staged compose/env files.
    edit="""const fs=require('fs');const base='/stage';const image=process.argv[1];
let f=base+'/.env';let s=fs.readFileSync(f,'utf8');if(!/^OPENCLAW_IMAGE=/m.test(s))throw Error('Image variable absent');s=s.replace(/^OPENCLAW_IMAGE=.*$/m,'OPENCLAW_IMAGE='+image);fs.writeFileSync(f,s);
f=base+'/docker-compose.yml';s=fs.readFileSync(f,'utf8');s=s.replace(/^(\\s*image:\\s*)(?:zedbiz[^\\s]*openclaw[^\\s]*)\\s*$/m,'$1'+image);fs.writeFileSync(f,s);"""
    run(['docker','run','--rm','--user','root','-v',str(stage)+':/stage','--entrypoint','node',image,'-e',edit,image],'image-edit.log')
    # Preserve the entire old directory as an immediate rollback target.
    run(['docker','run','--rm','-v','/:/host','alpine','sh','-ec',
        'test ! -e /host'+str(b)+'/original; test -d /host'+str(root)+'; test -d /host'+str(stage)+'; mv /host'+str(root)+' /host'+str(b)+'/original; mv /host'+str(stage)+' /host'+str(root)],'promote.log')
    promoted=True
    run([str(root/('op-start-'+name+'.sh')),'up'],'start.log')
    interval=info['Config'].get('Healthcheck',{}).get('Interval',30000000000)/1000000000
    for _ in range(max(60,int(interval/3)+40)):
        state=json.loads(run(['docker','inspect',name]))[0]['State']
        if state.get('Health',{}).get('Status')=='healthy':break
        time.sleep(3)
    else: raise RuntimeError('Gateway did not become healthy')
    run(['docker','exec',name,'openclaw','config','validate'],'live-validate.log')
    run(['docker','exec',name,'openclaw','doctor','--post-upgrade','--json'],'live-post-upgrade.json')
    run(['docker','exec',name,'openclaw','plugins','list','--json'],'live-plugins.json')
    run(['docker','exec',name,'openclaw','--version'],'version.txt')
    print(name+' CORE_READY_FOR_LIVE_TEST',flush=True)
except Exception:
    if not promoted: run(['docker','start',name],'old-restart.log')
    # If promoted, leave evidence intact for explicit diagnosis/rollback.
    raise
