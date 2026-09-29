# Amanda AGENTS.md Cleanup Assessment

## Target

- Agent: Amanda
- Server and runtime: VPS1, Docker-isolated OpenClaw
- OpenClaw version: 2026.9.4
- Workspace: /home/node/.openclaw/workspace
- Operator: Cody
- Requested mode: Get-er-Done; approved canary for agents above 15,000 characters

## Sources Checked

- Live baseline SHA-256: b38192f55070f49e3f0a27c523f4780903dba9fe1337d14ebc3f576bbf3133c5
- GitHub main baseline: 7e5b4daac5b62f4ff2141f259000a869283e3073
- Core workspace files, recognized bootstrap files, runtime health, bootstrap settings, official OpenClaw documentation, and the Z OpenClaw AGENTS.md Manager procedure

## Size and Injection

| Version | Bytes | OpenClaw characters | Lines | Per-file limit | Result |
|---|---:|---:|---:|---:|---|
| Live baseline | 19,983 | 19,973 | 218 | 20,000 | 27 characters of headroom |
| Candidate | 13,972 | 13,972 | 130 | 20,000 | Within recommended range |

- Candidate SHA-256: a06fd9ac4d1b7c373dfc8835c25af42eb64442912ff4b10ad56a7c28eb8a23e7

## Findings and Decisions

- The file was at immediate truncation risk.
- September additions for LanceDB retention, daily journals, technical-record limits, collection coordination, and unlimited work are intentional and preserved.
- Critical authority, operating modes, and continuity rules moved near the beginning.
- Repeated source, tool, memory, Notion, communication, verification, and maintenance wording was merged.
- Amanda's unusual collection-completion email authority, both collection IDs, server-group release rule, blocker isolation, and Mary exception remain.
- One empty heading was retired. No role, approval gate, source owner, memory safeguard, or email safeguard was retired.

## Deployment Plan

- Commit the exact candidate, register, and assessment before production.
- Re-read the live baseline hash and create an external timestamped backup.
- Deploy Amanda only, preserving node:node ownership and mode 0644.
- Start a fresh session and test role, Diagnose boundary, Asana identity, broad-change approval, collection coordination, memory proof, unlimited work, and the final preservation rule.
- Confirm hash, health, restart count, context evidence, and no unintended external actions.
- Roll back immediately if any critical test fails. Scale only after Amanda passes.
