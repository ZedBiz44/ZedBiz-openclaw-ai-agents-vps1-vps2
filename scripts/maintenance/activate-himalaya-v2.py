import subprocess,pathlib,json,sys,os,time,hashlib
n=sys.argv[1];assert n in ['terry','amanda','edith','gohzed','grogar','inga','maggie','marsha','victor','vivian','wilma']
b=pathlib.Path('/opt/openclaw/builds/vps1-email-20261003');w=b/n
proof=json.loads((w/'verification-candidate.json').read_text());assert proof['imapAuth'] and proof['smtpAuth'] and proof['draftCompose']
if n!='terry':assert (b/'terry/live-agent-proof-summary.json').exists(),'Terry live agent pilot must pass first'
c=json.loads(subprocess.check_output(['docker','inspect',n]))[0];labels=c['Config']['Labels'];compose=pathlib.Path(labels['com.docker.compose.project.config_files']);text=compose.read_text()
assert not (w/'activation.log').exists(),'Inspect previous activation before rerunning'
old='/usr/local/bin/himalaya:/usr/local/bin/himalaya';new='/opt/openclaw/shared/bin/himalaya-2.2.1:/usr/local/bin/himalaya'
assert text.count(old)==1,'Expected exactly one binary mount';updated=text.replace(old,new)
for filename,data in [('compose-before.yml',text),('compose-after.yml',updated)]:p=w/filename;p.write_text(data);os.chmod(p,0o600)
raw=subprocess.check_output(['docker','exec',n,'cat','/home/node/.openclaw/openclaw.json']);(w/'openclaw-before.json').write_bytes(raw);os.chmod(w/'openclaw-before.json',0o600)
workspace=next(m['Source'] for m in c['Mounts'] if m['Destination']=='/home/node/.openclaw/workspace')
# Let the gateway release its SQLite ownership before recreating the container.
# Docker's shell entrypoint does not reliably forward its stop signal to this child.
subprocess.run(['docker','update','--restart=no',n],check=True,stdout=subprocess.DEVNULL)
owner_code="import sqlite3,json; c=sqlite3.connect('file:/home/node/.openclaw/state/openclaw.sqlite?mode=ro',uri=True); r=c.execute(\"select payload_json from state_leases where scope='gateway-owner' and lease_key='global'\").fetchone(); print(r[0] if r else '{}')"
owner=json.loads(subprocess.check_output(['docker','exec',n,'python3','-c',owner_code])).get('owner',{})
if owner.get('host')==c['Config']['Hostname'] and isinstance(owner.get('pid'),int):
 subprocess.run(['docker','exec',n,'kill','-TERM',str(owner['pid'])],check=True)
 for _ in range(66):
  live=json.loads(subprocess.check_output(['docker','inspect',n]))[0]
  if not live['State']['Running']:break
  time.sleep(5)
subprocess.run(['docker','stop','-t','30',n],check=True,stdout=subprocess.DEVNULL)
try:
 subprocess.run(['docker','run','--rm','--user','root','--entrypoint','python3','-v',str(b)+':/maintenance','-v',workspace+':/agent',c['Config']['Image'],'/maintenance/deploy-email-files.py',n],check=True)
 subprocess.run(['docker','run','--rm','-v',str(compose.parent)+':/target','-v',str(w)+':/source:ro','alpine:3.22','sh','-c','cat /source/compose-after.yml > /target/'+compose.name],check=True)
 wrapper=compose.parent/('op-start-'+n+'.sh');assert wrapper.is_file()
 with (w/'activation.log').open('w') as f:subprocess.run([str(wrapper),'up'],stdout=f,stderr=subprocess.STDOUT,check=True)
except Exception:
 subprocess.run(['docker','start',n],stdout=subprocess.DEVNULL);raise
for _ in range(100):
 p=subprocess.run(['docker','exec',n,'curl','-fsS','--max-time','3','http://127.0.0.1:'+str(json.loads(raw)['gateway']['port'])+'/healthz'],capture_output=True)
 if p.returncode==0:break
 time.sleep(5)
else:raise RuntimeError('Gateway failed to start')
after=json.loads(subprocess.check_output(['docker','exec',n,'cat','/home/node/.openclaw/openclaw.json']));before=json.loads(raw)
current=json.loads(subprocess.check_output(['docker','inspect',n]))[0];environment=dict(x.split('=',1) for x in current['Config']['Env'])
assert all(environment.get(k) and not environment[k].startswith(('op://','${')) for k in ['EMAIL_ADDRESS','EMAIL_PASSWORD']), 'Protected startup did not resolve email credentials'
assert after['agents']['defaults']['model']==before['agents']['defaults']['model'] and after['auth']==before['auth']
skill=subprocess.check_output(['docker','exec',n,'cat','/home/node/.openclaw/workspace/skills/himalaya/SKILL.md']);assert hashlib.sha256(skill).digest()==hashlib.sha256((b/'himalaya/SKILL.md').read_bytes()).digest()
version=subprocess.check_output(['docker','exec',n,'himalaya','--version'],text=True).splitlines()[0];assert version.startswith('himalaya v2.2.1 ')
r={'agent':n,'version':version,'gatewayHealthy':True,'modelAndAuthPreserved':True,'skillSha256':hashlib.sha256(skill).hexdigest(),'binaryMount':'/opt/openclaw/shared/bin/himalaya-2.2.1'};(w/'activation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
