"""Remove only an agent's old October 18 data leaves after verified post-update offsite recovery."""
import pathlib,json,subprocess,shutil,os,sys
P=pathlib.Path;os.umask(0o077);agent=sys.argv[1];assert agent in ['terry','marsha','amanda','victor','wilma','gohzed','grogar','inga','maggie','edith','vivian']
W=P('/opt/openclaw/backups/private-recovery-20261024');proof=json.loads((W/('agent-'+agent)/'offsite.json').read_text())
assert json.loads(P('/opt/openclaw/backups/fleet-10-6-20261024/wave-complete.json').read_text())['completed'],'Finish agent updates before removing October 18 data'
assert proof['passed'] and proof['cloudMd5AndSizeVerified'] and proof['selectedRestoreVerified'] and proof['decryptionRoundtripVerified'] and proof['postBackupHealthy']
assert json.loads((W/'offsite-images.json').read_text())['passed']
targets=[P('/opt/openclaw/backups')/folder/agent for folder in ['fleet-20261018','components-20261018']]
ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();containers=json.loads(subprocess.check_output(['docker','inspect',*ids]))
controls=[]
for root in [P('/etc/systemd/system'),P('/opt/openclaw/recovery')]:
 for p in root.rglob('*'):
  if p.is_file() and not p.is_symlink() and p.suffix in ['.json','.sh','.py','.service'] and p.stat().st_size<2*1024**2:
   controls.append((str(p),p.read_text(errors='replace')))
before=shutil.disk_usage(W).free;removed=[];inventory=[]
for target in targets:
 if not target.exists():continue
 assert target.resolve()==target and not target.is_symlink() and target.parent.name in ['fleet-20261018','components-20261018'] and target.name==agent
 for d in containers:
  for mount in d['Mounts']:
   source=P(mount['Source']);assert source!=target and target not in source.parents,'Old data is mounted'
 refs=[name for name,text in controls if str(target) in text];assert not refs,'Recovery control still references old data: '+str(refs)
 inventory.extend({'path':str(p),'bytes':p.stat().st_size} for p in target.rglob('*') if p.is_file() and not p.is_symlink())
 shutil.rmtree(target);assert not target.exists();removed.append(str(target))
receipt={'passed':True,'agent':agent,'removed':removed,'freedBytes':shutil.disk_usage(W).free-before,'replacementDriveFileId':proof['fileId'],'oldDataFileInventory':inventory,'activeRecoveryControlsPreserved':True}
(W/('agent-'+agent)/'old-data-cleanup.json').write_text(json.dumps(receipt,indent=2));print(json.dumps({k:v for k,v in receipt.items() if k!='oldDataFileInventory'}),flush=True)
