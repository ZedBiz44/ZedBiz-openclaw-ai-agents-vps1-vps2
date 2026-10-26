"""Build/startup gate: package pin, integration and installed-file integrity."""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor'))
import filelock

assert filelock.__version__ == '4.2.1' and filelock.has_fcntl, 'Native filelock 4.2.1 required'
assert pathlib.Path(filelock.__file__).resolve().is_relative_to(ROOT / 'vendor')
files = [p for p in pathlib.Path('/app/dist').glob('*.mjs')
         if 'async function withMemoryWikiVaultMutation(' in p.read_text()]
assert len(files) == 1, 'Wiki coordinator changed'
t = files[0].read_text()
for token in ['zedbiz-wiki-filelock-fd-v2', 'await zedbizAcquireWikiLock(key)',
              'await releaseSharedLock()', 'async function zedbizLintUnlocked(',
              'return withMemoryWikiVaultMutation(config.vault.path, () => zedbizLintUnlocked(config, options));']:
    assert t.count(token) == 1, 'Wiki transaction/upgrade gate missing: ' + token
paths = [ROOT / n for n in ['lock.mjs', 'acquire-lock.py', 'verify.py', 'patch.py']]
paths += [p for p in (ROOT / 'vendor').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
manifest = ROOT / 'integrity.json'
if sys.argv[1:] == ['--record']:
    if manifest.exists():
        raise SystemExit('Refusing to overwrite build integrity manifest')
    manifest.write_text(json.dumps({'version': 'filelock-fd-v2', 'files': hashes}, sort_keys=True, indent=2))
else:
    assert sys.argv[1:] == []
    assert json.loads(manifest.read_text())['files'] == hashes, 'Installed Wiki/filelock files changed'
print('Shared Wiki filelock 4.2.1 / parent-held descriptor v2 verified')
