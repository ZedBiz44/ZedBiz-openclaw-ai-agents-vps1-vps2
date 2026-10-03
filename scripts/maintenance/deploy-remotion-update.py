import pathlib,json,hashlib,shutil,os,subprocess
b=pathlib.Path('/maintenance');s=b/'remotion-update';root=pathlib.Path('/skills');plan=json.loads((s/'plan.json').read_text())
for x in plan:
 p=root/x['path'];assert p.resolve().is_relative_to(root);assert (hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None)==x['before'],x['path']
 assert hashlib.sha256((s/x['path']).read_bytes()).hexdigest()==x['after']
for x in plan:
 p=root/x['path'];backup=b/'remotion-files-before'/x['path'];backup.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():shutil.copy2(p,backup)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((s/x['path']).read_bytes());os.chown(p,1000,1000)
for folder in s.iterdir():
 if not folder.is_dir():continue
 for validator in ['/app/skills/skill-creator/scripts/quick_validate.py','/maintenance/validate_skill.py']:
  r=subprocess.run(['python3',validator,str(root/folder.name)],capture_output=True,text=True);assert r.returncode==0,folder.name+': '+r.stdout+r.stderr
r={'agent':'vivian','version':'4.0.532','upstreamCommit':'e385a83dbde54179c0457ad90b7d7c3a4b6ab44a','files':len(plan),'validated':True};(b/'remotion-deployment.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
