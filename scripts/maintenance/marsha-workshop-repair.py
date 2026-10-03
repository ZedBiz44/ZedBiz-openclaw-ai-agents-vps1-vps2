from pathlib import Path
import subprocess,os
p=Path('/app/dist/skill-collection-review-monitor-D4d1nVZB.mjs')
s=p.read_text();old='message: SKILL_WORKSHOP_MAINTENANCE_PROMPT,';new=old+'\n\t\t\t\tmodel: "openrouter/google/gemini-3.1-flash-lite", // Existing compatible Workshop runtime.'
if new not in s:
 assert s.count(old)==1,'Unsupported runtime source'
 b=Path('/home/node/.openclaw/workspace/workshop-runtime-repair-20260927/module.before.mjs')
 if not b.exists():b.write_text(s)
 t=p.with_suffix('.repair.mjs');t.write_text(s.replace(old,new));subprocess.run(['node','--check',str(t)],check=True);os.chmod(t,p.stat().st_mode);os.replace(t,p)
