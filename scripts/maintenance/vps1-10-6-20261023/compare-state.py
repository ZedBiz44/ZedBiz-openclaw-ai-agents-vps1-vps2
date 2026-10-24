"""Compare rehearsed migration against the verified offline archive."""
import hashlib,json,pathlib,sqlite3,tarfile
w=pathlib.Path('/opt/openclaw/backups/release-20261023/terry');stage=w/'rehearsal';ref=w/'comparison-original'
ref.mkdir(mode=0o700,exist_ok=True)
files={};skills={}
with tarfile.open(w/'state-before.tar.gz','r|gz') as tf:
 for m in tf:
  if not m.isfile():continue
  rel=m.name.removeprefix('./')
  if rel in ['config/openclaw.json','config/state/openclaw.sqlite','config/state/openclaw.sqlite-wal','config/state/openclaw.sqlite-shm']:
   p=ref/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(tf.extractfile(m).read())
  elif rel in ['workspace/AGENTS.md','workspace/SOUL.md','workspace/USER.md','workspace/IDENTITY.md','workspace/MEMORY.md','workspace/TOOLS.md']:
   files[rel]=tf.extractfile(m).read()
  elif rel.startswith(('skills/','workspace/skills/')):
   skills[rel]=hashlib.file_digest(tf.extractfile(m),'sha256').hexdigest()
before=json.loads((ref/'config/openclaw.json').read_text());after=json.loads((stage/'config/openclaw.json').read_text())
checks={}
for key in ['model','models','modelPolicy','thinkingDefault','timeoutSeconds']:
 checks['model.'+key]=before['agents']['defaults'].get(key)==after['agents']['defaults'].get(key)
for key in ['mcp','tools','channels']:
 checks[key]=before.get(key)==after.get(key)
checks['gatewayAuth']=before.get('gateway',{}).get('auth')==after.get('gateway',{}).get('auth')
checks['memorySlot']=before['plugins'].get('slots')==after['plugins'].get('slots')
memory=before['plugins']['slots']['memory'];checks['memoryConfig']=before['plugins']['entries'][memory]==after['plugins']['entries'][memory]
checks['customSkills']=all((stage/p).is_file() and hashlib.sha256((stage/p).read_bytes()).hexdigest()==h for p,h in skills.items())
instructionChanges=[]
for rel,old in files.items():
 p=stage/rel
 if not p.exists() or p.read_bytes()!=old:instructionChanges.append(rel)
 if rel=='workspace/AGENTS.md' and p.exists() and p.read_bytes()!=old:
  expected=old.decode().rstrip()+'\n\n## Tools\n\n### Local notes (migrated from TOOLS.md)\n\n'+files.get('workspace/TOOLS.md',b'').decode().strip()
  checks['instructions.'+rel]=p.read_text().strip()==expected.strip()
 elif rel=='workspace/TOOLS.md' and not p.exists():
  checks['instructions.'+rel]=files[rel].decode().strip() in (stage/'workspace/AGENTS.md').read_text()
 else:checks['instructions.'+rel]=p.is_file() and p.read_bytes()==old
def rows(root):
 with sqlite3.connect('file:'+str(root/'config/state/openclaw.sqlite')+'?mode=ro',uri=True) as db:
  cols=[x[1] for x in db.execute('pragma table_info(cron_jobs)')]
  return cols,db.execute('select * from cron_jobs').fetchall()
cols,old=rows(ref);cols2,new=rows(stage);assert cols==cols2
idx=cols.index('declaration_key')
retired=[r for r in old if str(r[idx]).startswith('skill-collection-review:')]
retained=[r for r in old if r not in retired]
checks['schedules']=sorted(retained)==sorted(new)
databases=[]
for p in [stage/'config/state/openclaw.sqlite',*(stage/'agents').glob('*/agent/openclaw-agent.sqlite')]:
 with sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True) as db:
  db.create_function('octet_length',1,lambda x:len(x.encode() if isinstance(x,str) else x),deterministic=True)
  assert db.execute('pragma quick_check').fetchall()==[('ok',)]
 databases.append(str(p.relative_to(stage)))
result={'checks':checks,'instructionChanges':instructionChanges,'originalJobs':len(old),'retiredBuiltinReviewJobs':len(retired),'remainingJobs':len(new),'customSkillFiles':len(skills),'databases':databases,'passed':all(checks.values())}
(w/'rehearsal-preservation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result),flush=True)
assert result['passed'],'Migration changed protected settings or content; investigate before activation'

