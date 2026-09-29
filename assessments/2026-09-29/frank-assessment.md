# Frank AGENTS.md Cleanup Assessment

## Target

- Agent: Frank
- Server and runtime: VPS2 systemd
- OpenClaw version: 2026.9.4
- Operator: Cody
- Requested mode: Get-er-Done; approved rollout after Amanda canary

## Sources Checked

- Live baseline SHA-256: 6d7ca5d8789f6958ad07d799e79254d679edcbae8387c697cb6f1f20eaac0b5f
- GitHub main baseline: 7e5b4daac5b62f4ff2141f259000a869283e3073
- Live file, core workspace files, recognized bootstrap files, relevant runtime settings, official OpenClaw documentation, and the Z OpenClaw AGENTS.md Manager procedure

## Size and Injection

| Version | Bytes | OpenClaw characters | Lines | Per-file limit | Result |
|---|---:|---:|---:|---:|---|
| Live baseline | 18,515 | 18,503 | 207 | 24,000 | Above 15,000-character cleanup threshold |
| Candidate | 11,862 | 11,856 | 128 | 24,000 | Within recommended range |

- Candidate SHA-256: ecabe33eda7cebd280399a3adc3448c20541e5e1c4659ea474b2c6e509949545

## Findings and Decisions

- Important September memory, journal, technical-record, email, and unlimited-work additions were preserved.
- Critical role, authority, approval, and continuity rules remain or moved earlier.
- Repeated source, memory, Notion, communication, verification, and maintenance wording was merged.
- Agent-specific safeguards preserved: Deal qualification and economics, due diligence labels, non-binding negotiation authority, conflict checks, pipeline stages, specialist handoffs, and automatic durable knowledge capture.
- Empty headings and non-operative filler were retired. No role, approval gate, source owner, memory safeguard, or email safeguard was retired.

## Deployment Plan

- Commit the exact candidate, register, and assessment before production.
- Re-read the live baseline hash and create an external timestamped backup.
- Deploy only after Amanda's canary passes. Preserve existing owner and mode.
- Start a fresh session and test role, Diagnose boundary, one approval gate, one source route, the agent-specific safeguard, the Asana email negative case, unlimited work, and final instruction preservation.
- Confirm live hash, health, restart count, context evidence, and no unintended external actions.
- Roll back immediately if a critical test fails.

## Deployment and Verification Result

- Deployed live with exact candidate hash `ecabe33eda7cebd280399a3adc3448c20541e5e1c4659ea474b2c6e509949545`.
- External backup: `/root/openclaw-agent-backups/frank/20260929T203800Z/AGENTS.md`.
- Ownership and mode remained `root:root`, `0644`; the systemd service stayed active with zero restarts.
- Fresh session `frank-agents-cleanup-validation-20260929-203943-1398205` passed Deal Specialist role, Diagnose boundary, non-binding proposed terms, `Counterparty Claim` labeling with source/date, source routing, continuity, unlimited-work, and size-only deletion tests.
- No validation tools or external actions ran. Native injection metadata did not expose `rawChars`; live JavaScript UTF-16 count was 11,856 and tail behavior passed.
- Rollback was not required.
