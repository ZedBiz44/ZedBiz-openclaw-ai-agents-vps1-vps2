#!/usr/bin/env python3
import pathlib,subprocess,json,os,sys,hashlib
n=sys.argv[1];assert n in {'suzy','frank'}
state=pathlib.Path('/root/.openclaw-'+n);install=pathlib.Path('/opt/openclaw-'+n)
base=pathlib.Path('/root/openclaw-fleet94-20260912');b=base/n
env=os.environ.copy();env['OP_SERVICE_ACCOUNT_TOKEN']=(state/'.op.token').read_text().strip()
env.update(HOME=str(state),OPENCLAW_STATE_DIR=str(state),OPENCLAW_CONFIG_PATH=str(state/'openclaw.json'),NODE_OPTIONS='--max-old-space-size=1536')
def protected(args,log):
 r=subprocess.run(['op','run','--env-file='+str(state/'.env'),'--']+args,text=True,capture_output=True,env=env)
 (b/log).write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError('Check failed; inspect '+str(b/log)+' before retrying')
 return r.stdout
def cli(args,log):return protected([str(install/'node_modules/.bin/openclaw')]+args,log)
def parsed(s):return json.JSONDecoder().raw_decode(s[s.index('{'):])[0]
cli(['config','validate'],'live-validate.log')
post=parsed(cli(['doctor','--post-upgrade','--json'],'live-post-upgrade.json'));assert not post['findings']
cli(['plugins','list','--json'],'live-plugins.json')
print(n+' '+protected(['node',str(install/'probe-imap-source-fetch.cjs'),str(install/'node_modules/openclaw'),str(state)],'live-imap.json').strip(),flush=True)
old=pathlib.Path(str(state)+'.pre94-20260912');a=json.load(open(old/'openclaw.json'));c=json.load(open(state/'openclaw.json'))
slot=a['plugins']['slots']['memory']
audit={'agent':n,'modelUnchanged':a['agents']['defaults'].get('model')==c['agents']['defaults'].get('model'),'memorySlotUnchanged':slot==c['plugins']['slots']['memory'],'memoryConfigUnchanged':a['plugins']['entries'][slot].get('config')==c['plugins']['entries'][slot].get('config'),'sessionVisibilityPreserved':a.get('tools',{}).get('sessions',{}).get('visibility','tree')==c.get('tools',{}).get('sessions',{}).get('visibility'),'files':{}}
for f in ['AGENTS.md','TOOLS.md']:
 x=old/'workspace'/f;y=state/'workspace'/f
 audit['files'][f]='absent-both' if not x.exists() and not y.exists() else 'unchanged' if x.exists() and y.exists() and x.read_bytes()==y.read_bytes() else 'CHANGED'
audit['startupUnchanged']=(pathlib.Path(str(install)+'.pre94-20260912')/('start-'+n+'.sh')).read_bytes()==(install/('start-'+n+'.sh')).read_bytes()
audit['backupSha256']=(b/'backup.sha256').read_text().strip()
(b/'final-audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit),flush=True)
assert audit['modelUnchanged'] and audit['memorySlotUnchanged'] and audit['memoryConfigUnchanged'] and audit['sessionVisibilityPreserved'] and audit['startupUnchanged']
assert 'CHANGED' not in audit['files'].values()
raw=cli(['agent','--agent','main','--session-key','agent:main:pilot94-'+n+'-20260912','--message-file',str(base/'openclaw-94-fleet-verification.txt'),'--timeout','300','--json'],'live-test.json')
j=parsed(raw)
for p in j.get('result',j).get('payloads',[]):print(p.get('text',''),flush=True)
