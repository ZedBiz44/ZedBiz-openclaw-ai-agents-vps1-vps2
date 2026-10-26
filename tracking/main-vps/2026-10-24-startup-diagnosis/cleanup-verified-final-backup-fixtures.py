"""Remove only restored test copies and packaged staging after offsite verification."""
import pathlib,json,subprocess,shutil,os,datetime,hashlib
P=pathlib.Path;W=P('/opt/openclaw/backups/private-recovery-20261024');os.umask(0o077)
for name in ['current-backups-complete.json','backup-index-published.json','shared-recovery/offsite.json']:
 assert json.loads((W/name).read_text())['passed']
h=json.loads((W/'hindsight-final-proof/proof.json').read_text());q=json.loads((W/'qdrant-final-proof/proof.json').read_text());assert h['passed'] and q['passed']
for file,digest in [(W/'hindsight-final-proof/before.dump',h['dumpSha256']),(W/'qdrant-final-proof/storage.snapshot',q['snapshotSha256'])]:
 with file.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==digest
ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();containers=json.loads(subprocess.check_output(['docker','inspect',*ids]));before=shutil.disk_usage(W).free;removed=[]
for rel in ['hindsight-final-proof/data','qdrant-final-proof/restore-data','shared-recovery/inputs']:
 target=W/rel
 if not target.exists():continue
 assert target.resolve()==target and W in target.parents and not target.is_symlink()
 for d in containers:
  for m in d['Mounts']:
   source=P(m['Source']);assert source!=target and target not in source.parents,'Test copy remains mounted'
 for fd in P('/proc').glob('[0-9]*/fd/*'):
  try:link=os.readlink(fd)
  except OSError:continue
  assert not (link==str(target) or link.startswith(str(target)+'/')),'Test copy remains open'
 shutil.rmtree(target);assert not target.exists();removed.append(str(target))
proof={'passed':True,'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'removedVerifiedTemporaryCopies':removed,'freeBytesRecovered':shutil.disk_usage(W).free-before,'sourceSnapshotsAndRestoreProofsRetained':True}
(W/'final-fixture-cleanup.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
