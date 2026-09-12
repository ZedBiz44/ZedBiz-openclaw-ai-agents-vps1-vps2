#!/usr/bin/env python3
"""Qualified 9.4 artifact preparation or one authorized VPS2 native cutover."""
import pathlib,subprocess,json,os,sys,shutil,hashlib,re
n=sys.argv[1];mode=sys.argv[2];assert n in {'suzy','frank'} and mode in {'prepare','upgrade'}
install=pathlib.Path('/opt/openclaw-'+n);candidate=pathlib.Path(str(install)+'-2026.9.4-pilot')
state=pathlib.Path('/root/.openclaw-'+n);base=pathlib.Path('/root/openclaw-fleet94-20260912');base.mkdir(mode=0o700,exist_ok=True)
b=base/n;b.mkdir(mode=0o700,exist_ok=True)
def run(cmd,log=None,env=None):
 r=subprocess.run(cmd,text=True,capture_output=True,env=env)
 if log:(b/log).write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError('Command failed; inspect '+str(b/log) if log else 'Command failed: '+cmd[0])
 return r.stdout
def parsed(s):return json.JSONDecoder().raw_decode(s[s.index('{'):])[0]
if mode=='prepare':
 assert not candidate.exists()
 old=json.load(open(install/'package.json'));assert set(old.get('dependencies',{}))=={'openclaw'}
 shutil.copytree(install,candidate,symlinks=True,ignore=shutil.ignore_patterns('node_modules'))
 qualified=pathlib.Path('/opt/openclaw-harry')
 shutil.copytree(qualified/'node_modules',candidate/'node_modules',symlinks=True)
 for f in ['package.json','package-lock.json','patch-imap-source-fetch.mjs','test-imap-source-fetch.mjs','probe-imap-source-fetch.cjs']:
  shutil.copy2(qualified/f,candidate/f)
 p=json.load(open(candidate/'package.json'));p['name']=old['name'];(candidate/'package.json').write_text(json.dumps(p,indent=2)+'\n')
 lock=json.load(open(candidate/'package-lock.json'))
 assert lock['packages']['node_modules/openclaw']['integrity']=='sha512-lTQpEEe1Xm3u2PCHaPEr+vP8paGk1vLdHuzdItsNToaLI6hAqRVvgJYg+GxukJhETJp4tPy/S1Gftl4KuB8n7A=='
 lock['name']=old['name'];lock['packages']['']['name']=old['name'];(candidate/'package-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
 assert hashlib.sha256((candidate/'node_modules/openclaw/dist/extensions/imap/index.js').read_bytes()).hexdigest()=='280c7f32fbd8911abb96338a891ac869394357e500c4a24366e0d7f325ed3bea'
 assert (candidate/('start-'+n+'.sh')).read_bytes()==(install/('start-'+n+'.sh')).read_bytes()
 print(n+' QUALIFIED_NATIVE_ARTIFACT_PREPARED');sys.exit(0)
assert candidate.exists() and not (b/'full-state.tar').exists()
unit='openclaw-'+n
env=os.environ.copy();env['OP_SERVICE_ACCOUNT_TOKEN']=(state/'.op.token').read_text().strip()
env.update(HOME=str(state),OPENCLAW_STATE_DIR=str(state),OPENCLAW_CONFIG_PATH=str(state/'openclaw.json'),NODE_OPTIONS='--max-old-space-size=1536')
run(['systemctl','stop',unit],'stop.log')
promoted=False
try:
 paths=[str(state).lstrip('/'),str(install).lstrip('/'),'etc/systemd/system/'+unit+'.service']
 drop=pathlib.Path('/etc/systemd/system/'+unit+'.service.d')
 if drop.exists():paths.append(str(drop).lstrip('/'))
 run(['tar','-cf',str(b/'full-state.tar'),'-C','/']+paths,'backup.log')
 (b/'backup.sha256').write_text(hashlib.file_digest(open(b/'full-state.tar','rb'),'sha256').hexdigest()+'\n')
 proof=b/'restore-proof';proof.mkdir();run(['tar','-xf',str(b/'full-state.tar'),'-C',str(proof)],'restore.log')
 copied=proof/str(state).lstrip('/')
 assert (copied/'openclaw.json').read_bytes()==(state/'openclaw.json').read_bytes()
 import sqlite3
 with sqlite3.connect('file:'+str(copied/'state/openclaw.sqlite')+'?mode=ro',uri=True) as db:assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
 print(n+' OFFLINE_BACKUP_RESTORE_VERIFIED',flush=True)
 c=json.load(open(copied/'openclaw.json'));t=c.setdefault('tools',{});t.setdefault('sessions',{}).setdefault('visibility','tree');t.setdefault('swarm',False);t.setdefault('agentToAgent',{'enabled':False});c.setdefault('agents',{}).setdefault('defaults',{}).setdefault('subagents',{}).setdefault('maxSpawnDepth',1)
 (copied/'openclaw.json').write_text(json.dumps(c,indent=2)+'\n')
 def cli(args,log):
  script='set -e; mount -t tmpfs tmpfs /tmp; mount --bind '+str(copied)+' '+str(state)+'; mount --bind '+str(candidate)+' '+str(install)+'; exec '+str(install/'node_modules/.bin/openclaw')+' "$@"'
  return run(['op','run','--env-file='+str(state/'.env'),'--','unshare','--mount','--propagation','private','--pid','--fork','--mount-proc','bash','-c',script,'bash']+args,log,env)
 raw=cli(['plugins','list','--json'],'plugins-before.json');plugins=parsed(raw)['plugins']
 for p in plugins:
  if p.get('origin')!='global':continue
  m=re.search(r'/node_modules/(@[^/]+/[^/]+)/',p['source']);assert m
  pkg=m.group(1)
  if pkg.startswith('@openclaw/'):cli(['plugins','update',pkg+'@2026.9.4'],'update-'+p['id']+'.log')
  elif p['id']=='hindsight-openclaw':cli(['plugins','enable',p['id'],'--accept-capabilities'],'enable-hindsight.log')
  else:raise RuntimeError('Unreviewed external plugin '+p['id'])
  print(n+' PLUGIN '+p['id'],flush=True)
 run(['node',str(base/'archive-empty-workshop-backups.mjs'),str(copied)],'workshop.log')
 cli(['config','validate'],'validate.log');assert not parsed(cli(['doctor','--post-upgrade','--json'],'post-upgrade.json'))['findings']
 old_install=pathlib.Path(str(install)+'.pre94-20260912');old_state=pathlib.Path(str(state)+'.pre94-20260912')
 assert not old_install.exists() and not old_state.exists()
 install.rename(old_install);candidate.rename(install);state.rename(old_state);copied.rename(state);promoted=True
 run(['systemctl','start',unit],'start.log');run(['systemctl','is-active',unit],'active.txt')
 print(n+' CORE_READY_FOR_LIVE_TEST',flush=True)
except Exception:
 if not promoted:run(['systemctl','start',unit],'old-restart.log')
 raise
