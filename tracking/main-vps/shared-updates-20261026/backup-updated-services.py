"""Refresh encrypted offsite recovery after shared upgrades and preserve all current Asana-fixed images."""
import pathlib,subprocess,json,os,time,hashlib,shutil,sqlite3,tarfile,urllib.request,urllib.parse,datetime
P=pathlib.Path;os.umask(0o077);W=P('/opt/openclaw/backups/shared-updates-20261026');A=W/'offsite';inputs=A/'inputs';inputs.mkdir(mode=0o700);assert json.loads((A/'key-reference.json').read_text())['passed'];agents=['terry','marsha','edith','vivian','amanda','victor','wilma','gohzed','grogar','inga','maggie'];supports=['hindsight','hindsight-db','mem0-dev-qdrant-1','1password-connect-api','1password-connect-sync','caddy','z-code-allocator','z-code-admin','z-code-notion-mirror','zedbiz-restart-api','rocky-restart-bridge','rocky-tunnel-bridge','portainer','filebrowser','uptime-kuma','dozzle','homepage','docker-socket-proxy'];names=[*[x for n in agents for x in [n,n+'-asana-mcp']],*supports];containers=json.loads(subprocess.check_output(['docker','inspect',*names]));byName={d['Name'].lstrip('/'):d for d in containers}
def run(args,label,timeout=300):
 p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(A/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return p.stdout
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);run(['cp','-a',str(src),str(dst)],'copy-'+str(len(list(inputs.iterdir()))))
for component in ['hindsight','qdrant','connect','portainer','uptime-kuma','dozzle','homepage','cloud-init']:assert json.loads((W/('update-'+component)/'acceptance.json').read_text())['passed']
assert json.loads((W/'vps1-live-memory-acceptance.json').read_text())['passed'];assert json.loads((W/'Manus-fix-preservation.json').read_text())['passed'];assert json.loads(P('/home/jackadmin/vps1-10-6-20261023/vps2-memory-acceptance-20261026.json').read_text())['passed']
(inputs/'runtime-inspect.private.json').write_text(json.dumps(containers));(inputs/'networks.private.json').write_bytes(subprocess.check_output(['docker','network','inspect',*subprocess.check_output(['docker','network','ls','-q'],text=True).split()]));images={}
for name in [*[x for n in agents for x in [n,n+'-asana-mcp']],'hindsight']:
 d=byName[name];role='hindsight' if name=='hindsight' else 'asana' if name.endswith('-asana-mcp') else 'gateway';ref=d['Config']['Image'];ref='zedbiz/hindsight:1.1.0-flashrank-20261023' if name=='hindsight' else ref;assert '@sha256:' not in ref and not ref.startswith('sha256:');assert json.loads(subprocess.check_output(['docker','image','inspect',ref]))[0]['Id']==d['Image'];row=images.setdefault(d['Image'],{'id':d['Image'],'refs':[],'roles':[]})
 if ref not in row['refs']:row['refs'].append(ref)
 if role not in row['roles']:row['roles'].append(role)
