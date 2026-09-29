# Terry AGENTS.md Cleanup Assessment

## Target

- Agent: Terry
- Server and runtime: VPS1, Docker-isolated OpenClaw
- OpenClaw version: 2026.9.4
- Workspace: /home/node/.openclaw/workspace
- Operator: Cody
- Requested mode: Get-er-Done, candidate plus approved live pilot

## Sources Checked

- Live file SHA-256: 37c7c819f5ecab51a13ea28140ebae3825dbbbd7fc0895097a9edd60944f7011
- GitHub main baseline: 2182823e4d903b10ff1c5e4047db254377f79ead
- Core workspace files, runtime health, bootstrap limits, recognized files, and official OpenClaw references
- Z OpenClaw AGENTS.md Manager standard and deployment procedure

## Size and Injection

| Version | Bytes | OpenClaw characters | Lines | Per-file limit | Result |
|---|---:|---:|---:|---:|---|
| Live baseline | 20,002 | 19,994 | 203 | 20,000 | Six characters of headroom |
| Candidate | 13,997 | 13,997 | 143 | 20,000 | Within target range |

- Candidate SHA-256: eaf30c7d75e09eecdfc642a1e44362d34449626eb857388488c2c97d77a6fe28

## Findings and Decisions

- Important September additions were preserved: memory retention, daily journals, Notion routing, technical-record limits, and unlimited work.
- Critical authority, safety, mode, and unlimited-work rules moved earlier.
- Repeated source, memory, journal, communication, verification, and completion wording was merged.
- Two empty headings were retired.
- Legacy TOOLS.md remains an on-demand reference, but the candidate no longer claims arbitrary referenced files are automatically loaded.
- No role, approval gate, sender rule, source owner, memory privacy rule, or Terry-specific testing safeguard was retired.

## Deployment Plan

- Commit the candidate, register, and assessment before production.
- Re-read the live baseline hash.
- Create an external timestamped backup.
- Deploy Terry only and preserve node:node ownership and mode 0644.
- Start a fresh session and test role, Diagnose boundary, source routing, testing safeguard, email negative case, and final maintenance rule.
- Roll back immediately if the candidate hash, health, injection, or behavior tests fail.

## Fresh-Session Result

- Deployed candidate hash matched exactly; owner node:node and mode 0644 were preserved.
- External backup: /home/jackadmin/openclaw-agent-backups/terry/20260929T195858Z/AGENTS.md
- Fresh session: terry-agents-validation-20260929-1959
- Terry correctly stated role and reporting line, kept Diagnose work read-only, routed technical records to GitHub and SOPs/prompts to Notion, rejected a reminder email as a work trigger, distinguished discovery from execution, continued healthy long work, and refused size-only instruction deletion.
- No validation tools or external actions ran. Runtime stayed running and healthy with zero restarts.
- Native injection metadata did not report an injected character count for AGENTS.md; it reported rawChars 13,996 and native_unverified. Successful behavior on the final maintenance rule is practical tail evidence, not a claim of complete injection metadata.
- Rollback was not required.
