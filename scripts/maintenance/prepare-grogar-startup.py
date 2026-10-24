from pathlib import Path
import shutil
p=Path('/home/node/.openclaw/workspace/workshop-runtime-repair-20260927/apply.py')
s=p.read_text();old='skill-collection-review-monitor-vmq0YSXR.mjs';new='skill-collection-review-monitor-D4d1nVZB.mjs'
assert s.count(old)==1
source=(Path('/app/dist')/new).read_text()
assert source.count('message: SKILL_WORKSHOP_MAINTENANCE_PROMPT,')==1
shutil.copy2(p,p.with_name('apply.py.before-9.8'))
p.write_text(s.replace(old,new))
print('Grogar Workshop repair adapted to verified 9.8 module; existing model choice retained')
