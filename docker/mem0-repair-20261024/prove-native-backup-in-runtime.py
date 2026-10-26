"""Run inside Terry's live container; native backups require the live owner namespace and writable run ledger."""
import pathlib,json,subprocess,os,shutil,hashlib,sqlite3
P=pathlib.Path;os.umask(0o077);home=P('/home/node/.openclaw');stage=P('/tmp/cody-native-backup-proof-20261024');proofFile=home/'cody-native-backup-proof.json'
assert not stage.exists() and not proofFile.exists() and shutil.disk_usage('/tmp').free>12*1024**3;stage.mkdir(mode=0o700)
def sha(p):
 with P(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def jobs(p):
 db=sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True)
 try:return sorted((i,json.dumps({k:v for k,v in json.loads(s).items() if k not in ['state','updatedAtMs']},sort_keys=True)) for i,s in db.execute('select job_id,job_json from cron_jobs'))
 finally:db.close()
def run(args,label):
 print(json.dumps({'nativeRuntimeBackupPilot':label}),flush=True);p=subprocess.run(args,capture_output=True,text=True,timeout=1800);(stage/(label+'.private.log')).write_text(p.stdout+p.stderr);assert p.returncode==0,label+' failed; private log retained';return json.loads(p.stdout)
beforeConfig=sha(home/'openclaw.json');beforeJobs=jobs(home/'state/openclaw.sqlite');instructions={p.name:sha(p) for p in (home/'workspace').glob('*.md') if p.name in ['AGENTS.md','SOUL.md','USER.md','IDENTITY.md','MEMORY.md','TOOLS.md']}
archive=stage/'terry-native.tar.gz';result=run(['node','/app/openclaw.mjs','backup','create','--output',str(archive),'--verify','--json'],'create');assert result.get('verified') is True
archiveBytes=archive.stat().st_size;archiveSha=sha(archive);restore=stage/'restore';result=run(['node','/app/openclaw.mjs','backup','restore',str(archive),'--target',str(restore),'--json'],'restore')
matches=[p for p in restore.rglob('openclaw.json') if sha(p)==beforeConfig];assert len(matches)==1,'Restored main configuration missing/ambiguous';restoredHome=matches[0].parent
assert jobs(restoredHome/'state/openclaw.sqlite')==beforeJobs,'Schedule definitions differ';assert all(sha(restoredHome/'workspace'/name)==value for name,value in instructions.items()),'Instructions differ'
checked=[]
for p in restoredHome.rglob('*.sqlite'):
 db=sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True)
 try:
  db.create_function('octet_length',1,lambda x:None if x is None else len(x.encode() if isinstance(x,str) else x),deterministic=True);assert db.execute('pragma quick_check').fetchall()==[('ok',)]
 finally:db.close()
 checked.append(str(p.relative_to(restoredHome)))
assert len(checked)>=3 and sha(home/'openclaw.json')==beforeConfig
proof={'passed':True,'agent':'terry','nativeArchiveVerified':True,'freshTargetRestorePassed':True,'sqliteChecks':checked,'scheduleDefinitionsPreserved':len(beforeJobs),'instructionFilesPreserved':list(instructions),'configurationUnchanged':True,'productionGatewayNotRestarted':True,'archiveBytes':archiveBytes,'archiveSha256':archiveSha,'customManagedPluginArtifactRequiredSeparately':True}
assert stage.resolve()==stage and stage.parent==P('/tmp');shutil.rmtree(stage);proof['temporaryPilotCopiesRemoved']=True;proofFile.write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)

