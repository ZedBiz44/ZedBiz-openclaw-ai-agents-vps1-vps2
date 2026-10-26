const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const path = process.argv[2];
const source = fs.readFileSync(path, 'utf8');
const old = 'options?.processMemoryLimitBytes ?? DEFAULT_PROCESS_MEMORY_LIMIT_BYTES';
assert.equal(source.split(old).length, 2, 'Expected exactly one cached-limit use');
const patched = source.replace(old, 'options?.processMemoryLimitBytes ?? process.constrainedMemory()')
  .replace('const DEFAULT_PROCESS_MEMORY_LIMIT_BYTES = process.constrainedMemory();\n', '');
const marker = '//#region src/logging/diagnostic-memory.ts';
function verify(text) {
  const start = text.indexOf(marker);
  assert(start >= 0);
  const section = text.slice(start + marker.length, text.indexOf('//#endregion', start));
  let limit = 3 * 1024 ** 3, events = [], retired = 0;
  const context = { process: {constrainedMemory: () => limit, versions: {}, uptime: () => 1},
    getHeapStatistics: () => ({heap_size_limit: 2 * 1024 ** 3}), getHeapSpaceStatistics: () => [], totalmem: () => 32 * 1024 ** 3,
    createSubsystemLogger: () => ({child: () => ({warn() {}, error() {}})}),
    sampleTrackedWorkerMemory: () => ({}), emitInternalDiagnosticEvent: e => events.push(e),
    channel: () => ({publish: () => retired++}) };
  vm.createContext(context); vm.runInContext(section, context);
  function sample(rss) {
    events = []; retired = 0;
    context.testMemory = {rss: rss * 1024 ** 3, heapTotal: 700 * 1024 ** 2, heapUsed: 500 * 1024 ** 2, external: 0, arrayBuffers: 0};
    vm.runInContext('resetDiagnosticMemoryForTest(); emitDiagnosticMemorySample({now:1000,memoryUsage:testMemory})', context);
    return {level: events.find(e => e.type === 'diagnostic.memory.pressure')?.level, retired};
  }
  const initial = sample(2.8); limit = 5 * 1024 ** 3;
  const raised = sample(2.8), high = sample(4.6); limit = 2 * 1024 ** 3;
  return {initial, raised, high, lowered: sample(1.9)};
}
const before = verify(source), after = verify(patched);
assert.equal(before.raised.level, 'critical');
assert.equal(after.raised.level, undefined);
assert.equal(after.raised.retired, 0);
assert.equal(after.initial.retired, 1);
assert.equal(after.high.retired, 1);
assert.equal(after.lowered.retired, 1);
fs.writeFileSync(path, patched);
console.log(JSON.stringify({before, after, assertions: 6,
  beforeHash: crypto.createHash('sha256').update(source).digest('hex'),
  afterHash: crypto.createHash('sha256').update(patched).digest('hex')}));
