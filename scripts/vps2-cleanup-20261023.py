import json, hashlib, os, shutil, subprocess, sys
from pathlib import Path
B=Path('/root/cody-vps2-20261023');E=Path('/root/cody-vps2-followup-20261023');os.umask(0o077)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
checks=[]
for n in ['frank','harry','suzy']:
 p=B/n/'before.tar';expected=json.loads((B/n/'baseline.json').read_text())['archiveSha256']
 assert sha(p)==expected,'Archive mismatch';checks.append(str(p))
p=B/'frank/activation-before.tar';assert sha(p)==json.loads((B/'frank/activation-checkpoint.json').read_text())['sha256'];checks.append(str(p))
phase=sys.argv[1]
targets=([B/'core-candidate']+[B/n/k for n in ['frank','harry','suzy'] for k in ['candidate','rehearsal-state','old-node_modules']]) if phase=='temporary' else ([B/'frank/activation-original']+[B/n/'extracted' for n in ['frank','harry','suzy']])
assert phase in ['temporary','extracted']
for t in targets:
 assert t.is_dir() and not t.is_symlink() and t.resolve().is_relative_to(B.resolve())
for proc in Path('/proc').glob('[0-9]*'):
 for link in [proc/'cwd',proc/'exe',*list((proc/'fd').glob('*'))]:
  try:v=os.readlink(link)
  except OSError:continue
  assert not any(v==str(t) or v.startswith(str(t)+'/') for t in targets),'Live reference '+str(link)
for n in ['frank','harry','suzy']:
 for root in [Path('/root/.openclaw-'+n),Path('/opt/openclaw-'+n)]:
  for p in root.rglob('*'):
   if p.is_symlink():
    v=p.resolve();assert not any(v==t or v.is_relative_to(t) for t in targets),'Live symlink '+str(p)
sizes={str(t):int(subprocess.check_output(['du','-sxB1',str(t)],text=True).split()[0]) for t in targets}
for t in targets:shutil.rmtree(t)
result={'phase':phase,'verifiedArchives':checks,'removed':sizes,'reclaimedGiB':sum(sizes.values())/2**30}
(E/('cleanup-'+phase+'.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result))
