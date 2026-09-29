# Wilma AGENTS.md Cleanup Assessment

## Target

- Agent: Wilma
- Server and runtime: VPS1 Docker
- OpenClaw version: 2026.9.4
- Operator: Cody
- Requested mode: Get-er-Done; approved rollout after Amanda canary

## Sources Checked

- Live baseline SHA-256: fb9eb903bebf476cac0448f58fbe2fb2fc3ca95848eb5400fb8908421b1a7de7
- GitHub main baseline: 7e5b4daac5b62f4ff2141f259000a869283e3073
- Live file, core workspace files, recognized bootstrap files, relevant runtime settings, official OpenClaw documentation, and the Z OpenClaw AGENTS.md Manager procedure

## Size and Injection

| Version | Bytes | OpenClaw characters | Lines | Per-file limit | Result |
|---|---:|---:|---:|---:|---|
| Live baseline | 18,675 | 18,665 | 219 | 20,000 | Above 15,000-character cleanup threshold |
| Candidate | 12,090 | 12,090 | 112 | 20,000 | Within recommended range |

- Candidate SHA-256: 595a2b5e23c43a805b234975f389e8f915e6691f2d8cf901e52e59428c7f0505

## Findings and Decisions

- Important September memory, journal, technical-record, email, and unlimited-work additions were preserved.
- Critical role, authority, approval, and continuity rules remain or moved earlier.
- Repeated source, memory, Notion, communication, verification, and maintenance wording was merged.
- Agent-specific safeguards preserved: WordPress ownership, exact-site scope, plugin and production approval gates, wordpress-allzed routing, SEO/conversion safeguards, Standard Asana limit, and visitor-path verification.
- Empty headings and non-operative filler were retired. No role, approval gate, source owner, memory safeguard, or email safeguard was retired.

## Deployment Plan

- Commit the exact candidate, register, and assessment before production.
- Re-read the live baseline hash and create an external timestamped backup.
- Deploy only after Amanda's canary passes. Preserve existing owner and mode.
- Start a fresh session and test role, Diagnose boundary, one approval gate, one source route, the agent-specific safeguard, the Asana email negative case, unlimited work, and final instruction preservation.
- Confirm live hash, health, restart count, context evidence, and no unintended external actions.
- Roll back immediately if a critical test fails.

## Deployment and Verification Result

- Deployed live with exact candidate hash `595a2b5e23c43a805b234975f389e8f915e6691f2d8cf901e52e59428c7f0505`.
- External backup: `/home/jackadmin/openclaw-agent-backups/wilma/20260929T203808Z/AGENTS.md`.
- Ownership and mode remained `node:node`, `0644`; the container stayed healthy with zero restarts.
- Fresh session `wilma-agents-cleanup-validation-20260929-203943-100806` passed WordPress Specialist role, Diagnose boundary, plugin-install and unassigned-site approval gates, source routing, continuity, unlimited-work, and size-only deletion tests.
- No validation tools or external actions ran. Native injection metadata did not expose `rawChars`; live JavaScript UTF-16 count was 12,090 and tail behavior passed.
- Rollback was not required.
