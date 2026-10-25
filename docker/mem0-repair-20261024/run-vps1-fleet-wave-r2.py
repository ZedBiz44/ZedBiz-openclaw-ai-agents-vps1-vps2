"""Serial authorized fleet wave; each acceptance gates the next production change."""
import pathlib,json,subprocess,hashlib,shutil,os,time
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/fleet-10-6-20261024');S=W/'scripts';activation=S/'activate-vps1-cohort-r4.py';acceptance=S/'accept-live-vps1-cohort.py'
def sha(p):
 with P(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(activation)=='21b80977f654d141dffac651587d21429cd91b1aefc52c4ec0c510115253850b'
assert sha(acceptance)=='b4591c1217ef14d15d2994e3e9d1cbd92de7ab02a139ada9d508c30949eb4c9f'
prior=W/'edith';attempt=W/'edith-attempt1';assert prior.resolve()==prior and attempt.resolve()==attempt and not attempt.exists()
assert json.loads((prior/'rejected-copy-cleanup.json').read_text())['originalStateRestored']
assert not (prior/'activation.json').exists() and (prior/'failure.json').exists()
healthStart=time.monotonic()
while True:
 d=json.loads(subprocess.check_output(['docker','inspect','edith']))[0];assert d['State']['Running'] and not d['State']['OOMKilled'] and d['RestartCount']==0 and '2026.10.4' in d['Config']['Image']
 if d['State']['Health']['Status']=='healthy':break
 assert time.monotonic()-healthStart<900,'Restored original did not become healthy';time.sleep(10)
assert subprocess.check_output(['systemctl','show','openclaw-edith.service','--property=SubState','--value'],text=True).strip()=='exited'
prior.rename(attempt)
def clearRestoreCopies(agent):
 A=W/agent;assert json.loads((A/'acceptance.json').read_text())['passed'];checkpoint=json.loads((A/'checkpoint.json').read_text());assert sha(A/'state-before.tar.gz')==checkpoint['sha256']
 targets=[A/'restore-check',A/'lancedb-restore-check']
 if agent=='edith':targets+=[attempt/'restore-check',attempt/'state-before.tar.gz']
 ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();containers=json.loads(subprocess.check_output(['docker','inspect',*ids])) if ids else []
 before=shutil.disk_usage(W).free;removed=[]
 for target in targets:
  if not target.exists():continue
  assert target.resolve()==target and not target.is_symlink() and W in target.parents
  for d in containers:
   for m in d.get('Mounts',[]):
    source=P(m['Source']);assert source!=target and target not in source.parents
  if target.is_dir():shutil.rmtree(target)
  else:target.unlink()
  removed.append(str(target))
 (A/'accepted-working-copy-cleanup.json').write_text(json.dumps({'removed':removed,'diskBytesFreed':shutil.disk_usage(W).free-before,'verifiedCurrentArchiveRetained':True}))
for agent in ['edith','vivian','amanda','victor','wilma','gohzed','grogar','inga','maggie','terry']:
 print(json.dumps({'waveAgent':agent,'phase':'activation'}),flush=True)
 r=subprocess.run(['/usr/bin/python3',str(activation),agent]);assert r.returncode==0,'Activation stopped at '+agent
 print(json.dumps({'waveAgent':agent,'phase':'live-acceptance'}),flush=True)
 r=subprocess.run(['/usr/bin/python3',str(acceptance),agent]);assert r.returncode==0,'Acceptance stopped at '+agent
 clearRestoreCopies(agent);print(json.dumps({'waveAgent':agent,'accepted':True}),flush=True)
(W/'wave-complete.json').write_text(json.dumps({'completed':True,'agents':['edith','vivian','amanda','victor','wilma','gohzed','grogar','inga','maggie','terry'],'marshaPreviouslyAccepted':True,'marshaSlackPreserved':True}));print('Authorized VPS1 agent wave complete.',flush=True)

