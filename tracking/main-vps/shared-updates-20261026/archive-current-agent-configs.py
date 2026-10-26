"""Include verified current post-Manus gateway configuration alongside current images."""
import pathlib,json,hashlib,subprocess,datetime
P=pathlib.Path;W=P('/opt/openclaw/backups/shared-updates-20261026');A=W/'offsite';inputs=A/'inputs';assert inputs.is_dir() and not (A/'VPS1-2026-10-26-shared-services-and-current-images.tar.age').exists()
baseline=json.loads((W/'post-Manus-baseline.private.json').read_text());proof=[]
for row in baseline:
 for name,digest in row['files'].items():
  source=P(name);assert hashlib.sha256(source.read_bytes()).hexdigest()==digest,'Post-Manus config changed'
  target=inputs/'original-paths'/name.lstrip('/')
  if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
  else:
   target.parent.mkdir(parents=True,exist_ok=True);subprocess.run(['cp','-a',str(source),str(target)],check=True)
  proof.append({'agent':row['agent'],'path':name,'sha256':digest,'currentPostManusConfigurationIncluded':True})
result={'passed':True,'checkedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':proof,'configurationOnlyFullAgentStateRemainsOctober24':True};(inputs/'current-agent-configuration-proof.json').write_text(json.dumps(result,indent=2));(W/'current-agent-configuration-proof.json').write_text(json.dumps(result,indent=2));print(json.dumps({'currentAgentConfigurationBackupPassed':True,'files':len(proof)}))
