import fs from 'node:fs/promises';
const [vault, id] = process.argv.slice(2);
const files = await fs.readdir('/app/dist');
const name = files.find(name => name.startsWith('presentation-') && name.endsWith('.mjs'));
const wiki = await import('/app/dist/' + name);
// Each process has its own private cache, as each production agent does.
const entries = new Map();
wiki.j(wiki.M(() => ({
  async register(key, bytes, metadata) { entries.set(key, {key, bytes, metadata}); },
  async lookup(key) { return entries.get(key); },
  async entries() { return [...entries.values()]; },
  async delete(key) { return entries.delete(key); },
})));
const config = {
  vaultMode: 'isolated', vault: {scope: 'global', path: vault, renderMode: 'native'},
  obsidian: {enabled: false, useOfficialCli: false, openAfterWrites: false},
  bridge: {enabled: false}, unsafeLocal: {allowPrivateMemoryCoreAccess: false, paths: []},
  ingest: {autoCompile: true, maxConcurrentJobs: 1, allowUrlIngest: false},
  search: {backend: 'local', corpus: 'wiki'}, context: {includeCompiledDigestPrompt: false},
  render: {preserveHumanBlocks: true, createBacklinks: true, createDashboards: true},
};
const inputPath = '/tmp/wiki-lock-input-' + id + '.md';
await fs.writeFile(inputPath, '# Isolation test ' + id + '\nA unique source for concurrent import verification.\n');
const result = await wiki.m({config, inputPath, title: 'Lock verification ' + id});
console.log(JSON.stringify({id, imported: result.pagePath, resultKeys: Object.keys(result)}));
const compiled = await wiki.y(config);
console.log(JSON.stringify({id, compiled: true, updatedFiles: compiled.updatedFiles.length}));
const lint = await wiki.p(config);
console.log(JSON.stringify({id, linted: true, issues: lint.issueCount}));
