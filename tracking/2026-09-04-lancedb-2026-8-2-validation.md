# LanceDB 2026.8.2 Fleet Validation — 2026-09-04

## Scope

Amanda, Victor, Vivian, and Wilma on VPS1. Amanda was the canary. This record closes issue #251.

## Approved Fleet Standard

- Active memory slot: `memory-lancedb`
- Independent store: `/opt/openclaw/shared/external-memory/lancedb/{agent}`
- `autoRecall=true`
- `autoCapture=false`
- `captureMaxChars=800`
- `recallMaxChars=1000`
- OpenAI `text-embedding-3-small`
- API key supplied by reference, never as a literal
- `hooks.allowConversationAccess=true`
- OpenClaw and `@openclaw/memory-lancedb` version: `2026.8.2`

## Why autoCapture Is Off

The 2026-08-05 safety benchmark proved that automatic capture could store whole prompts, including fake-secret and raw-log markers. The approved design is deliberate compact capture through `memory_store`, followed by a verified recall check.

## 2026-09-04 Results

Amanda passed first. Victor, Vivian, and Wilma then passed the same checks.

- Explicit store: pass
- Exact semantic search: pass; intended record ranked first
- Paraphrased fresh-session recall: pass
- Authoritative pointer returned: pass
- Unsafe prompt marker absent from stored memory: pass
- Cross-agent isolation: pass
- Amanda stale-fact replacement: pass
- Synthetic-record cleanup and absence recheck: pass
- Configuration validation and container health: pass
- Direct exact-search scores: Amanda 0.6307, Victor 0.6017, Vivian 0.6302, Wilma 0.6191
- Observed direct-search time including the remote command path: roughly 8–9 seconds

## Codex Runtime Finding And Mitigation

On the OpenClaw 2026.8.2 Codex agent harness, `autoRecall=true` did not reliably inject LanceDB results and the direct `memory_recall` surface was unavailable. The database and plugin search worked.

The four agents' live `AGENTS.md` files now require `gateway_exec` with:

`openclaw ltm search "<short task query>" --limit 5`

before answering about a prior status, decision, approval, preference, previous work, or named ongoing item. Fresh user-level tests passed on all four agents after this change. Each original file is backed up as `AGENTS.md.bak-20260904-lancedb`.

## Known Non-Fatal Warning

A dormant `memory-core` configuration remains present while the memory slot selects `memory-lancedb`. OpenClaw reports this as a warning. It does not change the active provider. The entry also contains separate dreaming configuration and was not deleted merely to silence the warning.

## Acceptance Test After Upgrades

- Validate the configuration and provider version.
- Store one harmless, uniquely marked memory with a fact and authoritative pointer.
- Search by exact marker and paraphrase.
- Ask the agent in a fresh session without giving it the marker.
- Confirm unsafe text present only in the prompt was not captured.
- Confirm a different LanceDB agent cannot retrieve the marker.
- Replace a stale test fact and confirm only the replacement returns.
- Remove every test record with `memory_forget` and verify marker absence.
- Record scores, elapsed time, route, version, cleanup proof, and any limitation.

Optimal means the memory reaches the agent when needed, remains private to that agent, excludes unsafe prompt text, can be updated, and leaves no test debris.
