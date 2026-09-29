# GohZed AGENTS.md Cleanup Assessment

## Target

- Agent: GohZed
- Server and runtime: VPS1 Docker
- OpenClaw version: 2026.9.4
- Operator: Cody
- Requested mode: Get-er-Done; approved rollout after Amanda canary

## Sources Checked

- Live baseline SHA-256: 3dd8cbb641a1b8d61416f20bed2a1f285a176a5a35b5f56d0a550dd3b76c0982
- GitHub main baseline: 7e5b4daac5b62f4ff2141f259000a869283e3073
- Live file, core workspace files, recognized bootstrap files, relevant runtime settings, official OpenClaw documentation, and the Z OpenClaw AGENTS.md Manager procedure

## Size and Injection

| Version | Bytes | OpenClaw characters | Lines | Per-file limit | Result |
|---|---:|---:|---:|---:|---|
| Live baseline | 16,389 | 16,375 | 158 | 20,000 | Above 15,000-character cleanup threshold |
| Candidate | 13,927 | 13,915 | 148 | 20,000 | Within recommended range |

- Candidate SHA-256: 9f7c135678f1a09d12a2a9c1b63cc47d6dda2f4d66979a2ff8a47f10eefcbdfd

## Findings and Decisions

- Important September memory, journal, technical-record, email, and unlimited-work additions were preserved.
- Critical role, authority, approval, and continuity rules remain or moved earlier.
- Repeated source, memory, Notion, communication, verification, and maintenance wording was merged.
- Agent-specific safeguards preserved: GoHighLevel ownership, approval gates, credential routing, heartbeats, Asana identity, Hindsight exact facts, and GHL completion rules.
- Empty headings and non-operative filler were retired. No role, approval gate, source owner, memory safeguard, or email safeguard was retired.

## Deployment Plan

- Commit the exact candidate, register, and assessment before production.
- Re-read the live baseline hash and create an external timestamped backup.
- Deploy only after Amanda's canary passes. Preserve existing owner and mode.
- Start a fresh session and test role, Diagnose boundary, one approval gate, one source route, the agent-specific safeguard, the Asana email negative case, unlimited work, and final instruction preservation.
- Confirm live hash, health, restart count, context evidence, and no unintended external actions.
- Roll back immediately if a critical test fails.

## Deployment and Verification Result

- Deployed live with exact candidate hash `9f7c135678f1a09d12a2a9c1b63cc47d6dda2f4d66979a2ff8a47f10eefcbdfd`.
- External backup: `/home/jackadmin/openclaw-agent-backups/gohzed/20260929T203808Z/AGENTS.md`.
- Ownership and mode remained `node:node`, `0644`; the container stayed healthy with zero restarts.
- Fresh session `gohzed-agents-cleanup-validation-20260929-203943-100801` passed role/reporting, Diagnose boundary, GitHub/Notion routing, assignment-start boundary, healthy-work continuation, size-only deletion refusal, GoHighLevel ownership, and production/client approval tests.
- No validation tools or external actions ran. Native injection metadata did not expose `rawChars`; live JavaScript UTF-16 count was 13,915 and tail behavior passed.
- Rollback was not required.
