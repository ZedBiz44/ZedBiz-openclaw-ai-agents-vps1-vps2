from pathlib import Path
import shutil, subprocess, os, json, hashlib, re, tarfile

b=Path(__file__).parent
py=Path('C:/Users/zener/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
validator=Path('D:/Google Drive/Documents/Codex-Projects/.codex/skills/z-ai-skill-developer/scripts/validate_skill.py')
native=Path('D:/Google Drive/Documents/Codex-Projects/.codex/skills/.system/skill-creator/scripts/quick_validate.py')
env={**os.environ,'PYTHONPATH':str(b/'.validation-deps'),'PYTHONUTF8':'1'}
names=['z-asana-procedures','z-advanced-asana-control','z-asana-agent-control','z-agent-communication']
manifest={}
for name in names:
 repo=b/(name+'-Skill'); src=repo/name if name=='z-asana-procedures' else repo
 package=repo/'dist'/name
 package.mkdir(parents=True,exist_ok=True)
 resources=[d for d in ('agents','references','assets') if (src/d).is_dir()]
 (repo/'package-resources.txt').write_text('\n'.join(resources)+'\n',encoding='utf-8')
 shutil.copy2(src/'SKILL.md',package/'SKILL.md')
 for d in resources: shutil.copytree(src/d,package/d,dirs_exist_ok=True)
 # Match Git's canonical LF content across Windows authoring and Linux runtimes.
 for f in package.rglob('*'):
  if f.is_file(): f.write_bytes(f.read_bytes().replace(b'\r\n',b'\n'))
 if src==repo: subprocess.run([str(py),str(validator),'--repository',str(repo)],check=True,env=env)
 subprocess.run([str(py),str(validator),'--platform','openclaw',str(package)],check=True,env=env)
 subprocess.run([str(py),str(native),str(package)],check=True,env=env)
 for f in package.rglob('*.md'):
  for link in re.findall(r'\]\(([^)]+)\)',f.read_text(encoding='utf-8')):
   if '://' in link or link.startswith('#'):continue
   assert (f.parent/link.split('#')[0]).exists(), (f,link)
 manifest[name]={str(f.relative_to(package)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(package.rglob('*')) if f.is_file()}
 subprocess.run(['git','-C',str(repo),'diff','--check'],check=True)
(b/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
with tarfile.open(b/'skills-20260924.tar.gz','w:gz') as tar:
 for name in names:tar.add(b/(name+'-Skill')/'dist'/name,arcname=name)
 tar.add(b/'manifest.json',arcname='manifest.json')
print('Validated and packaged',len(names),'skills;',sum(len(x) for x in manifest.values()),'runtime files')
