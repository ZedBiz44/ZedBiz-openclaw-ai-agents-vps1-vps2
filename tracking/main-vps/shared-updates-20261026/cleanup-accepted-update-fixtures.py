"""After cloud publication, remove only owned fixtures, upload copies and transient key material."""
import pathlib,subprocess,json,hashlib,os,sys,shutil,datetime
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/shared-updates-20261026');A=W/'offsite';off=json.loads((A/'offsite.json').read_text());assert off['passed'] and off['cloudMd5AndSizeVerified'];assert json.loads((A/'index-published.json').read_text())['passed'];alignment=json.loads((W/'recovery-alignment.json').read_text());assert alignment['passed'];key=json.loads((A/'key-reference.json').read_text());token=sys.stdin.read().strip();assert token.startswith('ops_');env=os.environ.copy();env['OP_SERVICE_ACCOUNT_TOKEN']=token;p=subprocess.run(['op','read','op://z-backups/'+key['itemId']+'/password'],env=env,capture_output=True,text=True,timeout=90);assert p.returncode==0;identity=A/'age-identity.txt';assert p.stdout.strip()==identity.read_text().strip() and p.stdout.strip().startswith('AGE-SECRET-KEY-1');assert subprocess.check_output(['age-keygen','-y',str(identity)],text=True).strip()==key['publicRecipient']
source=A/'inputs/current-images/images.tar.gz';durable=P(alignment['newArchive']);assert source.stat().st_ino==durable.stat().st_ino and source.stat().st_dev==durable.stat().st_dev and source.stat().st_size==durable.stat().st_size;before=shutil.disk_usage(W).free;stopped=[];receipts=A/'receipts';receipts.mkdir(exist_ok=True)
for rel in ['current-images/catalog.json','current-images/cold-restore-proof.json','databases/hindsight-restore-proof.json','databases/qdrant-snapshot-metadata.json']:
 target=receipts/P(rel).name;shutil.copy2(A/'inputs'/rel,target)
shutil.copy2(receipts/'cold-restore-proof.json',durable.parent/'cold-restore-proof.json')
for name in ['cody-shared-marsha-20261026','cody-shared-20261026-api','cody-shared-20261026-db','cody-qdrant-120-20261026']:
 p=subprocess.run(['docker','inspect',name],capture_output=True,text=True)
 if p.returncode:continue
 d=json.loads(p.stdout)[0];assert d['Config'].get('Labels',{}).get('cody.shared-update-fixture')=='true'
 if d['State']['Running']:subprocess.run(['docker','stop','-t','15',name],check=True,stdout=subprocess.DEVNULL,timeout=90)
 subprocess.run(['docker','rm',name],check=True,stdout=subprocess.DEVNULL);stopped.append(name)
for name in ['cody-shared-20261026','cody-dashboard-proof-20261026']:
 p=subprocess.run(['docker','network','inspect',name],capture_output=True,text=True)
 if p.returncode:continue
 d=json.loads(p.stdout)[0];assert not d.get('Containers');subprocess.run(['docker','network','rm',name],check=True,stdout=subprocess.DEVNULL)
ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();containers=json.loads(subprocess.check_output(['docker','inspect',*ids]));removed=[]
for rel in ['marsha-pilot/profile','marsha-pilot/wiki','marsha-pilot-before-Manus/profile','marsha-pilot-before-Manus/wiki','hindsight-empty-test/data','hindsight-migration-proof/data','qdrant-pilot/storage','offsite/inputs']:
 target=W/rel
 if not target.exists():continue
 assert target.resolve()==target and W in target.parents and not target.is_symlink()
 for d in containers:
  for m in d['Mounts']:
   src=P(m['Source']);assert src!=target and target not in src.parents,'Test path remains mounted'
 for fd in P('/proc').glob('[0-9]*/fd/*'):
  try:link=os.readlink(fd)
  except OSError:continue
  assert not (link==str(target) or link.startswith(str(target)+'/')),'Test path remains open'
 shutil.rmtree(target);removed.append(str(target))
cipher=A/off['name'];assert cipher.resolve()==cipher and A in cipher.parents
with cipher.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==off['cipherSha256']
cipher.unlink();identity.unlink();assert durable.exists() and not identity.exists();proof={'passed':True,'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'vaultKeyFreshReadbackVerified':True,'temporaryServerKeyRemoved':True,'temporaryUploadCipherRemoved':True,'ownedFixtureContainersRemoved':stopped,'temporaryPathsRemoved':removed,'freeBytesRecovered':shutil.disk_usage(W).free-before,'currentColdRecoveryArchiveRetained':str(durable),'allRollbacksProofsAndProductionDataRetained':True};(W/'cleanup.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
