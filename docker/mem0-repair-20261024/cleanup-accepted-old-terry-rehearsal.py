"""Remove only the obsolete Terry test copy after fresh live acceptance."""
import pathlib,json,subprocess,shutil,os
P=pathlib.Path;os.umask(0o077);M=P('/opt/openclaw/backups/mem0-repair-20261024-r2');assert json.loads((M/'terry-activation/acceptance.json').read_text())['passed']
assert (M/'terry-activation/state-before.tar.gz').is_file() and json.loads((M/'terry-activation/checkpoint.json').read_text())
target=P('/opt/openclaw/backups/release-20261023/terry/rehearsal');assert target.is_dir() and not target.is_symlink() and target.resolve()==target
ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();containers=json.loads(subprocess.check_output(['docker','inspect',*ids])) if ids else []
for d in containers:
 for mount in d.get('Mounts',[]):
  source=P(mount['Source']);assert source!=target and target not in source.parents,'Test copy still mounted'
for proc in P('/proc').glob('[0-9]*'):
 try:
  if proc.name==str(os.getpid()):continue
  assert str(target).encode() not in (proc/'cmdline').read_bytes(),'Test copy still used by a process'
 except (FileNotFoundError,ProcessLookupError,PermissionError):pass
before=shutil.disk_usage(target).free;bytesUsed=int(subprocess.check_output(['du','-sb',str(target)],text=True).split()[0]);shutil.rmtree(target);assert not target.exists()
proof={'removed':str(target),'logicalBytes':bytesUsed,'diskBytesFreed':shutil.disk_usage(target.parent).free-before,'freshCheckpointRetained':True,'liveAcceptanceRetained':True}
(M/'old-rehearsal-cleanup.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof))

