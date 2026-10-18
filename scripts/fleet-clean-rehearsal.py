"""Remove only disposable restored copies after acceptance; retain offline archives."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

name = sys.argv[1]
assert name in {'wilma','vivian','inga','maggie','gohzed','grogar','edith','terry','marsha'}
base = Path('/opt/openclaw/backups/fleet-20261018').resolve()
work = base/name
assert work.resolve() == work and not work.is_symlink()
acceptance = json.loads((work/'acceptance.json').read_text())
baseline = json.loads((work/'baseline.json').read_text())
assert acceptance['agent'] == name and acceptance['accepted'] is True
assert baseline['archiveSha256'] and (work/'before-10.4.tar').stat().st_size > 0
assert not subprocess.check_output(['docker','ps','-q','--filter',f'name=^/{name}-migration-check$'],text=True).strip()
removed = []
for leaf in ['rehearsal','extracted']:
    target = work/leaf
    assert target.resolve() == target and target.is_relative_to(base) and not target.is_symlink()
    if target.exists():
        shutil.rmtree(target)
        removed.append(str(target))
result = dict(agent=name, removedDisposableCopies=removed, retainedArchive=str(work/'before-10.4.tar'))
(work/'rehearsal-cleanup.json').write_text(json.dumps(result))
print(json.dumps(result), flush=True)

