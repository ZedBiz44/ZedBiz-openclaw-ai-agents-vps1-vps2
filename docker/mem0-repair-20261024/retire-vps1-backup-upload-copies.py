"""After verified cloud publication, remove temporary encrypted upload copies and the transient age identity."""
import pathlib,json,subprocess,hashlib,sys,os,datetime
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/private-recovery-20261024');assert json.loads((W/'current-backups-complete.json').read_text())['passed'];assert json.loads((W/'backup-index-published.json').read_text())['passed']
token=sys.stdin.read().strip();assert token.startswith('ops_');env=os.environ.copy();env['OP_SERVICE_ACCOUNT_TOKEN']=token;key=json.loads((W/'key-receipt.json').read_text());identity=W/'age-identity.txt';assert identity.is_file() and not identity.is_symlink()
p=subprocess.run(['op','read','op://z-backups/'+key['itemId']+'/password'],env=env,capture_output=True,text=True,timeout=90);assert p.returncode==0,'Vault read failed; retain temporary local identity';secret=p.stdout.strip();localSecret=next(line for line in identity.read_text().splitlines() if line.startswith('AGE-SECRET-KEY-1'));assert len(secret)>50 and secret==localSecret,'Vault key differs; retain local identity'
recipient=subprocess.check_output(['age-keygen','-y',str(identity)],text=True).strip();assert recipient==key['publicRecipient'];removed=[]
folders=[*[W/('agent-'+agent) for agent in ['terry','marsha','amanda','victor','wilma','gohzed','grogar','inga','maggie','edith','vivian']],W/'shared-recovery']
for folder in folders:
 proof=json.loads((folder/'offsite.json').read_text());assert proof['passed'] and proof['cloudMd5AndSizeVerified'] and proof['decryptionRoundtripVerified'];target=folder/proof['name'];assert target.resolve()==target and W in target.parents and not target.is_symlink()
 if target.exists():
  with target.open('rb') as file:assert hashlib.file_digest(file,'sha256').hexdigest()==proof['cipherSha256']
  size=target.stat().st_size;target.unlink();removed.append({'name':target.name,'bytes':size})
identity.unlink();assert not identity.exists();proof={'passed':True,'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'vaultKeyFreshReadbackVerified':True,'publicRecipient':recipient,'vault':'z-backups','itemId':key['itemId'],'temporaryLocalIdentityRemoved':True,'verifiedUploadCopiesRemoved':removed,'totalBytesRemoved':sum(r['bytes'] for r in removed),'offsiteFilesAndAllRecoveryReceiptsRetained':True};(W/'temporary-backup-copy-cleanup.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
