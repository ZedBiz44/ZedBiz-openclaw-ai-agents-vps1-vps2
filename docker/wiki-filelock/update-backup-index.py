"""Append the verified Wiki overlay to the existing Drive index with a version lease."""
import datetime,hashlib,json,os,pathlib,subprocess
P=pathlib.Path;ROOT=P('/opt/openclaw/recovery/wiki-filelock-20261026');proof=json.loads((ROOT/'offsite-proof.json').read_text());assert proof['passed']
stage=P('/opt/openclaw/agents/terry/config/.cody-wiki-index');stage.mkdir(mode=0o700);os.chown(stage,1000,1000)
gog=['docker','exec','terry','gog','--account','jack@zbiz.work','--no-input','--json'];prefix='/home/node/.openclaw/.cody-wiki-index/'
def call(args):
 p=subprocess.run(gog+args,capture_output=True,text=True,timeout=120);assert p.returncode==0,'Drive operation failed';r=json.loads(p.stdout);return r.get('file',r)
def md5(p):return hashlib.md5(p.read_bytes()).hexdigest()
try:
 for id,name in [('1AxObfW_mSsJrHbTBoqEO6MTxsUngPsKO','index'),('17Xqakx1la2dy5Hnv1543SwBnGHasMhAB','key-reference')]:
  meta=call(['--readonly','drive','get',id,'--fields=id,name,size,md5Checksum,version'])
  call(['--readonly','drive','download',id,'--out',prefix+name+'.json'])
  p=stage/(name+'.json');assert md5(p)==meta['md5Checksum'];obj=json.loads(p.read_text())
  (ROOT/(name+'-before.json')).write_bytes(p.read_bytes())
  if name=='index':
   assert not any(x.get('fileId')==proof['fileId'] for x in obj['backupFiles'])
   obj['backupFiles'].append({'component':'wiki-filelock-overlay',**proof,'snapshotDate':'2026-10-26','freshCloudMd5AndSizeVerified':True})
   obj['sharedRestoreOrder'].append(proof['fileId'])
   obj['fileCount']=len(obj['backupFiles']);obj['totalEncryptedBytes']=sum(x['bytes'] for x in obj['backupFiles'])
   obj['latestWikiOverlayFileId']=proof['fileId'];obj['scope']+=' Apply the October26 Wiki filelock image/configuration overlay last. This overlay uses the existing verified encryption recipient; its plaintext images passed cold restore and encrypted cloud size/checksum were verified. A fresh decryption roundtrip was not performed for this overlay.'
   count,total=obj['fileCount'],obj['totalEncryptedBytes']
  else:
   obj.update(backupFileCount=count,totalEncryptedBytes=total,latestWikiOverlayFileId=proof['fileId'])
  obj['checkedUtc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
  p.write_text(json.dumps(obj,indent=2)+'\n');os.chown(p,1000,1000)
  call(['drive','upload',prefix+p.name,'--replace',id,'--if-version',str(meta['version']),'--mime-type','application/json'])
  after=call(['--readonly','drive','get',id,'--fields=id,size,md5Checksum']);assert after['md5Checksum']==md5(p) and int(after['size'])==p.stat().st_size
  (ROOT/(name+'-current.json')).write_bytes(p.read_bytes())
 (ROOT/'index-proof.json').write_text(json.dumps({'passed':True,'existingIndexUpdatedWithVersionLease':True,'cloudReadbackMatched':True,'fileCount':count,'totalEncryptedBytes':total},indent=2))
 print(json.dumps({'backupIndexUpdated':True,'files':count}),flush=True)
finally:
 for p in stage.iterdir():
  assert p.is_file() and p.name in ['index.json','key-reference.json'];p.unlink()
 stage.rmdir()
