import os,json,subprocess,shutil,hashlib
from pathlib import Path
B=Path('/root/cody-vps2-followup-20261023');os.umask(0o077)
targets=[B/'tools-candidate',B/'asana-candidate',B/'asana-old-node_modules',B/'asana-old-dist']
for n in ['frank','suzy']:
 assert json.loads((B/(n+'-accepted.json')).read_text())['accepted']
 w=B/('hindsight-'+n)
 with (w/'before.tar').open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==json.loads((w/'baseline.json').read_text())['archiveSha256']
 targets.extend([w/'state',w/'program'])
for t in targets:assert t.is_dir() and not t.is_symlink() and t.resolve().is_relative_to(B)
for proc in Path('/proc').glob('[0-9]*'):
 for link in [proc/'cwd',proc/'exe',*list((proc/'fd').glob('*'))]:
  try:v=os.readlink(link)
  except OSError:continue
  assert not any(v==str(t) or v.startswith(str(t)+'/') for t in targets),'Active reference '+str(link)
for n in ['frank','harry','suzy']:
 for base in [Path('/root/.openclaw-'+n),Path('/opt/openclaw-'+n)]:
  for p in base.rglob('*'):
   if p.is_symlink():assert not any(p.resolve().is_relative_to(t) for t in targets),'Live link '+str(p)
sizes={str(t):int(subprocess.check_output(['du','-sxB1',str(t)],text=True).split()[0]) for t in targets}
for t in targets:shutil.rmtree(t)
subprocess.run(['npm','cache','clean','--force'],check=True)
subprocess.run(['apt-get','clean'],check=True)
r={'removed':sizes,'temporaryGiB':sum(sizes.values())/2**30,'cachesCleaned':['npm','apt']};(B/'cleanup-followup.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
