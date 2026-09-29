# Rocky AGENTS.md Cleanup Assessment

## Target

- Agent: Rocky
- Server and runtime: VPS4 native systemd
- OpenClaw version: 2026.9.5
- Operator: Cody
- Requested mode: Get-er-Done; approved rollout after Amanda canary

## Sources Checked

- Live baseline SHA-256: 7ad86f4095258918a8b3cfbc71ee881e19829a87cb96454edcdeb7d9b155a225
- GitHub main baseline: 7e5b4daac5b62f4ff2141f259000a869283e3073
- Live file, core workspace files, recognized bootstrap files, relevant runtime settings, official OpenClaw documentation, and the Z OpenClaw AGENTS.md Manager procedure

## Size and Injection

| Version | Bytes | OpenClaw characters | Lines | Per-file limit | Result |
|---|---:|---:|---:|---:|---|
| Live baseline | 17,681 | 17,679 | 146 | 20,000 | Above 15,000-character cleanup threshold |
| Candidate | 13,463 | 13,463 | 125 | 20,000 | Within recommended range |

- Candidate SHA-256: 64768b0fb60720dfa1ad64ffaf27bdffb2e3f5d2eed4744a56dc83bf94d639ae

## Findings and Decisions

- Important September memory, journal, technical-record, email, and unlimited-work additions were preserved.
- Critical role, authority, approval, and continuity rules remain or moved earlier.
- Repeated source, memory, Notion, communication, verification, and maintenance wording was merged.
- Agent-specific safeguards preserved: VA mentoring, Asana ownership handoff, real media generation, exact xAI video model, Percify route, screenshot helper, private Discord response rule, personal versus shared Wiki, and 1Password-only secrets.
- Empty headings and non-operative filler were retired. No role, approval gate, source owner, memory safeguard, or email safeguard was retired.

## Deployment Plan

- Commit the exact candidate, register, and assessment before production.
- Re-read the live baseline hash and create an external timestamped backup.
- Deploy only after Amanda's canary passes. Preserve existing owner and mode.
- Start a fresh session and test role, Diagnose boundary, one approval gate, one source route, the agent-specific safeguard, the Asana email negative case, unlimited work, and final instruction preservation.
- Confirm live hash, health, restart count, context evidence, and no unintended external actions.
- Roll back immediately if a critical test fails.
