#!/usr/bin/env python3
import subprocess,json,pathlib,sys
name=sys.argv[1]
assert name in {'edith','vivian','maggie','inga','gohzed','grogar','wilma','victor','marsha','amanda'}
base=pathlib.Path('/home/jackadmin/openclaw-backups/fleet94-20260912')
b=base/name
def run(cmd):
 r=subprocess.run(cmd,text=True,capture_output=True)
 if r.returncode: raise RuntimeError('Command failed: '+cmd[0])
 return r.stdout
run(['docker','cp',str(base/'openclaw-94-fleet-verification.txt'),name+':/tmp/pilot94-test.txt'])
run(['docker','cp',str(base/'probe-imap-source-fetch.cjs'),name+':/tmp/probe-imap.cjs'])
imap=run(['docker','exec',name,'node','/tmp/probe-imap.cjs','/app','/home/node/.openclaw'])
(b/'live-imap.json').write_text(imap)
print(name+' IMAP '+imap.strip(),flush=True)
r=subprocess.run(['docker','exec',name,'openclaw','agent','--agent','main','--session-key','agent:main:pilot94-'+name+'-20260912','--message-file','/tmp/pilot94-test.txt','--timeout','300','--json'],text=True,capture_output=True)
(b/'live-test.json').write_text(r.stdout+r.stderr)
if r.returncode: raise RuntimeError('Agent test failed; inspect private live-test.json before any retry')
j=json.loads(r.stdout[r.stdout.index('{'):])
for p in j.get('result',j).get('payloads',[]):print(p.get('text',''),flush=True)
