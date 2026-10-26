"""Continue the authorized wave using corrected directory handling and actual memory-result validation."""
import pathlib,json,subprocess,hashlib,shutil,os
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/fleet-10-6-20261024');S=W/'scripts'
expected={'activate-vps1-cohort-r5.py':'0cadc260b2d1028e1242df8decaa891ae3a09e04ec68e83a996d952b1e5bbd4c','accept-live-vps1-cohort.py':'b4591c1217ef14d15d2994e3e9d1cbd92de7ab02a139ada9d508c30949eb4c9f','verify-live-memory-result.py':'d4c255721147324be576b5c9fa930e970a6d7c8f2c21ac07d8b7a3bef53ad756'}
def sha(p):
 with P(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for name,digest in expected.items():assert sha(S/name)==digest
assert not subprocess.check_output(['docker','ps','--filter','label=cody.fleet-wave=true','-q'],text=True).strip(),'Original maintenance wave still active'
for agent in ['edith','vivian']:
 proof=json.loads((W/agent/'acceptance.json').read_text());assert proof['passed'] and proof['actualMemoryResultValidated'] and proof['storedScheduleDefinitionsCompared']
marsha=json.loads(P('/opt/openclaw/agents/marsha/config/openclaw.json').read_text());assert marsha['channels']['slack']['enabled'] is True
def clearRestoreCopies(agent):
 A=W/agent;proof=json.loads((A/'acceptance.json').read_text());assert proof['passed'] and proof['actualMemoryResultValidated'];checkpoint=json.loads((A/'checkpoint.json').read_text());assert sha(A/'state-before.tar.gz')==checkpoint['sha256']
 targets=[A/'restore-check',A/'lancedb-restore-check']
 if agent=='vivian':targets.append(A/'restored-original-unused')
 ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();containers=json.loads(subprocess.check_output(['docker','inspect',*ids])) if ids else [];before=shutil.disk_usage(W).free;removed=[]
 for target in targets:
  if not target.exists():continue
  assert target.resolve()==target and not target.is_symlink() and W in target.parents
  for d in containers:
   for m in d.get('Mounts',[]):
    src=P(m['Source']);assert src!=target and target not in src.parents
  shutil.rmtree(target);assert not target.exists();removed.append(str(target))
 (A/'accepted-working-copy-cleanup.json').write_text(json.dumps({'removed':removed,'diskBytesFreed':shutil.disk_usage(W).free-before,'currentVerifiedArchiveRetained':True}))
 if agent=='vivian' and (A/'failure.json').exists():
  assert not (A/'repaired-preactivation-failure.json').exists();(A/'failure.json').rename(A/'repaired-preactivation-failure.json')
for agent in ['edith','vivian']:clearRestoreCopies(agent)
for agent in ['amanda','victor','wilma','gohzed','grogar','inga','maggie','terry']:
 A=W/agent
 if (A/'acceptance.json').exists():
  proof=json.loads((A/'acceptance.json').read_text());assert proof['passed'] and proof.get('actualMemoryResultValidated');continue
 assert not A.exists(),'Inspect existing unfinished checkpoint before retry'
 for script,phase in [('activate-vps1-cohort-r5.py','activation'),('accept-live-vps1-cohort.py','live-acceptance'),('verify-live-memory-result.py','memory-result-and-schedules')]:
  print(json.dumps({'waveAgent':agent,'phase':phase}),flush=True);r=subprocess.run(['/usr/bin/python3',str(S/script),agent]);assert r.returncode==0,phase+' stopped at '+agent
 clearRestoreCopies(agent);print(json.dumps({'waveAgent':agent,'accepted':True}),flush=True)
(W/'wave-complete.json').write_text(json.dumps({'completed':True,'agents':['edith','vivian','amanda','victor','wilma','gohzed','grogar','inga','maggie','terry'],'marshaPreviouslyAccepted':True,'marshaSlackPreserved':True,'actualMemoryResultsValidated':True}));print('Authorized VPS1 agent wave complete.',flush=True)

