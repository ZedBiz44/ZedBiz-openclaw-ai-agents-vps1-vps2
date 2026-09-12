// OpenClaw 2026.8.2: filter IMAP UIDs before fetching message sources.
// Usage: node patch-imap-source-fetch.mjs /path/to/openclaw
// Refuses unknown code; retains the exact original beside each modified file.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const root = process.argv[2];
if (!root) throw new Error('Provide the OpenClaw package root');
const marker = 'zedbiz-imap-metadata-first-v1';
const targets = [
  ['dist/extensions/imap/index.js', /\t\tconst messages = \[\];\n\t\tfor await \(const message of client\.fetch\(`\$\{cursor\.lastSeenUid \+ 1\}:\*`, \{\n\t\t\tuid: true,\n\t\t\tinternalDate: true,\n\t\t\tsize: true,\n\t\t\tsource: \{ maxLength: MAX_SOURCE_BYTES \}\n\t\t\}, \{ uid: true \}\)\) if \(message\.uid > cursor\.lastSeenUid\) messages\.push\(message\);/],
  ['extensions/imap/src/watcher.ts', /    const messages: FetchMessageObject\[\] = \[\];\n    for await \(const message of client\.fetch\(\n      `\$\{cursor\.lastSeenUid \+ 1\}:\*`,\n      \{ uid: true, internalDate: true, size: true, source: \{ maxLength: MAX_SOURCE_BYTES \} \},\n      \{ uid: true \},\n    \)\) \{\n      \/\/ IMAP N:\* returns the mailbox's final message even when its UID is below N\.\n      if \(message\.uid > cursor\.lastSeenUid\) \{\n        messages\.push\(message\);\n      \}\n    \}/],
];
const changes = [];
for (const [relative, pattern] of targets) {
  const file = path.join(root, relative);
  if (!fs.existsSync(file)) {
    if (relative.startsWith('dist/')) throw new Error(`Missing deployed bundle: ${file}`);
    continue;
  }
  const original = fs.readFileSync(file, 'utf8');
  if (original.includes(marker)) { console.log(JSON.stringify({file, status:'already-patched'})); continue; }
  if ((original.match(new RegExp(pattern.source, 'g')) || []).length !== 1) throw new Error(`Unknown watcher code: ${file}`);
  const typed = relative.endsWith('.ts');
  const replacement = `    // ${marker}: N:* can return an old UID; never fetch its source.
    const pendingUids${typed ? ': number[]' : ''} = [];
    for await (const message of client.fetch(\`\${cursor.lastSeenUid + 1}:*\`, { uid: true }, { uid: true })) {
      if (message.uid > cursor.lastSeenUid) pendingUids.push(message.uid);
    }
    if (pendingUids.length === 0 || this.stopping || this.client !== client) return;
    const messages${typed ? ': FetchMessageObject[]' : ''} = [];
    for await (const message of client.fetch(pendingUids, {
      uid: true, internalDate: true, size: true, source: { maxLength: MAX_SOURCE_BYTES }
    }, { uid: true })) {
      if (message.uid > cursor.lastSeenUid) messages.push(message);
    }`;
  changes.push({file,original,updated:original.replace(pattern,()=>replacement)});
}
for (const {file,original,updated} of changes) {
  const backup = `${file}.before-zedbiz-imap-v1`;
  if (fs.existsSync(backup) && fs.readFileSync(backup,'utf8') !== original) throw new Error(`Backup conflict: ${backup}`);
}
for (const {file,original,updated} of changes) {
  const backup = `${file}.before-zedbiz-imap-v1`;
  if (!fs.existsSync(backup)) fs.copyFileSync(file,backup,fs.constants.COPYFILE_EXCL);
  fs.writeFileSync(file,updated);
  console.log(JSON.stringify({file,status:'patched',backup,sha256:crypto.createHash('sha256').update(updated).digest('hex')}));
}
