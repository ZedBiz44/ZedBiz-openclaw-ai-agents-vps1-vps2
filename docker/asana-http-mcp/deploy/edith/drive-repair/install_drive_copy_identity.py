"""Activate only Edith's isolated binary copy identity path, preserving guards."""
from pathlib import Path
import shutil,sqlite3
root=Path('/home/node/.openclaw')
db=sqlite3.connect('file:'+str(root/'agents/main/agent/openclaw-agent.sqlite')+'?mode=ro',uri=True)
assert not db.execute("select session_key from session_nodes where status='running'").fetchall(),'Wait for the existing session to finish'
def replace(path,old,new):
    s=path.read_text();assert s.count(old)==1,(str(path),old)
    backup=path.with_name(path.name+'.before-copy-identity-20260918')
    if not backup.exists():shutil.copy2(path,backup)
    patched=s.replace(old,new,1);compile(patched,str(path),'exec');path.write_text(patched)

p=root/'private/folder-cleanup/albertawide/work.py'
replace(p,'def _gog(*args):','def _gog_once(*args):')
replace(p,"if args[0]=='copy' else 'gog'","if args[0] in ('copy','generate-id') else 'gog'")
replace(p,"if args[0]=='copy' and transient:","if args[0]=='copy' and transient and '--destination-id' not in args:")
replace(p,"FIELDS='id,name,mimeType", "def _gog(*args):\n if args[0]=='copy':\n  from drive_copy_identity import execute as copy_with_identity\n  return copy_with_identity(P,args,_gog_once)\n return _gog_once(*args)\n\nFIELDS='id,name,mimeType")
guard=root/'workspace/scripts/execution_guard.py'
replace(guard,"            raise RuntimeError('Uncertain prior write: reconcile this journal with live Drive before retry: ' + key)","            from drive_copy_identity import has_identity\n            if args[0] != 'copy' or not has_identity(base,args):\n                raise RuntimeError('Uncertain prior write: reconcile this journal with live Drive before retry: ' + key)\n            # A persisted Google-reserved ID makes this an exact same-resource retry.\n            # The copy transport revalidates source and destination before proceeding.")
wrapper=root/'workspace/edith-drive-repair/gog-copy'
s=wrapper.read_text();old='exec /home/node/.openclaw/workspace/edith-drive-repair/gog-edith "$@"';assert old in s
shutil.copy2(wrapper,wrapper.with_name('gog-copy.before-identity-20260918'))
wrapper.write_text(s.replace(old,'exec /home/node/.openclaw/workspace/edith-drive-repair/gog-edith-identity "$@"'))
print('Installed durable destination IDs for binary copies; legacy uncertain copies still held')

