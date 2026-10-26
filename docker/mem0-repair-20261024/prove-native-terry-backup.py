"""Pilot the native online backup/restore path on Terry without restarting his Gateway."""
import pathlib,json,subprocess,os,shutil,hashlib,sqlite3
P=pathlib.Path;os.umask(0o077);live=P('/opt/openclaw/agents/terry');W=P('/opt/openclaw/backups/private-recovery-20261024');stage=live/'config/backups/cody-native-proof-20261024';inside='/home/node/.openclaw/backups/cody-native-proof-20261024'
assert not stage.exists() and shutil.disk_usage(live).free>14*1024**3
def sha(p):
 with P(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,label,timeout=1800):
 print(json.dumps({'nativeBackupPilot':label}),flush=True);p=subprocess.run(args,capture_output=True,text=True,timeout=timeout);(W/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed';return json.loads(p.stdout)
def jobs(p):
 db=sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True)
 try:return sorted((i,json.dumps({k:v for k,v in json.loads(s).items() if k not in ['state','updatedAtMs']},sort_keys=True)) for i,s in db.execute('select job_id,job_json from cron_jobs'))
 finally:db.close()
configSha=sha(live/'config/openclaw.json');jobBefore=jobs(live/'config/state/openclaw.sqlite');instructions={p.name:sha(p) for p in (live/'workspace').glob('*.md') if p.name in ['AGENTS.md','SOUL.md','USER.md','IDENTITY.md','MEMORY.md','TOOLS.md']}
stage.mkdir(mode=0o700,parents=True);os.chown(stage,1000,1000);os.chown(stage.parent,1000,1000)
result=run(['docker','exec','terry','node','/app/openclaw.mjs','backup','create','--output',inside+'/terry-native.tar.gz','--verify','--json'],'native-terry-create')
assert result.get('verified') is True
archive=stage/'terry-native.tar.gz';assert archive.is_file();archiveSha=sha(archive);archiveBytes=archive.stat().st_size
restored=run(['docker','exec','terry','node','/app/openclaw.mjs','backup','restore',inside+'/terry-native.tar.gz','--target',inside+'/restore','--json'],'native-terry-restore')
root=stage/'restore';matches=[p for p in root.rglob('openclaw.json') if sha(p)==configSha];assert len(matches)==1,'Restored main config missing/ambiguous';home=matches[0].parent
assert jobs(home/'state/openclaw.sqlite')==jobBefore,'Restored schedule definitions changed'
assert all(sha(home/'workspace'/n)==digest for n,digest in instructions.items()),'Restored instructions differ'
checked=[]
for p in home.rglob('*.sqlite'):
 db=sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True)
 try:
  db.create_function('octet_length',1,lambda x:None if x is None else len(x.encode() if isinstance(x,str) else x),deterministic=True);assert db.execute('pragma quick_check').fetchall()==[('ok',)]
 finally:db.close()
 checked.append(str(p.relative_to(home)))
assert len(checked)>=3 and sha(live/'config/openclaw.json')==configSha
proof={'passed':True,'nativeArchiveVerified':True,'freshTargetRestorePassed':True,'sqliteChecks':checked,'scheduleDefinitionsPreserved':len(jobBefore),'instructionFilesPreserved':list(instructions),'configurationUnchanged':True,'productionGatewayNotRestarted':True,'archiveBytes':archiveBytes,'archiveSha256':archiveSha,'customManagedPluginArtifactRequiredSeparately':True}
(W/'native-terry-backup-proof.json').write_text(json.dumps(proof,indent=2));assert stage.resolve()==stage and stage.is_relative_to(live/'config/backups');shutil.rmtree(stage);proof['temporaryPilotCopiesRemoved']=True;(W/'native-terry-backup-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)