catalog={'images':list(images.values()),'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'allCurrentManusPatchedGateways':True};imgDir=inputs/'current-images';imgDir.mkdir();(imgDir/'catalog.json').write_text(json.dumps(catalog,indent=2));archive=imgDir/'images.tar.gz';imageLog=(A/'image-save.private.err').open('w');imageOut=archive.open('xb');save=subprocess.Popen(['docker','image','save',*[r for i in images.values() for r in i['refs']]],stdout=subprocess.PIPE,stderr=imageLog);compress=subprocess.Popen(['nice','-n','15','pigz','-p','2','-3'],stdin=save.stdout,stdout=imageOut,stderr=imageLog);save.stdout.close();print(json.dumps({'backupPhase':'current-image-archive','uniqueImages':len(images)}),flush=True)
# Fresh database snapshots and coherent management data copies are gathered while images stream.
pg=byName['hindsight-db'];pgEnv=dict(e.split('=',1) for e in pg['Config']['Env']);user=pgEnv.get('POSTGRES_USER','postgres');database=pgEnv.get('POSTGRES_DB',user);dbDir=inputs/'databases';dbDir.mkdir();dump=dbDir/'hindsight.dump'
with dump.open('xb') as out,(A/'pg-dump.private.err').open('w') as err:p=subprocess.run(['docker','exec','hindsight-db','pg_dump','-U',user,'-d',database,'-Fc'],stdout=out,stderr=err,timeout=300)
assert p.returncode==0;run(['docker','run','--rm','--network','none','--entrypoint','pg_restore','-v',str(dump)+':/backup.dump:ro',pg['Image'],'--list','/backup.dump'],'pg-catalog')
# Restore the current1.1 dump into the already-isolated same-version PG fixture.
fixtureDb='cody-shared-20261026-db';targetDb='current_backup_20261026';run(['docker','exec',fixtureDb,'createdb','-U','hindsight',targetDb],'restore-create-db')
with dump.open('rb') as src,(A/'pg-restore.private.log').open('w') as out:p=subprocess.run(['docker','exec','-i',fixtureDb,'pg_restore','--exit-on-error','--no-owner','--no-privileges','-U','hindsight','-d',targetDb],stdin=src,stdout=out,stderr=subprocess.STDOUT,timeout=600)
assert p.returncode==0;tableCounts={t:int(run(['docker','exec',fixtureDb,'psql','-U','hindsight','-d',targetDb,'-Atc','select count(*) from '+t],'restore-count-'+t).strip()) for t in ['banks','documents','memory_units','entities','mental_models','knowledge_pages','chunks','directives','webhooks']};assert tableCounts['banks'] and tableCounts['memory_units'];(dbDir/'hindsight-restore-proof.json').write_text(json.dumps({'passed':True,'restoredCurrent11Database':True,'counts':tableCounts,'sha256':sha(dump)},indent=2))
q=byName['mem0-dev-qdrant-1'];qenv=dict(e.split('=',1) for e in q['Config']['Env']);qkey=qenv['QDRANT__SERVICE__API_KEY'];qbase='http://'+next(iter(q['NetworkSettings']['Networks'].values()))['IPAddress']+':6333'
def qreq(path,method='GET',data=None):
 headers={'api-key':qkey}
 if data is not None:headers['Content-Type']='application/json';data=json.dumps(data).encode()
 with urllib.request.urlopen(urllib.request.Request(qbase+path,headers=headers,method=method,data=data),timeout=120) as r:return json.load(r)
snap=qreq('/snapshots','POST',{})['result'];qfile=dbDir/'qdrant.storage.snapshot'
with urllib.request.urlopen(urllib.request.Request(qbase+'/snapshots/'+urllib.parse.quote(snap['name'],safe=''),headers={'api-key':qkey}),timeout=180) as response,qfile.open('xb') as out:shutil.copyfileobj(response,out)
(dbDir/'qdrant-snapshot-metadata.json').write_text(json.dumps({'version':'1.20.0','snapshot':snap,'sha256':sha(qfile),'collectionCounts':{c['name']:qreq('/collections/'+urllib.parse.quote(c['name'],safe=''))['result']['points_count'] for c in qreq('/collections')['result']['collections']}},indent=2))
for group,serviceList in [('portainer',['portainer']),('connect',['1password-connect-api','1password-connect-sync'])]:
 d=byName[serviceList[0]];source=next(P(m['Source']) for m in d['Mounts'] if m['Destination'] in ['/data','/home/opuser/.op/data']);run(['docker','stop','-t','15',*serviceList],group+'-snapshot-stop',90)
 try:copy(source,inputs/'management'/group/'data')
 finally:run(['docker','start',*serviceList],group+'-snapshot-resume',90)
# Kuma uses a supported online SQLite backup; no monitor/notification clone is started.
source=P('/opt/uptime-kuma/data');dest=inputs/'management/uptime-kuma/data';copy(source,dest);db=source/'kuma.db';dst=dest/'kuma.db'
for p in [dst,P(str(dst)+'-wal'),P(str(dst)+'-shm')]:
 if p.exists():p.unlink()
with sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) as oldDb,sqlite3.connect(dst) as newDb:oldDb.backup(newDb);assert newDb.execute('pragma quick_check').fetchone()==('ok',)
st=db.stat();os.chown(dst,st.st_uid,st.st_gid);os.chmod(dst,st.st_mode&0o7777)
for src in [P('/opt/homepage/config'),P('/opt/homepage/icons'),P('/opt/openclaw/1password-connect/1password-credentials.json'),P('/etc/cloud')]:copy(src,inputs/'original-paths'/str(src).lstrip('/'))
for d in containers:
 labels=d['Config'].get('Labels') or {};files=labels.get('com.docker.compose.project.config_files','')
 for path in files.split(','):
  src=P(path)
  if path and src.is_file():
   target=inputs/'original-paths'/str(src).lstrip('/')
   if not target.exists():copy(src,target)
