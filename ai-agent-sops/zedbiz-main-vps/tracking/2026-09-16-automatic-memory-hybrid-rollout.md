# Automatic Memory And Hybrid Rollout

Date: 2026-09-16 MDT | Owner: Cody | Status: Implemented and live-verified

## Approved Standard

- External providers use automatic capture or retain and automatic recall when supported.
- Useful context from reviews, research, audits, diagnosis, planning, and ordinary questions may be remembered.
- Memory capture does not authorize publication or changes to authoritative records.
- Credentials, secrets, raw private logs, full documents, unsupported guesses, and needless duplicate chatter remain excluded.

## Live Changes

- Mem0: Terry, Edith, and Harry run Mem0 1.1.0, Qdrant JS 1.18.0, automatic capture and recall, and no skills/triage block. Standard workspace memory and native Dreaming remain available as the local sidecar while Mem0 owns conversational recall.
- LanceDB: Amanda, Victor, Vivian, and Wilma have `autoCapture=true` and `autoRecall=true` in independent stores.
- Central Hindsight: Marsha, Maggie, Inga, GohZed, Grogar, Frank, Suzy, and Ruby have automatic retain/capture and recall. Ruby's Hermes configuration has memory enabled, Hindsight selected, and write approval disabled.
- Rocky: upgraded the separate VPS4 Hindsight API from 0.9.1 to 0.10.0. PostgreSQL 18.6, connector 0.12.0, crash-safe writes, encrypted backup, gateway restart, and the recurring health timer were preserved and verified.
- Core instructions now name the active provider near the top so the rule remains inside the bootstrap context budget.

## Verification

- Automatic capture does not preserve every message verbatim. It extracts useful context, and recall across channels requires both routes to resolve to the same provider store, identity, and bank or collection scope.
- Configuration verifier passed for every OpenClaw provider agent on VPS1, VPS2, and VPS4.
- Ruby's Hermes settings and early Hindsight instruction were read back.
- Rocky's API, database, gateway, and timer were healthy after restart. Rocky correctly named Hindsight and confirmed useful Notion-review context may be remembered.
- Cross-context marker tests passed for Harry/Mem0, Amanda/LanceDB, and Marsha/fixed-bank Hindsight using separate Discord-labelled and Web-style sessions.
- Rocky passed the same CLI test only because both CLI sessions resolved to the same bank. Real Discord and Web UI routes use dynamic channel/user banks, so true cross-channel continuity is not guaranteed for Rocky without an approved identity or bank-scope change.

## Rocky 0.10 Health-Check Repair

Hindsight 0.10 requires the existing bank IDs to be URL-encoded before requesting bank statistics. The health script now encodes each bank ID, checks API and database health, verifies crash-safe PostgreSQL settings, fails on consolidation errors, and reports queued plus historical failed operations without treating old per-bank counters as a new outage.

## Rollback

- Timestamped configuration and instruction backups were created before each alignment run.
- Rocky's pre-upgrade Compose file and encrypted database backup remain on VPS4.
- The prior Hindsight image digest can be restored with the preserved Compose and backup if required.

