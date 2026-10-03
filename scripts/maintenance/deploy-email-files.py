import pathlib,shutil,os,sys,hashlib
n=sys.argv[1];root=pathlib.Path('/agent');b=pathlib.Path('/maintenance');backup=root/'backups/email-migration-20261003';backup.mkdir(parents=True,exist_ok=True)
skill=root/'skills/himalaya';old=backup/'himalaya-v1'
assert not old.exists(),'Skill backup already exists'
if skill.exists():skill.rename(old)
skill.mkdir(parents=True);shutil.copyfile(b/'himalaya/SKILL.md',skill/'SKILL.md')
cfg=root/'.config/himalaya';cfg.mkdir(parents=True,exist_ok=True)
shutil.copyfile(b/n/'config-v2.toml',cfg/'config.toml');os.chmod(cfg/'config.toml',0o600)
for p in [backup,skill,skill/'SKILL.md',cfg,cfg/'config.toml']:os.chown(p,1000,1000)
print('Installed version-2 configuration and skill for '+n)
