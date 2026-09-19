from pathlib import Path
import shutil
base=Path('/home/node/.openclaw')
def replace(path,old,new):
 s=path.read_text();assert old in s,str(path)
 backup=path.with_name(path.name+'.before-container-archive-20260918')
 assert not backup.exists(),'Inspect the prior installation before repeating'
 shutil.copy2(path,backup);path.write_text(s.replace(old,new,1));compile(path.read_text(),str(path),'exec')
replace(base/'workspace/scripts/execution_guard.py',"    elif action == 'move':\n        fid = args[1]\n        proof =", "    elif action == 'move':\n        fid = args[1]\n        if originals.get(fid, {}).get('mimeType') == 'application/vnd.google-apps.folder':\n            from original_folder_archive import validate_plan\n            validate_plan(plan, before, review, state, root, args, protected)\n            return digest(plan_path)\n        proof =")
replace(base/'private/folder-cleanup/albertawide/work.py'," return guarded_run(P, ROOT, args, lambda: _gog(*args), check_file_plan)"," if args and args[0]=='move':\n  original=json.loads((P/'initial-inventory.json').read_text())\n  if any(x['id']==args[1] and x.get('mimeType')=='application/vnd.google-apps.folder' for x in original['items']):\n   from original_folder_archive import execute as archive_container\n   return guarded_run(P, ROOT, args, lambda: archive_container(P, ROOT, args, _gog), check_file_plan)\n return guarded_run(P, ROOT, args, lambda: _gog(*args), check_file_plan)")
print('Installed saved-plan gate for original empty-container archiving.')

