import sys
exec(open('/root/cody-vps2-followup-20261023/followup.py').read().split("if action==")[0])
n=sys.argv[2];assert n in ['frank','suzy'];w=B/('hindsight-'+n);s=Path('/root/.openclaw-'+n);program=Path('/opt/openclaw-'+n)
def mapped(args,label):
 e,p=context(n)
 with (w/(label+'.log')).open('w') as out:run(p+['unshare','--mount','--propagation','private','python3',__file__,'namespace',n,*args],env=e,stdout=out,stderr=subprocess.STDOUT,timeout=900)
def prepare_config(root):
 p=root/'openclaw.json';c=json.loads(p.read_text());m=c['plugins']['entries']['hindsight-openclaw']['config'];m['memoryMode']='context';m['allowKnowledgeDelete']=False;p.write_text(json.dumps(c,indent=2)+'\n')
def verify(mode):
 root=w/'state' if mode=='rehearsal' else s
 old=json.loads((w/'config-before.json').read_text());new=json.loads((root/'openclaw.json').read_text())
 expected=json.loads(json.dumps(old));expected['plugins']['entries']['hindsight-openclaw']['config'].update(memoryMode='context',allowKnowledgeDelete=False)
 assert new==expected,'Unexpected configuration drift'
 for leaf in ['AGENTS.md','SOUL.md','USER.md','IDENTITY.md']:
  assert sha(root/'workspace'/leaf)==json.loads((w/'baseline.json').read_text())['instructions'][leaf]
 args=['plugins','list','--json']
 if mode=='rehearsal':mapped(args,'rehearsal-plugins');d=obj(w/'rehearsal-plugins.log')
 else:d=obj(oc(n,args,'hindsight-live-plugins'))
 p=next(p for p in d['plugins'] if p['id']=='hindsight-openclaw');assert p['status']=='loaded' and p['version']=='1.2.0'
 result={k:p.get(k) for k in ['id','version','status','toolNames','source']};(w/(mode+'-passed.json')).write_text(json.dumps(result));emit(result)
if action=='namespace':
 run(['mount','-t','tmpfs','-o','mode=1777','tmpfs','/tmp']);run(['mount','--bind',str(w/'state'),str(s)]);run(['mount','--bind',str(w/'program'),str(program)])
 os.execv(str(program/'node_modules/.bin/openclaw'),[str(program/'node_modules/.bin/openclaw'),*sys.argv[3:]])
elif action=='stage':
 if n=='suzy':assert json.loads((B/'frank-accepted.json').read_text())['accepted']
 w.mkdir(mode=0o700);idle(n);run(['systemctl','stop','openclaw-'+n],timeout=300)
 try:
  shutil.copy2(s/'openclaw.json',w/'config-before.json')
  baseline={'instructions':{leaf:sha(s/'workspace'/leaf) for leaf in ['AGENTS.md','SOUL.md','USER.md','IDENTITY.md']}}
  run(['tar','-C','/','--exclude='+str(s/'.op.token').lstrip('/'),'--exclude='+str(s/'.env.resolved').lstrip('/'),'-cf',str(w/'before.tar'),str(s).lstrip('/')],timeout=900)
  baseline['archiveSha256']=sha(w/'before.tar');(w/'baseline.json').write_text(json.dumps(baseline))
  dest=w/'restore';dest.mkdir();run(['tar','-xf',str(w/'before.tar'),'-C',str(dest)],timeout=900)
  (dest/str(s).lstrip('/')).rename(w/'state');shutil.copytree(program,w/'program',symlinks=True)
 finally:run(['systemctl','start','openclaw-'+n],timeout=300)
 mapped(['plugins','update','@vectorize-io/hindsight-openclaw@1.2.0','--accept-capabilities'],'rehearsal-update')
 prepare_config(w/'state')
 verify('rehearsal')
elif action=='resume-stage':
 assert sha(w/'before.tar')==json.loads((w/'baseline.json').read_text())['archiveSha256']
 assert not (w/'program').exists()
 assert (w/'state').resolve().is_relative_to(B.resolve());shutil.rmtree(w/'state')
 dest=w/'restore';dest.mkdir();run(['tar','-xf',str(w/'before.tar'),'-C',str(dest)],timeout=900)
 (dest/str(s).lstrip('/')).rename(w/'state');shutil.copytree(program,w/'program',symlinks=True)
 mapped(['plugins','update','@vectorize-io/hindsight-openclaw@1.2.0','--accept-capabilities'],'rehearsal-update');prepare_config(w/'state');verify('rehearsal')
elif action=='rehearse':
 p=w/'state/openclaw.json';c=json.loads(p.read_text());m=c['plugins']['entries']['hindsight-openclaw']['config'];m.pop('memoryMode',None);m.pop('allowKnowledgeDelete',None);p.write_text(json.dumps(c,indent=2)+'\n')
 mapped(['plugins','update','@vectorize-io/hindsight-openclaw@1.2.0','--accept-capabilities'],'rehearsal-update');prepare_config(w/'state');verify('rehearsal')
elif action=='install':
 assert (w/'rehearsal-passed.json').exists();idle(n);run(['systemctl','stop','openclaw-'+n],timeout=300)
 # Fresh SQLite/config recovery preserves work since the brief rehearsal capture.
 import sqlite3
 d=w/'activation';d.mkdir()
 for p in [s/'state/openclaw.sqlite',*s.glob('agents/*/agent/openclaw-agent.sqlite')]:
  dest=d/p.relative_to(s);dest.parent.mkdir(parents=True,exist_ok=True)
  with sqlite3.connect(p) as a,sqlite3.connect(dest) as z:a.backup(z)
 shutil.copy2(s/'openclaw.json',d/'openclaw.json')
 oc(n,['plugins','update','@vectorize-io/hindsight-openclaw@1.2.0','--accept-capabilities'],'hindsight-update',900)
 prepare_config(s)
 verify('live');run(['systemctl','start','openclaw-'+n],timeout=300)
else:raise ValueError(action)
