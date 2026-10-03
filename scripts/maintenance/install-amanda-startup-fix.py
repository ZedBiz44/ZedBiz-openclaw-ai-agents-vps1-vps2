import pathlib,shutil,json
b=pathlib.Path('/home/node/.openclaw/workspace')
p=b/'post-start.sh';s=p.read_text()
old='python3 /home/node/.openclaw/workspace/runtime-repair-20260927/apply.py || exit $?'
new='python3 /home/node/.openclaw/workspace/runtime-repair-20260927/preserve-amanda-runtime-9-8.py || exit $?'
assert s.count(old)==1
shutil.copy2(p,b/'post-start.sh.before-9.8-runtime-repair')
shutil.copyfile('/maintenance/preserve-amanda-runtime-9-8.py',b/'runtime-repair-20260927/preserve-amanda-runtime-9-8.py')
p.write_text(s.replace(old,new))
c=json.loads(pathlib.Path('/home/node/.openclaw/openclaw.json').read_text())
print('Updated Amanda startup repair; configured agent timeout:',c['agents']['defaults'].get('timeoutSeconds'))
