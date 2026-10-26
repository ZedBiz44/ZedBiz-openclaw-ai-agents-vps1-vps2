"""Build versioned wrappers and packages without changing live mount sources."""
import hashlib,json,os,pathlib,shutil,subprocess,tempfile
root=pathlib.Path('/opt/openclaw/shared/tools-20261023');root.mkdir(mode=0o755)
bin=root/'bin';bin.mkdir(mode=0o755)
src=pathlib.Path('/home/jackadmin/vps1-10-6-20261023/tool-assets/gog')
shutil.copy2(src,bin/'gog-real')
gog=pathlib.Path('/opt/openclaw/shared/bin/gog').read_text()
old='/opt/openclaw/shared/bin/gog-real-0.45.0';new=str(bin/'gog-real')
assert gog.count(old)==1
updated=gog.replace(old,new);(bin/'gog-wrapper').write_text(updated);(bin/'gog-wrapper').chmod(0o755)
for name in ['mcporter','summarize']:
 text=(pathlib.Path('/opt/openclaw/shared/bin')/name).read_text()
 assert text.count('/opt/openclaw/shared/tools-20261018/')==1
 wrapper=bin/(name+'-wrapper');wrapper.write_text(text.replace('/opt/openclaw/shared/tools-20261018/',str(root)+'/'));wrapper.chmod(0o755)
# Verify real argument forwarding, including the draft-only flag, without contacting Gmail.
with tempfile.TemporaryDirectory(prefix='gog-wrapper-proof-') as temp:
 p=pathlib.Path(temp);mock=p/'mock';mock.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n');mock.chmod(0o755)
 wrapper=p/'gog';wrapper.write_text(updated.replace(new,str(mock)));wrapper.chmod(0o755)
 (p/'email-mode').write_text('draft_only\n');env={**os.environ,'GOG_HOME':str(p)}
 assert subprocess.check_output([str(wrapper),'drive','ls'],env=env,text=True).splitlines()==['--gmail-no-send','drive','ls']
 (p/'email-mode').unlink()
 assert subprocess.check_output([str(wrapper),'drive','ls'],env=env,text=True).splitlines()==['drive','ls']
subprocess.run([str(bin/'gog-real'),'--gmail-no-send','--version'],check=True)
private=pathlib.Path('/opt/openclaw/backups/release-20261023/shared-tools');private.mkdir(mode=0o700)
with (private/'npm-install.log').open('w') as log:
 subprocess.run(['docker','run','--rm','--network','host','-v',str(root)+':/out','node:24.22.1-bookworm-slim@sha256:2dd9a4f758e173b65fee15388f7706af6fb01ef50cf7a2c0538711d67a6981ae','npm','install','-g','--prefix','/out','--no-audit','--no-fund','mcporter@0.16.0','@steipete/summarize@0.25.3'],stdout=log,stderr=subprocess.STDOUT,check=True)
proof={'stagedRoot':str(root),'liveMountsChanged':False,'gogDraftOnlyForwardingPassed':True,'oldGogWrapperSha256':hashlib.sha256(gog.encode()).hexdigest(),'newGogWrapperSha256':hashlib.sha256(updated.encode()).hexdigest(),'packages':{'mcporter':'0.16.0','@steipete/summarize':'0.25.3'}}
(private/'proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof),flush=True)