# Immutable image save is complete before cold-loading and updating recovery manifests.
assert compress.wait(timeout=1200)==0 and save.wait(timeout=60)==0;imageOut.close();imageLog.close();run(['pigz','-t',str(archive)],'image-gzip-check');catalog['archiveSha256']=sha(archive);catalog['archiveBytes']=archive.stat().st_size;(imgDir/'catalog.json').write_text(json.dumps(catalog,indent=2));print(json.dumps({'backupPhase':'cold-image-restore','archiveGiB':round(archive.stat().st_size/1024**3,2)}),flush=True);run(['/usr/bin/python3','/home/jackadmin/vps1-10-6-20261023/prove-current-images-cold-20261026.py'],'cold-images',1800);assert json.loads((imgDir/'cold-restore-proof.json').read_text())['passed']
recovery=P('/opt/openclaw/recovery/release-20261026-current-images');assert not recovery.exists();recovery.mkdir(mode=0o755);os.link(archive,recovery/'images.tar.gz');os.chmod(recovery/'images.tar.gz',0o644);(recovery/'catalog.json').write_text(json.dumps(catalog,indent=2));alignment=[];oldManifests=inputs/'previous-recovery-manifests';oldManifests.mkdir()
for agent in agents:
 manifest=P('/opt/openclaw/recovery')/(agent+'-20261018')/'manifest.json' if agent in ['amanda','victor'] else P('/opt/openclaw/recovery/fleet-20261018')/agent/'manifest.json';old=manifest.read_bytes();m=json.loads(old);assert sha(P(m['wrapper']))==m['wrapper_sha256'];(oldManifests/(agent+'.json')).write_bytes(old);m['archive']=str(recovery/'images.tar.gz');m['sha256']=catalog['archiveSha256'];m['images']=[{'ref':byName[n]['Config']['Image'],'id':byName[n]['Image'],'automatic':True} for n in [agent,agent+'-asana-mcp']];st=manifest.stat();temp=manifest.with_name(manifest.name+'.cody26.tmp');assert not temp.exists();temp.write_text(json.dumps(m,indent=2)+'\n');os.chmod(temp,st.st_mode&0o7777);os.chown(temp,st.st_uid,st.st_gid);os.replace(temp,manifest);assert sha(P(m['wrapper']))==m['wrapper_sha256'];alignment.append({'agent':agent,'currentImagePinsVerified':True,'wrapperUnchanged':True,'manifest':str(manifest)});copy(manifest,inputs/'original-paths'/str(manifest).lstrip('/'))
(inputs/'recovery-alignment.json').write_text(json.dumps({'passed':True,'agents':alignment,'newArchive':str(recovery/'images.tar.gz'),'coldRestoreVerified':True},indent=2));(W/'recovery-alignment.json').write_bytes((inputs/'recovery-alignment.json').read_bytes())
prior=P('/opt/openclaw/backups/private-recovery-20261024/supporting-images')
for p in prior.iterdir():
 if p.is_file() and (p.name.endswith('.tar.gz') or p.name=='proof.json'):copy(p,inputs/'unchanged-custom-support-images'/p.name)
