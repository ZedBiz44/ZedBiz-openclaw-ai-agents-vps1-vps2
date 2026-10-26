import pathlib,json,hashlib,sys,shutil,os,subprocess
base=pathlib.Path('/maintenance');root=pathlib.Path('/agents');names=sys.argv[1:];allowed={'amanda','edith','gohzed','grogar','inga','maggie','marsha','terry','victor','vivian','wilma'};assert set(names)<=allowed
rows=[x for x in json.loads((base/'skill-updates/plan.json').read_text()) if x['agent'] in names]
for x in rows:
 p=root/x['path'];assert p.resolve().is_relative_to(root/x['agent']/'workspace/skills')
 old=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
 assert old==x['before'],'Live file changed: '+x['path']
 assert hashlib.sha256((base/'skill-updates'/x['path']).read_bytes()).hexdigest()==x['after']
for x in rows:
 p=root/x['path'];s=base/'skill-updates'/x['path'];backup=base/'skill-files-before'/x['path'];backup.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():shutil.copy2(p,backup)
 p.parent.mkdir(parents=True,exist_ok=True);sdata=s.read_bytes();p.write_bytes(sdata);os.chown(p,1000,1000)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==x['after']
for agent,skill in sorted({(x['agent'],x['skill']) for x in rows}):
 p=subprocess.run(['python3','/app/skills/skill-creator/scripts/quick_validate.py',str(root/agent/'workspace/skills'/skill)],capture_output=True,text=True)
 assert p.returncode==0,agent+'/'+skill+': '+p.stdout+p.stderr
r={'agents':names,'files':len(rows),'hashesVerified':True,'nativeValidation':True};(base/('skills-deployed-'+','.join(names)+'.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r))
