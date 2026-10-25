"""Wait for the accepted serial upgrade wave, then prove one encrypted backup before applying it to the fleet."""
import pathlib,json,subprocess,time,os,hashlib
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/private-recovery-20261024');S=P('/home/jackadmin/vps1-10-6-20261023');F=P('/opt/openclaw/backups/fleet-10-6-20261024');start=time.monotonic()
while not (F/'wave-complete.json').exists():
 assert time.monotonic()-start<3*3600,'Upgrade wave has not completed; inspect before backups'
 active=subprocess.check_output(['docker','ps','--filter','label=cody.fleet-wave-r6=true','-q'],text=True).strip();assert active,'Upgrade wave stopped before acceptance; investigate first'
 time.sleep(25)
assert json.loads((F/'wave-complete.json').read_text())['completed']
expected=json.loads((S/'backup-scripts-sha256.json').read_text())
for name,digest in expected.items():
 with (S/name).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==digest,'Backup script source changed'
for agent in ['terry','marsha','amanda','victor','wilma','gohzed','grogar','inga','maggie','edith','vivian']:
 A=W/('agent-'+agent)
 if not (A/'offsite.json').exists():
  print(json.dumps({'currentBackupAgent':agent,'phase':'consistent-encrypted-backup'}),flush=True)
  assert subprocess.run(['/usr/bin/python3',str(S/'backup-current-vps1-agent.py'),agent]).returncode==0,'Backup failed for '+agent
 proof=json.loads((A/'offsite.json').read_text());assert proof['passed'] and proof['cloudMd5AndSizeVerified'] and proof['selectedRestoreVerified']
 if not (A/'old-data-cleanup.json').exists():
  assert subprocess.run(['/usr/bin/python3',str(S/'cleanup-replaced-vps1-agent-backups.py'),agent]).returncode==0,'Old backup cleanup needs review for '+agent
 print(json.dumps({'currentBackupAgent':agent,'acceptedOffsite':True}),flush=True)
if not (W/'shared-recovery/offsite.json').exists():
 assert subprocess.run(['/usr/bin/python3',str(S/'backup-vps1-shared-recovery.py')]).returncode==0,'Shared recovery backup failed'
shared=json.loads((W/'shared-recovery/offsite.json').read_text());assert shared['passed'] and shared['cloudMd5AndSizeVerified']
proof={'passed':True,'agents':11,'sharedMemoryAndRecoveryVerified':True,'currentAgentStatesOffsite':True,'oldOctober18AgentDataReplaced':True,'marshaSlackPreserved':json.loads(P('/opt/openclaw/agents/marsha/config/openclaw.json').read_text())['plugins']['entries']['slack']['enabled'] is True}
(W/'current-backups-complete.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
