"""Prepare in-place Drive index updates only after the new encrypted backup passes."""
import pathlib,json,hashlib,subprocess,os,datetime
P=pathlib.Path;S=P('/home/jackadmin/vps1-10-6-20261023');W=P('/opt/openclaw/backups/shared-updates-20261026/offsite')
off=json.loads((W/'offsite.json').read_text());assert off['passed'] and off['cloudMd5AndSizeVerified'] and off['decryptionRoundtripVerified']
gog=['docker','exec','terry','gog','--account','jack@zbiz.work','--no-input','--json','--readonly']
def get(id):
 r=json.loads(subprocess.check_output(gog+['drive','get',id,'--fields=id,name,size,md5Checksum,parents,webViewLink'],text=True));return r.get('file',r)
ids={'backup-index-before.json':'1AxObfW_mSsJrHbTBoqEO6MTxsUngPsKO','backup-key-before.json':'17Xqakx1la2dy5Hnv1543SwBnGHasMhAB'}
for name,id in ids.items():
 data=(S/name).read_bytes();m=get(id);assert m['md5Checksum']==hashlib.md5(data).hexdigest() and int(m['size'])==len(data),'Drive index changed since last read'
idx=json.loads((S/'backup-index-before.json').read_text());key=json.loads((S/'backup-key-before.json').read_text());files=idx['backupFiles'];old=[x for x in files if x['component']=='shared-services-and-memory'];assert len(old)==1 and old[0]['fileId']=='1wlVHPH3bFg1z6TxJroFxBPOJWqyWBPc7';assert len(files)==13
new={'component':'shared-services-and-memory',**off,'url':off.get('url') or 'https://drive.google.com/file/d/'+off['fileId']+'/view','decryptionVerified':True,'freshCloudMd5AndSizeVerified':True,'snapshotDate':'2026-10-26'}
idx['backupFiles']=[new if x['component']=='shared-services-and-memory' else x for x in files];now=datetime.datetime.now(datetime.timezone.utc).isoformat();idx.update({'publicationStatus':'Complete','checkedUtc':now,'latestSharedMaintenanceDate':'2026-10-26','agentStateSnapshotDate':'2026-10-24','currentRuntimeImagesIncluded':True,'fileCount':13,'totalEncryptedBytes':sum(x['bytes'] for x in idx['backupFiles']),'scope':'Application recovery set. Agent state snapshots remain dated October24. Shared service state, Hindsight1.1/Qdrant1.20 and all current post-Manus custom gateway/Asana images refreshed October26. No full OS image claimed.'})
key.update({'backupPublicationStatus':'Complete','verifiedUtc':now,'backupFileCount':13,'totalEncryptedBytes':idx['totalEncryptedBytes'],'latestSharedMaintenanceDate':'2026-10-26','latestSharedBackupFileId':off['fileId'],'agentStateSnapshotDate':'2026-10-24'})
assert key['itemReference']=='op://z-backups/3kgz2ekjiqzbtd4kwebuinp7lq/password' and key['publicRecipient']==idx['keyReference']['publicRecipient']
for name,obj in [('backup-index-current.json',idx),('backup-key-current.json',key)]:
 p=S/name;p.write_text(json.dumps(obj,indent=2)+'\n');os.chown(p,1001,1001);os.chmod(p,0o644)
print(json.dumps({'prepared':True,'backupFiles':13,'totalEncryptedBytes':idx['totalEncryptedBytes'],'newSharedFileId':off['fileId']}))
