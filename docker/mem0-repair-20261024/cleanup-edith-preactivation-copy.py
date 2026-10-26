"""Remove only the rejected preactivation copy after the original state was restored."""
import pathlib,json,subprocess,hashlib,shutil,os
P=pathlib.Path;os.umask(0o077);A=P('/opt/openclaw/backups/fleet-10-6-20261024/edith');target=A/'failed-preactivation-state';live=P('/opt/openclaw/agents/edith')
failure=json.loads((A/'failure.json').read_text());assert failure['changed'] and not failure['startedNew']
assert failure['message']=='Doctor lint errors require diagnosis before activation'
lint=json.loads((A/'lint.json').read_text());errors=[f for f in lint['findings'] if f['severity']=='error'];assert len(errors)==1 and errors[0]['checkId']=='core/doctor/runtime-tool-schemas' and 'EAI_AGAIN edith-asana-mcp' in errors[0]['requirement']
assert json.loads((live/'config/openclaw.json').read_text())==json.loads((A/'config-before.json').read_text())
assert (A/'resume-original.private.log').exists() and (A/'state-before.tar.gz').is_file() and json.loads((A/'checkpoint.json').read_text())
assert target.is_dir() and not target.is_symlink() and target.resolve()==target
ids=subprocess.check_output(['docker','ps','-aq'],text=True).split();containers=json.loads(subprocess.check_output(['docker','inspect',*ids]))
for d in containers:
 for mount in d.get('Mounts',[]):
  source=P(mount['Source']);assert source!=target and target not in source.parents
for proc in P('/proc').glob('[0-9]*'):
 try:
  if proc.name!=str(os.getpid()):assert str(target).encode() not in (proc/'cmdline').read_bytes()
 except (FileNotFoundError,ProcessLookupError,PermissionError):pass
shutil.copy2(target/'config/openclaw.json',A/'rejected-config.private.json');shutil.copy2(target/'workspace/ensure-mem0-compat.sh',A/'rejected-ensure.sh')
before=shutil.disk_usage(A).free;shutil.rmtree(target);assert not target.exists();proof={'removed':str(target),'diskBytesFreed':shutil.disk_usage(A).free-before,'originalStateRestored':True,'recoveryArchiveAndFailureLogsRetained':True};(A/'rejected-copy-cleanup.json').write_text(json.dumps(proof));print(json.dumps(proof))

