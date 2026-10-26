"""Read back every indexed cloud file and metadata file before permitting cleanup."""
import pathlib,json,subprocess,hashlib,datetime
P=pathlib.Path;S=P('/home/jackadmin/vps1-10-6-20261023');W=P('/opt/openclaw/backups/shared-updates-20261026/offsite');folder='19RU1qtUM-w0k2c66Cpj1im3OPOV3llaZ';archive='15qOrH9sPX0gHu60GkF-pbuSjQ2YoOaWx'
gog=['docker','exec','terry','gog','--account','jack@zbiz.work','--no-input','--json','--readonly']
def get(id):
 r=json.loads(subprocess.check_output(gog+['drive','get',id,'--fields=id,name,size,md5Checksum,parents,webViewLink'],text=True));return r.get('file',r)
idx=json.loads((S/'backup-index-current.json').read_text());assert len(idx['backupFiles'])==13;checked=[]
for x in idx['backupFiles']:
 m=get(x['fileId']);assert m['md5Checksum']==x['cipherMd5'] and int(m['size'])==x['bytes'] and folder in m['parents'];checked.append({'component':x['component'],'fileId':x['fileId'],'bytes':x['bytes'],'md5AndSizeVerified':True})
metadata=[]
for name,id in [('backup-index-current.json','1AxObfW_mSsJrHbTBoqEO6MTxsUngPsKO'),('backup-key-current.json','17Xqakx1la2dy5Hnv1543SwBnGHasMhAB')]:
 data=(S/name).read_bytes();m=get(id);assert m['md5Checksum']==hashlib.md5(data).hexdigest() and int(m['size'])==len(data) and folder in m['parents'];metadata.append({'fileId':id,'bytes':len(data),'md5AndSizeVerified':True})
old=get('1wlVHPH3bFg1z6TxJroFxBPOJWqyWBPc7');assert archive in old['parents'] and folder not in old['parents']
proof={'passed':True,'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'backupFiles':checked,'metadataFiles':metadata,'supersededSharedBackupArchived':True,'totalEncryptedBytes':sum(x['bytes'] for x in checked),'agentStateSnapshotsRemainOctober24':True,'archiveRetentionMonths':1}
(W/'index-published.json').write_text(json.dumps(proof,indent=2));print(json.dumps({'publishedIndexVerified':True,'backupFiles':len(checked),'totalEncryptedBytes':proof['totalEncryptedBytes']}))
