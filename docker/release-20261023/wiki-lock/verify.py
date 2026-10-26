"""Startup/upgrade gate: fail visibly rather than silently lose Wiki locking."""
import hashlib
import pathlib
import sys

root = pathlib.Path('/app/dist')
files = [p for p in root.glob('*.mjs') if 'async function withMemoryWikiVaultMutation(' in p.read_text()]
valid = len(files) == 1
if valid:
    text = files[0].read_text()
    valid = all(s in text for s in ['zedbiz-wiki-flock-v1', 'await zedbizAcquireWikiLock(key)',
                                  'await releaseSharedLock()', 'async function zedbizLintUnlocked('])
for name in ['lock.mjs', 'hold-lock.py']:
    valid = valid and pathlib.Path('/opt/zedbiz/wiki-lock', name).is_file()
if not valid:
    sys.exit('Wiki lock missing or incompatible. Rebuild with docker/wiki-lock before starting this shared-Wiki agent.')
print('Shared Wiki lock verified')
