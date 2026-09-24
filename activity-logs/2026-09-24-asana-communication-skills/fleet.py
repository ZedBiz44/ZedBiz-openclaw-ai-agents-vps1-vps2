import subprocess, json, pathlib, sys, hashlib
from concurrent.futures import ThreadPoolExecutor

B=pathlib.Path(__file__).parent
KEY=pathlib.Path('D:/Google Drive/Documents/Codex-Projects/.ssh')
COMMON=['z-asana-agent-control','z-agent-communication']
SPECIAL=['z-advanced-asana-control','z-asana-procedures']
HOSTS={1:'jackadmin@187.77.210.223',2:'root@harry.zbiz.ca',3:'root@ruby.zbiz.ca',4:'root@srv1849801.hstgr.cloud'}
VPS1=['amanda','edith','gohzed','grogar','inga','maggie','marsha','terry','victor','vivian','wilma']
TARGETS=[(1,n) for n in VPS1]+[(2,n) for n in ['harry','frank','suzy']]+[(3,'ruby'),(4,'rocky')]
def ssh(v,cmd,data=None):
 p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','-i',str(KEY/f'vps{v}-ssh-key.runtime'),HOSTS[v],cmd],input=data,encoding='utf-8',capture_output=True,timeout=120)
 if p.returncode:raise RuntimeError(f'{v}: {cmd}: {p.stderr}\n{p.stdout}')
 return p.stdout
def names(n):return COMMON+(SPECIAL if n in ['amanda','victor','terry','marsha','ruby'] else [])
def root(v,n):return '/home/node/.openclaw/workspace/skills' if v==1 else f'/root/.openclaw-{n}/workspace/skills' if v==2 else '/opt/hermes-ruby/skills' if v==3 else '/home/openclaw/.openclaw/workspace/skills'
def prefix(v,n):return f'docker exec -i {n} python3 -' if v==1 else 'python3 -'

mode=sys.argv[1]
manifest=json.loads((B/'manifest.json').read_text())
if mode=='preflight':
 def check(pair):
  v,n=pair; expected={s:list(manifest[s]) for s in names(n)}
  code='''import pathlib,json,hashlib\nroot=pathlib.Path(ROOT)\nassert root.is_dir(),root\nresult={}\nfor skill,files in EXPECTED.items():\n p=root/skill\n existing={str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()}\n extras=sorted(set(existing)-set(files))\n assert set(extras)<={'SKILL.md.before-task-memory-20260916'},(skill,extras)\n result[skill]={'exists':p.exists(),'extras':extras,'previous':existing}\nprint(json.dumps(result))\n'''.replace('ROOT',repr(root(v,n))).replace('EXPECTED',repr(expected))
  result=json.loads(ssh(v,prefix(v,n),code));(B/f'{n}-before.json').write_text(json.dumps(result,indent=2),encoding='utf-8');return {'agent':n,'preflight':'passed','skills':list(result)}
 with ThreadPoolExecutor(max_workers=4) as ex:
  for r in ex.map(check,TARGETS):print(json.dumps(r),flush=True)
elif mode=='install':
 # Amanda has already passed pilot; no further model turns are sent to other agents.
 installer=(B/'install.py').read_text(encoding='utf-8')
 for v in HOSTS:
  p=subprocess.run(['scp','-q','-i',str(KEY/f'vps{v}-ssh-key.runtime'),str(B/'skills-20260924.tar.gz'),HOSTS[v]+':/tmp/asana-communication-20260924.tar.gz'],capture_output=True,text=True)
  assert p.returncode==0,p.stderr
 for v,n in TARGETS:
  if n=='amanda':continue
  if v==1:ssh(v,f'docker cp /tmp/asana-communication-20260924.tar.gz {n}:/tmp/asana-communication-20260924.tar.gz')
  out=ssh(v,prefix(v,n)+' /tmp/asana-communication-20260924.tar.gz '+root(v,n)+' '+' '.join(names(n)),installer)
  (B/f'{n}-install.jsonl').write_text(out,encoding='utf-8')
  rows=[json.loads(x) for x in out.splitlines()];assert all(x['verified'] for x in rows) and len(rows)==len(names(n))
  print(json.dumps({'agent':n,'installed':list(x['skill'] for x in rows),'hashes':'matched'}),flush=True)
elif mode=='verify':
 def verify(pair):
  v,n=pair;expected={s:manifest[s] for s in names(n)}
  code='''import pathlib,json,hashlib\nroot=pathlib.Path(ROOT)\nfor skill,files in EXPECTED.items():\n for rel,digest in files.items():\n  f=root/skill/rel\n  assert hashlib.sha256(f.read_bytes()).hexdigest()==digest,(skill,rel)\nprint('hashes matched')\n'''.replace('ROOT',repr(root(v,n))).replace('EXPECTED',repr(expected))
  ssh(v,prefix(v,n),code)
  if v==1:cmd=f'docker exec {n} openclaw skills list --json --agent main'
  elif v==2:cmd=f'env HOME=/root OPENCLAW_STATE_DIR=/root/.openclaw-{n} OPENCLAW_CONFIG_PATH=/root/.openclaw-{n}/openclaw.json /opt/openclaw-{n}/node_modules/.bin/openclaw skills list --json --agent main'
  elif v==4:cmd='runuser -u openclaw -- /home/openclaw/.npm-global/bin/openclaw skills list --json --agent main'
  else:cmd=None
  if cmd:
   raw=ssh(v,cmd);result=json.loads(raw[raw.index('{'):]);found={x['name']:x for x in result['skills']}; selected={s:{k:found[s].get(k) for k in ['name','eligible','modelVisible','source']} for s in names(n)}
   for s,r in selected.items():assert r['eligible'] and r['modelVisible'] and r['source']=='openclaw-workspace',(n,s,r)
  else:
   code="import sys,json;sys.path.insert(0,'/opt/hermes');from tools.skills_tool import skills_list,SKILLS_DIR;assert str(SKILLS_DIR)=='/opt/data/skills';r=json.loads(skills_list());print(json.dumps(r))"
   raw=ssh(v,'docker exec -i hermes-ruby /opt/hermes/.venv/bin/python3 -',code);result=json.loads(raw);found={x['name']:x for x in result['skills']};selected={s:found[s] for s in names(n)}
  (B/f'{n}-verified.json').write_text(json.dumps(selected,indent=2),encoding='utf-8')
  return {'agent':n,'skills':list(selected),'hashes':'matched','discovery':'passed'}
 with ThreadPoolExecutor(max_workers=4) as ex:
  for r in ex.map(verify,TARGETS):print(json.dumps(r),flush=True)
