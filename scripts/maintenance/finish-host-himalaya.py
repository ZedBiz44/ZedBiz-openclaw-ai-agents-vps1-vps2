import pathlib,subprocess,json,hashlib
b=pathlib.Path('/opt/openclaw/builds/vps1-email-20261003')
names=['terry','amanda','edith','gohzed','grogar','inga','maggie','marsha','victor','vivian','wilma']
for n in names:
 p=json.loads((b/n/'live-agent-proof-summary.json').read_text());assert p['tools']['failures']==0 and p['trace']['fallbackUsed'] is False
ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();containers=json.loads(subprocess.check_output(['docker','inspect',*ids]));old_users=[]
for c in containers:
 if any(m.get('Source')=='/usr/local/bin/himalaya' for m in c['Mounts']):old_users.append(c['Name'])
assert not old_users,'Other containers still use the old shared binary: '+str(old_users)
subprocess.run(['docker','run','--rm','--user','root','-v','/usr/local/bin:/hostbin','-v','/opt/openclaw/shared/bin:/shared:ro','-v',str(b)+':/maintenance','alpine:3.22','sh','-c','test ! -e /maintenance/himalaya-1.2.0 && cp -p /hostbin/himalaya /maintenance/himalaya-1.2.0 && cp /shared/himalaya-2.2.1 /hostbin/himalaya.new && chmod 755 /hostbin/himalaya.new && mv /hostbin/himalaya.new /hostbin/himalaya'],check=True)
expected=json.loads((b/'binary-provenance.json').read_text())['binarySha256'];assert hashlib.sha256(pathlib.Path('/usr/local/bin/himalaya').read_bytes()).hexdigest()==expected
print(subprocess.check_output(['/usr/local/bin/himalaya','--version'],text=True).splitlines()[0])
