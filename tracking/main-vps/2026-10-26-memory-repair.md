# Memory repair — October 26, 2026

Owner: Cody. Authorized by Jack: “get the memory stuff fixed ASAP.” Times are Mountain Time. Workstream: [issue 498](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/498).

## Confirmed fix: false Mem0 timeout warnings

The installed Mem0 1.2.1 auto-recall hook raced search against an eight-second timer but never cancelled the losing timer. The timer's `.then()` logged a timeout even after a successful search or an immediate search error. The original Edith, Terry, and Harry warnings therefore did not prove that recall failed.

The fix logs only when the timer wins and clears the timer in `finally`. The eight-second deadline, search settings, memory stores, and helper models remain unchanged.

- Terry was the first pilot. The deployed hook passed fast success, immediate error, and genuine timeout tests. After an idle-checked restart, his gateway was healthy, all schedule definitions were unchanged, automatic recall injected five memories, and a nondelivering model turn successfully used `mem0_search` and `mem0_get`.
- Edith received the same fix after Terry passed. Her startup checks, schedule comparison, automatic recall (three memories), and live search/get passed.
- Harry received the same fix on VPS2. His existing HTTPS correction passed its guard. His configuration hash and schedule definitions were unchanged; automatic recall injected two memories and live search/get passed.
- Complete logs, including stderr, contained no false recall timeout for these acceptance turns after the eight-second deadline.
- All live tests used the existing model, `gpt-6.1-sol`, without fallback or rerouting.

The source-extracted regression test reproduces the original false warnings in baseline mode and verifies all three outcomes with the patched hook. It runs against the actual installed hook, with provider calls mocked and the timer shortened solely in the test.

### Deployed files and persistence

On Terry and Edith:

- Managed Mem0 `dist/index.js` under `/home/node/.openclaw/npm/projects/mem0-openclaw-mem0-09729737ad__openclaw-generation__g-1e5cd6aa3ff70dae/node_modules/@mem0/openclaw-mem0/`.
- `/home/node/.openclaw/scripts/repair-mem0-recall-timer.cjs`.
- `/home/node/.openclaw/scripts/verify-mem0-sdk331.cjs`: updated only the expected plugin source hash.
- `/home/node/.openclaw/workspace/ensure-mem0-compat.sh`: applies the idempotent repair before the existing source/dependency guard.

On Harry, the same managed package lives under `/root/.openclaw-harry/npm/projects/`. The persistent repair, source verifier, and startup hook are under `/opt/openclaw-harry/`, with startup hook `ensure-mem0-110-compat.sh`.

Original plugin SHA-256: `0e7205db54c8790c1aff7b09786ec0b7578db08181b5394a7137df4e530297c2`.

Patched plugin SHA-256: `7d1482d6a79bdd2e1ac69e0ea6f26736d8ccfd3c0780b1cc786c3f0c9c7066c9`.

The vendor archive and dependency lock remain unchanged. Startup reapplies the reviewed source patch before checking its resulting hash; all dependency checks remain active.

### Verification and rollback

Commands used included `node repair-mem0-recall-timer.cjs <installed-index.js>`, `node test-mem0-recall-timer.cjs <installed-index.js>`, each existing startup compatibility guard, gateway `status`, `health`, `cron.list`, nondelivering `agent` requests, and complete service logs.

Original index, verifier, and startup script were backed up in `/home/node/.openclaw/backups/memory-timer-20261026/` on Terry and Edith. Harry's backups are `/root/cody-memory-repair-20261026/{index.js,verify-mem0-sdk331.cjs,ensure-mem0-110-compat.sh}.before`. To roll back, first confirm the agent is idle, restore those three matching files together, verify the original hash and startup checks, then restart that one agent. Do not restore memory databases or alter schedules.

Minor execution snags: the first local patch attempt encountered CRLF line endings; normalization fixed matching. The first pilot launcher used the Docker environment option after the container name; corrected before mutation. Its next attempt lacked permission to copy into the scripts directory; narrow root execution fixed that. These attempts made no partial plugin changes. Existing startup guards include an exact plugin hash, so the reviewed new hash and persistent patch hook were deployed together before restart.

## Hindsight: read/write working, original cause unresolved

Gohzed, Grogar, and Maggie originally returned `Session delivery generation is unavailable; retry after session storage is ready.` for manual Hindsight tools. Automatic Hindsight context injection worked during those original runs. Inspection located this error in OpenClaw's session-generation checks, before the plugin's normal memory operation; the precise invalidating event was not captured.

- Gohzed passed fresh nondelivering probes in his original Discord session before a restart, including concurrent Wiki and Hindsight reads.
- After an idle-checked restart, Gohzed again passed the original combination of skill read, Notion fetch, concurrent `memory_search`/`hindsight_recall`, and a second Hindsight recall. His schedule definitions were unchanged.
- All three agents then passed concurrent Wiki/Hindsight reads and `hindsight_retain` in their original sessions. The retain response reports queued storage, so that response alone was not treated as durable success.
- Separate subsequent Hindsight recall calls found the actual operational note about issue 498 and independently verifying Notion writes versus memory errors on all three. HTTP responses were successful and the tools reported no errors.
- Grogar and Maggie did not require restarts or configuration changes. No session-generation guard was weakened, bypassed, or patched.

These checks establish current working read/write behavior. They do **not** establish a permanent fix for the earlier intermittent session rejection. Issue 498 remains open for that unresolved cause; the Mem0 timer correction must not be presented as fixing Hindsight.

### Acceptance run identifiers

| Agent | Successful run |
|---|---|
| Terry | `cody-terry-timer-20261026` |
| Edith | `cody-edith-timer-20261026` |
| Harry | `cody-harry-timer-20261026` |
| Gohzed | `cody-gohzed-fresh-memory-20261026`, `cody-gohzed-memory-retain-20261026` |
| Grogar | `cody-grogar-memory-retain-20261026` |
| Maggie | `cody-maggie-memory-retain-20261026` |

Private run receipts and logs remain on VPS1 under `/home/jackadmin/cody-memory-repair-20261026/` and VPS2 under `/root/cody-memory-repair-20261026/`. They are not committed because full model receipts can contain private context. The daily Cody Tech Updates journal links this workstream.

