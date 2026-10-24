import pathlib,json,os
root=pathlib.Path('/agents');out=[]
for name in ['amanda','edith','gohzed','grogar','inga','maggie','marsha','terry','victor','vivian','wilma']:
 workspace=root/name/'workspace';p=workspace/'skills/z-record-knowledge.before-20260916-auto-memory'
 if not p.exists():continue
 assert not p.is_symlink() and p.resolve().is_relative_to(workspace/'skills')
 dest=workspace/'backups/skill-maintenance-20261003'/p.name;assert not dest.exists()
 dest.parent.mkdir(parents=True,exist_ok=True);os.chown(dest.parent,1000,1000);p.rename(dest)
 assert (dest/'SKILL.md').exists() and not p.exists();out.append(name)
pathlib.Path('/maintenance/retired-backup-skill-copies.json').write_text(json.dumps({'agents':out,'action':'Moved dated backup skill copies outside active skill discovery; no contents deleted'},indent=2));print(json.dumps(out))
