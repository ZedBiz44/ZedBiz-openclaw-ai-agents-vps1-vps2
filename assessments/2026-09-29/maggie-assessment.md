# Maggie AGENTS.md Cleanup Assessment

## Target

- Agent: Maggie
- Server and runtime: VPS1 Docker
- OpenClaw version: 2026.9.4
- Operator: Cody
- Requested mode: Get-er-Done; approved rollout after Amanda canary

## Sources Checked

- Live baseline SHA-256: 80dd691989c68d3429ade9adf69ce17df5011a08fcc9b2c883ebfddde0d7017a
- GitHub main baseline: 7e5b4daac5b62f4ff2141f259000a869283e3073
- Live file, core workspace files, recognized bootstrap files, relevant runtime settings, official OpenClaw documentation, and the Z OpenClaw AGENTS.md Manager procedure

## Size and Injection

| Version | Bytes | OpenClaw characters | Lines | Per-file limit | Result |
|---|---:|---:|---:|---:|---|
| Live baseline | 17,435 | 17,425 | 204 | 20,000 | Above 15,000-character cleanup threshold |
| Candidate | 13,283 | 13,281 | 147 | 20,000 | Within recommended range |

- Candidate SHA-256: 2b6b8a5143ffdd55c5a79ff77c0c0aeb19fd1bc8e3701e9d07aa965e6488a4f0

## Findings and Decisions

- Important September memory, journal, technical-record, email, and unlimited-work additions were preserved.
- Critical role, authority, approval, and continuity rules remain or moved earlier.
- Repeated source, memory, Notion, communication, verification, and maintenance wording was merged.
- Agent-specific safeguards preserved: Brand voice and copy ownership, external-copy approvals, Hindsight lookup and exact facts, runtime routes, email commands, Asana identity, and brand-guide requirement.
- Empty headings and non-operative filler were retired. No role, approval gate, source owner, memory safeguard, or email safeguard was retired.

## Deployment Plan

- Commit the exact candidate, register, and assessment before production.
- Re-read the live baseline hash and create an external timestamped backup.
- Deploy only after Amanda's canary passes. Preserve existing owner and mode.
- Start a fresh session and test role, Diagnose boundary, one approval gate, one source route, the agent-specific safeguard, the Asana email negative case, unlimited work, and final instruction preservation.
- Confirm live hash, health, restart count, context evidence, and no unintended external actions.
- Roll back immediately if a critical test fails.

## Deployment and Verification Result

- Deployed live with exact candidate hash `2b6b8a5143ffdd55c5a79ff77c0c0aeb19fd1bc8e3701e9d07aa965e6488a4f0`.
- External backup: `/home/jackadmin/openclaw-agent-backups/maggie/20260929T203808Z/AGENTS.md`.
- Ownership and mode remained `node:node`, `0644`; the container stayed healthy with zero restarts.
- Fresh session `maggie-agents-cleanup-validation-20260929-203943-100803` passed role/reporting, Diagnose boundary, paid-ad platform/audience/budget and approval requirements, source routing, continuity, unlimited-work, and size-only deletion tests.
- No validation tools or external actions ran. Native injection metadata did not expose `rawChars`; live JavaScript UTF-16 count was 13,281 and tail behavior passed.
- Rollback was not required.
