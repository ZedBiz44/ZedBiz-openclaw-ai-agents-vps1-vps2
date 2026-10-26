"""Apply only the audited OpenClaw 2026.10.4 mutation-coordinator shape."""
import pathlib
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/app')
marker = 'zedbiz-wiki-flock-v1'
start = 'async function withMemoryWikiVaultMutation(vaultPath, mutation) {'
needle = '\treturn await vaultMutationQueue.enqueue(key, async () => {\n\t\ttry {'
replacement = '\treturn await vaultMutationQueue.enqueue(key, async () => {\n\t\tconst releaseSharedLock = await zedbizAcquireWikiLock(key);\n\t\ttry {'
end = '\t\t\tlease.active = false;\n\t\t}\n\t});\n}'
new_end = '\t\t\tlease.active = false;\n\t\t\tawait releaseSharedLock();\n\t\t}\n\t});\n}'
matches = []
for file in (root / 'dist').glob('*.mjs'):
    text = file.read_text()
    if start not in text:
        continue
    if marker in text:
        matches.append(file)
        continue
    begin = text.index(start)
    finish = text.index('\n//#endregion', begin)
    block = text[begin:finish]
    if block.count(needle) != 1 or block.count(end) != 1:
        raise SystemExit('Unsupported coordinator; review the upstream change before upgrading: ' + str(file))
    block = block.replace(needle, replacement).replace(end, new_end)
    text = text[:begin] + block + text[finish:]
    # Lint writes its report after compile returns. Keep that report write in
    # the same transaction so it cannot invalidate a different owner's build.
    lint = 'async function lintMemoryWikiVault(config, options = {}) {'
    if text.count(lint) != 1:
        raise SystemExit('Unsupported lint entrypoint: ' + str(file))
    text = text.replace(lint, '''async function lintMemoryWikiVault(config, options = {}) {
    return withMemoryWikiVaultMutation(config.vault.path, () => zedbizLintUnlocked(config, options));
}
async function zedbizLintUnlocked(config, options = {}) {''')
    text = '// ' + marker + '\nimport { acquireWikiLock as zedbizAcquireWikiLock } from "/opt/zedbiz/wiki-lock/lock.mjs";\n' + text
    file.write_text(text)
    matches.append(file)
if len(matches) != 1:
    raise SystemExit('Expected exactly one bundled coordinator; found ' + str(len(matches)))
print('Verified Wiki lock coordinator: ' + matches[0].name)
