# Harry AGENTS.md Cleanup Assessment

## Target

- Agent: Harry
- Server and runtime: VPS2 systemd
- OpenClaw version: 2026.9.4
- Operator: Cody
- Requested mode: Get-er-Done; approved rollout after Amanda canary

## Sources Checked

- Live baseline SHA-256: ac5a501abfe896027d859526249d446cca007a6ff50eca72800e60a3fc7f8c0b
- GitHub main baseline: 7e5b4daac5b62f4ff2141f259000a869283e3073
- Live file, core workspace files, recognized bootstrap files, relevant runtime settings, official OpenClaw documentation, and the Z OpenClaw AGENTS.md Manager procedure

## Size and Injection

| Version | Bytes | OpenClaw characters | Lines | Per-file limit | Result |
|---|---:|---:|---:|---:|---|
| Live baseline | 17,558 | 17,556 | 161 | 24,000 | Above 15,000-character cleanup threshold |
| Candidate | 13,222 | 13,220 | 130 | 24,000 | Within recommended range |

- Candidate SHA-256: 4cac99f67a420c4de04745282032083ab0c41aff7f039ad6b7bb04ea2e7d19b3

## Findings and Decisions

- Important September memory, journal, technical-record, email, and unlimited-work additions were preserved.
- Critical role, authority, approval, and continuity rules remain or moved earlier.
- Repeated source, memory, Notion, communication, verification, and maintenance wording was merged.
- Agent-specific safeguards preserved: Business-generalist role, Jack profile workaround while USER.md auto-loading is impaired, dual Codex/native Notion routes, mandatory knowledge capture, client approval gates, and owning-record completion.
- Empty headings and non-operative filler were retired. No role, approval gate, source owner, memory safeguard, or email safeguard was retired.

## Deployment Plan

- Commit the exact candidate, register, and assessment before production.
- Re-read the live baseline hash and create an external timestamped backup.
- Deploy only after Amanda's canary passes. Preserve existing owner and mode.
- Start a fresh session and test role, Diagnose boundary, one approval gate, one source route, the agent-specific safeguard, the Asana email negative case, unlimited work, and final instruction preservation.
- Confirm live hash, health, restart count, context evidence, and no unintended external actions.
- Roll back immediately if a critical test fails.

## Deployment and Verification Result

- Deployed live with exact candidate hash `4cac99f67a420c4de04745282032083ab0c41aff7f039ad6b7bb04ea2e7d19b3`.
- External backup: `/root/openclaw-agent-backups/harry/20260929T203800Z/AGENTS.md`.
- Ownership and mode remained `root:root`, `0644`; the systemd service stayed active with zero restarts.
- Fresh session `harry-agents-cleanup-validation-20260929-203943-1398206` passed generalist role, Diagnose boundary, Notion record plus Wiki mirror plus durable-facts workflow, bundled Notion/`ntn` routing outside Codex, continuity, unlimited-work, and size-only deletion tests.
- No validation tools or external actions ran. Native injection metadata did not expose `rawChars`; live JavaScript UTF-16 count was 13,220 and tail behavior passed.
- Rollback was not required.
