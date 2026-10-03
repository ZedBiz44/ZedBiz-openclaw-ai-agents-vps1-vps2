import subprocess,json,pathlib,os,tomllib,re,urllib.request,hashlib
b=pathlib.Path('/opt/openclaw/builds/vps1-email-20261003');b.mkdir(exist_ok=True,mode=0o700)
stage=pathlib.Path('/opt/openclaw/builds/2026.9.8-terry-20261003/tools-stage')
release=json.load(urllib.request.urlopen('https://api.github.com/repos/pimalaya/himalaya/releases/tags/v2.2.1'))
asset=next(a for a in release['assets'] if a['name']=='himalaya.x86_64-linux.tgz')
actual=hashlib.sha256((stage/asset['name']).read_bytes()).hexdigest();assert asset['digest']=='sha256:'+actual
(b/'binary-provenance.json').write_text(json.dumps({'version':'2.2.1','url':asset['browser_download_url'],'archiveSha256':actual,'binarySha256':hashlib.sha256((stage/'himalaya').read_bytes()).hexdigest()},indent=2))
names=['terry','amanda','edith','gohzed','grogar','inga','maggie','marsha','victor','vivian','wilma']
def docker(n,*a,**kw):return subprocess.run(['docker','exec',n,*a],capture_output=True,check=True,**kw).stdout
out=[]
for n in names:
 c=json.loads(subprocess.check_output(['docker','inspect',n]))[0];env=dict(x.split('=',1) for x in c['Config']['Env'])
 assert env.get('EMAIL_ADDRESS') and env.get('EMAIL_PASSWORD'),n+' lacks protected email credentials'
 folder=b/n;folder.mkdir(exist_ok=True,mode=0o700)
 raw=subprocess.run(['docker','exec',n,'cat','/home/node/.config/himalaya/config.toml'],capture_output=True)
 if raw.returncode==0:
  cfg=tomllib.loads(raw.stdout.decode());a=cfg['accounts']['default'];assert len(cfg['accounts'])==1
  if not (folder/'config-v1.toml').exists():(folder/'config-v1.toml').write_bytes(raw.stdout);os.chmod(folder/'config-v1.toml',0o600)
 else:
  assert n=='edith'
  a={'email':'${EMAIL_ADDRESS}','display-name':'Edith','folder':{'aliases':{'inbox':'INBOX','sent':'INBOX.Sent','drafts':'INBOX.Drafts','trash':'INBOX.Trash'}},'backend':{'type':'imap','host':env['EMAIL_SERVER'],'port':int(env['EMAIL_IMAP_PORT']),'encryption':{'type':'tls'},'login':'${EMAIL_ADDRESS}','auth':{'type':'password','cmd':'printf %s "$EMAIL_PASSWORD"'}},'message':{'send':{'backend':{'type':'smtp','host':env['EMAIL_SERVER'],'port':int(env['EMAIL_SMTP_PORT']),'encryption':{'type':'tls'},'login':'${EMAIL_ADDRESS}','auth':{'type':'password','cmd':'printf %s "$EMAIL_PASSWORD"'}}}}}
 def expand(v):return re.sub(r'\$\{([A-Z_]+)\}',lambda m:env[m[1]],v)
 q=lambda v:json.dumps(v,ensure_ascii=False)
 lines=['[accounts.default]','default = true','email = '+q(expand(a['email'])),'display-name = '+q(expand(a.get('display-name',n.title())))]
 for role,value in a.get('folder',{}).get('aliases',a.get('folder',{}).get('alias',{})).items():lines.append('mailbox.alias.'+role+' = '+q(value))
 for proto,src in [('imap',a['backend']),('smtp',a['message']['send']['backend'])]:
  assert src['type']==proto and src['encryption']['type'] in ['tls','start-tls']
  assert src['auth']['type']=='password' and isinstance(src['auth'].get('cmd'),str)
  tls=src['encryption']['type']=='tls'
  lines += [proto+'.server = '+q(proto+('s' if tls else '')+'://'+expand(src['host'])+':'+str(src['port'])),proto+'.starttls = '+str(not tls).lower(),proto+'.sasl.plain.username = '+q(expand(src['login'])),proto+'.sasl.plain.password.command = '+q(src['auth']['cmd'])]
 config='\n'.join(lines)+'\n';tomllib.loads(config)
 p=folder/'config-v2.toml';p.write_text(config);os.chmod(p,0o600)
 subprocess.run(['docker','cp',str(p),n+':/tmp/cody-himalaya-v2.toml'],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['docker','cp',str(stage/'himalaya'),n+':/tmp/cody-himalaya-v2'],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['docker','exec','-u','root',n,'chown','node:node','/tmp/cody-himalaya-v2.toml'],check=True)
 docker(n,'chmod','600','/tmp/cody-himalaya-v2.toml')
 out.append({'agent':n,'existingConfig':raw.returncode==0,'emailEnvironmentPresent':True,'candidatePrepared':True})
(b/'staging.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
