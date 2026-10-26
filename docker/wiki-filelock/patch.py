"""Upgrade only the previously audited Wiki transaction integration."""
import pathlib

root = pathlib.Path('/app/dist')
files = [p for p in root.glob('*.mjs') if 'async function withMemoryWikiVaultMutation(' in p.read_text()]
if len(files) != 1:
    raise SystemExit('Expected one Wiki coordinator; review upstream before upgrade')
p = files[0]
t = p.read_text()
required = ['await zedbizAcquireWikiLock(key)', 'await releaseSharedLock()',
            'return withMemoryWikiVaultMutation(config.vault.path, () => zedbizLintUnlocked(config, options));',
            'async function zedbizLintUnlocked(', '"/opt/zedbiz/wiki-lock/lock.mjs"']
if not all(t.count(s) == 1 for s in required):
    raise SystemExit('Existing Wiki/lint transaction shape changed; review before upgrade')
if t.count('zedbiz-wiki-flock-v1') != 1 or 'zedbiz-wiki-filelock-fd-v2' in t:
    raise SystemExit('Expected the known v1 integration as base')
p.write_text(t.replace('zedbiz-wiki-flock-v1', 'zedbiz-wiki-filelock-fd-v2'))
print('Preserved Wiki queue, nested transactions and complete lint wrapper')
