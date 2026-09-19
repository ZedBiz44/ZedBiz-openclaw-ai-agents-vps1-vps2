"""Reproduce the scoped correction routing change; preserve all other guards."""
from pathlib import Path
import shutil

p=Path('/home/node/.openclaw/private/folder-cleanup/albertawide/work.py')
old='def gog(*args):\n'
new=(old+' from reviewed_folder_corrections import supports, apply as apply_correction\n'
     ' if supports(ROOT,tuple(args)):\n'
     '  return apply_correction(P, ROOT, args, _gog)\n')
s=p.read_text()
if new in s:
    print('Exact correction routing already installed')
else:
    assert s.count(old)==1
    backup=p.with_name(p.name+'.before-reviewed-correction-route')
    assert not backup.exists(),'Review prior installation before repeating'
    patched=s.replace(old,new,1);compile(patched,str(p),'exec')
    shutil.copy2(p,backup);p.write_text(patched)
    print('Installed exact reviewed correction routing')