for component in ['hindsight','qdrant','connect','portainer','uptime-kuma','dozzle','homepage','cloud-init']:copy(W/('update-'+component)/'acceptance.json',inputs/'acceptance'/(component+'.json'))
for file in ['Manus-fix-preservation.json','vps1-live-memory-acceptance.json']:copy(W/file,inputs/'acceptance'/file)
copy(P('/home/jackadmin/vps1-10-6-20261023/vps2-memory-acceptance-20261026.json'),inputs/'acceptance/vps2-memory.json')
expected={str(p.relative_to(inputs)):sha(p) for p in inputs.rglob('*') if p.is_file() and not p.is_symlink()};(A/'input-sha256.private.json').write_text(json.dumps(expected));key=json.loads((A/'key-reference.json').read_text());name='VPS1-2026-10-26-shared-services-and-current-images.tar.age';cipher=A/name;print(json.dumps({'backupPhase':'encrypt-and-verify','regularFiles':len(expected)}),flush=True)
with cipher.open('xb') as out,(A/'tar.private.err').open('w') as te,(A/'age.private.err').open('w') as ae:
 tar=subprocess.Popen(['tar','-cf','-','-C',str(inputs),'.'],stdout=subprocess.PIPE,stderr=te);enc=subprocess.Popen(['age','-r',key['publicRecipient']],stdin=subprocess.PIPE,stdout=out,stderr=ae);digest=hashlib.sha256()
 while True:
  block=tar.stdout.read(1024*1024)
  if not block:break
  digest.update(block);enc.stdin.write(block)
 enc.stdin.close();assert tar.wait(timeout=120)==0 and enc.wait(timeout=120)==0
plainSha=digest.hexdigest();roundtrip=hashlib.sha256();seen={}
class Reader:
 def __init__(self,stream):self.stream=stream
 def read(self,n=-1):
  block=self.stream.read(n);roundtrip.update(block);return block
with (A/'decrypt.private.err').open('w') as err:
 dec=subprocess.Popen(['age','-d','-i',str(A/'age-identity.txt'),str(cipher)],stdout=subprocess.PIPE,stderr=err);reader=Reader(dec.stdout)
 with tarfile.open(fileobj=reader,mode='r|') as tar:
  for item in tar:
   if item.islnk():
    rel=item.name.removeprefix('./');target=item.linkname.removeprefix('./');assert rel in expected and target in expected and expected[rel]==expected[target];seen[rel]=expected[rel]
   if item.isfile():
    rel=item.name.removeprefix('./');assert rel in expected
    with tar.extractfile(item) as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
    assert actual==expected[rel];seen[rel]=actual
 while reader.read(1024*1024):pass
 assert dec.wait(timeout=60)==0 and roundtrip.hexdigest()==plainSha and seen==expected
stage=P('/opt/openclaw/agents/terry/config/.cody-shared-update-upload');assert not stage.exists();stage.mkdir(mode=0o700);os.chown(stage,1000,1000);link=stage/name;os.link(cipher,link);os.chown(cipher,1000,1000);gog=['docker','exec','terry','gog','--account','jack@zbiz.work','--no-input','--json'];folder='19RU1qtUM-w0k2c66Cpj1im3OPOV3llaZ';print(json.dumps({'backupPhase':'Drive-upload','bytes':cipher.stat().st_size}),flush=True)
try:
 cloud=json.loads(run(gog+['drive','upload','/home/node/.openclaw/.cody-shared-update-upload/'+name,'--parent',folder,'--name',name,'--mime-type','application/octet-stream'],'drive-upload',3600));cloud=cloud.get('file',cloud);meta=json.loads(run(gog+['--readonly','drive','get',cloud['id'],'--fields=id,name,size,md5Checksum,parents,webViewLink'],'drive-readback'));meta=meta.get('file',meta)
 with cipher.open('rb') as f:md5=hashlib.file_digest(f,'md5').hexdigest()
 assert meta['md5Checksum']==md5 and int(meta['size'])==cipher.stat().st_size and folder in meta['parents'];proof={'passed':True,'fileId':meta['id'],'name':name,'url':meta.get('webViewLink'),'bytes':cipher.stat().st_size,'cipherMd5':md5,'cipherSha256':sha(cipher),'plaintextSha256':plainSha,'allInputFilesVerifiedAfterDecryption':len(seen),'decryptionRoundtripVerified':True,'cloudMd5AndSizeVerified':True,'currentManusPatchedImagesColdRestored':len(images),'recoveryManifestsAligned':11,'currentHindsight11DatabaseRestored':True,'currentQdrantSnapshotIncluded':True,'serviceStateAndCredentialsIncluded':True,'publicThirdPartyImagesUsePinnedReferences':True,'scope':'Shared service recovery and current custom gateway/Asana images. Existing agent-state backups remain dated October24; no claim of a full fresh OS or agent-state image.'};(A/'offsite.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
finally:
 if link.exists():link.unlink()
 if stage.exists() and not any(stage.iterdir()):stage.rmdir()
