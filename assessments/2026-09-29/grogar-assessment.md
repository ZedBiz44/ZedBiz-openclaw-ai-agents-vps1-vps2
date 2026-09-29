# Grogar AGENTS.md Cleanup Assessment

## Target

- Agent: Grogar
- Server and runtime: VPS1 Docker
- OpenClaw version: 2026.9.4
- Operator: Cody
- Requested mode: Get-er-Done; approved rollout after Amanda canary

## Sources Checked

- Live baseline SHA-256: 45c9c59f853d2e53e5ed6dc6b7fa68b6712f0121c6a586e9185ca4ab0225b3cd
- GitHub main baseline: 7e5b4daac5b62f4ff2141f259000a869283e3073
- Live file, core workspace files, recognized bootstrap files, relevant runtime settings, official OpenClaw documentation, and the Z OpenClaw AGENTS.md Manager procedure

## Size and Injection

| Version | Bytes | OpenClaw characters | Lines | Per-file limit | Result |
|---|---:|---:|---:|---:|---|
| Live baseline | 15,306 | 15,302 | 139 | 20,000 | Above 15,000-character cleanup threshold |
| Candidate | 12,504 | 12,502 | 127 | 20,000 | Within recommended range |

- Candidate SHA-256: 68f43d32251233e0d671e6f0bea0521c5fb5604132a497689d85b480033d4644

## Findings and Decisions

- Important September memory, journal, technical-record, email, and unlimited-work additions were preserved.
- Critical role, authority, approval, and continuity rules remain or moved earlier.
- Repeated source, memory, Notion, communication, verification, and maintenance wording was merged.
- Agent-specific safeguards preserved: Growth Garage role, role approvals, source routing, operating discipline, Notion/Wiki standards, Asana identity, and Hindsight exact facts.
- Empty headings and non-operative filler were retired. No role, approval gate, source owner, memory safeguard, or email safeguard was retired.

## Deployment Plan

- Commit the exact candidate, register, and assessment before production.
- Re-read the live baseline hash and create an external timestamped backup.
- Deploy only after Amanda's canary passes. Preserve existing owner and mode.
- Start a fresh session and test role, Diagnose boundary, one approval gate, one source route, the agent-specific safeguard, the Asana email negative case, unlimited work, and final instruction preservation.
- Confirm live hash, health, restart count, context evidence, and no unintended external actions.
- Roll back immediately if a critical test fails.

## Deployment and Verification Result

- Deployed live with exact candidate hash `68f43d32251233e0d671e6f0bea0521c5fb5604132a497689d85b480033d4644`.
- External backup: `/home/jackadmin/openclaw-agent-backups/grogar/20260929T203808Z/AGENTS.md`.
- Ownership and mode remained `node:node`, `0644`; the container stayed healthy with zero restarts.
- Fresh session `grogar-agents-cleanup-validation-20260929-203943-100802` passed role/reporting, Diagnose boundary, external-publication and module approval gates, source routing, continuity, unlimited-work, and size-only deletion tests.
- No validation tools or external actions ran. Native injection metadata did not expose `rawChars`; live JavaScript UTF-16 count was 12,502 and tail behavior passed.
- Rollback was not required.
