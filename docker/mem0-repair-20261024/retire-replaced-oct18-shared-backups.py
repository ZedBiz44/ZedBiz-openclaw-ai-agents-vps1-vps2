"""Retire explicit old data leaves after complete current offsite replacement; preserve small audit records and all recovery controls."""
import pathlib,json,subprocess,shutil,os,re,datetime
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/private-recovery-20261024');assert json.loads((W/'current-backups-complete.json').read_text())['passed'];shared=json.loads((W/'shared-recovery/offsite.json').read_text());assert shared['passed'] and shared['cloudMd5AndSizeVerified'] and shared['managementDatabasesRestoreVerified']
parents=[P('/opt/openclaw/backups/fleet-20261018'),P('/opt/openclaw/backups/components-20261018')];targets=[parents[0]/'shared-memory',*[parents[1]/n for n in ['shared-tools','shared','host','asana','shared-services']]];audit=W/'retired-oct18-audit';audit.mkdir(mode=0o700,exist_ok=True);ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();containers=json.loads(subprocess.check_output(['docker','inspect',*ids]));controls=[]
for root in [P('/etc/systemd/system'),P('/opt/openclaw/recovery')]:
 for p in root.rglob('*'):
  if p.is_file() and not p.is_symlink() and p.suffix in ['.py','.sh','.json','.service'] and p.stat().st_size<2*1024**2:controls.append((str(p),p.read_text(errors='replace')))
def noUsers(target):
 for d in containers:
  for mount in d['Mounts']:
   src=P(mount['Source']);assert src!=target and target not in src.parents,'Old backup is mounted'
 for p in P('/proc').glob('[0-9]*/fd/*'):
  try:link=os.readlink(p)
  except OSError:continue
  assert not (link==str(target) or link.startswith(str(target)+'/')),'Old backup is open by a process'
before=shutil.disk_usage(W).free;removed=[];copied=0
for target in targets:
 if not target.exists():continue
 assert target.resolve()==target and not target.is_symlink() and target.parent in parents;noUsers(target);refs=[name for name,text in controls if str(target) in text];assert not refs,'Recovery control references old data: '+str(refs)
 for p in target.rglob('*'):
  if p.is_file() and not p.is_symlink() and p.stat().st_size<1024**2 and any(word in p.name.lower() for word in ['accepted','acceptance','activation','failure','validation','apt-','packages-before','orchestrat']):
   dest=audit/p.relative_to(P('/opt/openclaw/backups'));dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);copied+=1
 shutil.rmtree(target);assert not target.exists();removed.append(str(target))
for parent in parents:
 if not parent.exists():continue
 assert parent.resolve()==parent and not parent.is_symlink();remainingDirs=[p for p in parent.iterdir() if p.is_dir()];assert not remainingDirs,'Unexpected old data remains; inspect before removing parent'
 for p in list(parent.iterdir()):
  assert p.is_file() and not p.is_symlink() and p.stat().st_size<5*1024**2,'Unexpected old root file';dest=audit/parent.name/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);p.unlink();copied+=1
 parent.rmdir();removed.append(str(parent))
pg=P('/opt/openclaw/services/hindsight/backups/postgres');oldPg=[]
for p in pg.iterdir():
 match=re.fullmatch(r'hindsight-(\d{8})T\d{6}Z\.dump\.enc(?:\.sha256)?',p.name)
 if match and match[1]<='20261018':
  assert p.resolve()==p and not p.is_symlink();noUsers(p);size=p.stat().st_size;p.unlink();oldPg.append({'name':p.name,'bytes':size})
proof={'passed':True,'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'removedOldDataPaths':removed,'smallAuditFilesPreserved':copied,'oldPostgresFilesRemoved':oldPg,'freeBytesRecovered':shutil.disk_usage(W).free-before,'currentOffsiteSharedBackupId':shared['fileId'],'activeRecoveryControlDirectoriesPreserved':True,'currentPostgresBackupScheduleUnchanged':True};(W/'oct18-shared-data-cleanup.json').write_text(json.dumps(proof,indent=2));print(json.dumps({k:v for k,v in proof.items() if k!='oldPostgresFilesRemoved'}),flush=True)
