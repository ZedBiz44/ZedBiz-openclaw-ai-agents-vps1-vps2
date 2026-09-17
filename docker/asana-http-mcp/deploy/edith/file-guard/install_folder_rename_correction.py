"""Install only the scoped correction hook in the existing shared executor."""
from pathlib import Path
import py_compile
p=Path('/home/node/.openclaw/private/folder-cleanup/albertawide/work.py')
old="def gog(*args):\n return guarded_run(P, ROOT, args, lambda: _gog(*args), check_file_plan)"
new="def gog(*args):\n if args and args[0]=='rename':\n  from folder_rename_correction import rename\n  return rename(P, ROOT, args, _gog)\n return guarded_run(P, ROOT, args, lambda: _gog(*args), check_file_plan)"
s=p.read_text()
if new in s:print('Already installed')
else:
 assert s.count(old)==1,'Unexpected wrapper; stop before changing'
 backup=p.with_name('work.py.before-approved-rename-20260917')
 if not backup.exists():backup.write_text(s)
 p.write_text(s.replace(old,new))
py_compile.compile(str(p),doraise=True)
