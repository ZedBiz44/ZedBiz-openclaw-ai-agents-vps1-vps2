# Wilma AGENTS.md Instruction Preservation Register

Date: 2026-09-02 | Agent: Cody | Status: Deployed and verified after Amanda gate

## Baseline

- Live file: `/opt/openclaw/agents/wilma/workspace/AGENTS.md`
- Runtime workspace: `/home/node/.openclaw/workspace`
- Baseline SHA-256: `efb735c6ecd6d70db0e7b346ab43b0d9ab54cb48c510a1961a553c24021c164b`
- Baseline size: 13,144 bytes / 140 lines
- Runtime: healthy on `ghcr.io/zedbiz44/openclaw-base:2026.8.2`
- Verified configuration: GPT-5.6 Sol primary; configured fallbacks; `asana` and `wordpress-allzed` MCPs; LanceDB; Discord and Telegram.

## Disposition Standard

- Retain: keep the governing rule in `AGENTS.md`.
- Compress: preserve the behavior with shorter wording.
- Relocate: keep the trigger or boundary here; details stay in the owning file, Skill, or SOP.
- Merge: consolidate overlapping rules without changing the behavior.
- Retire: remove only when stale, contradictory, unsafe, or misplaced, and record why.

## Preservation Map

| Prior rule or section | Disposition | Destination | Decision |
|---|---|---|---|
| Purpose and core-file ownership | Retain and compress | Purpose and Startup | `WILMA-KEY.md`, `TOOLS.md`, `HEARTBEAT.md`, Skills, and GitHub SOP responsibilities preserved. |
| WordPress role, reporting, and authority | Retain and reorder | Setup and Role | Website revenue responsibility, Jack/Marsha reporting, Amanda handoff, and medium authority moved near the start. |
| WordPress guardrails | Retain and strengthen | WordPress Operating Standards | Exact site/target, read-before-write, smallest change, rollback, structured tools, live verification, SEO, speed, accessibility, tracking, lead path, and plugin-bloat rules preserved. |
| Plugin, theme, menu, structure, deletion, client, and production gates | Retain | Role and Security | Approval boundaries remain explicit and are grouped before implementation guidance. |
| Resident WordPress route | Retain and correct | Setup and Capability | Live `wordpress-allzed` route retained. Other-site access now requires an installed approved route and a scoped call from Wilma; configuration or host-side success is not treated as proof. |
| Get-er-Done and Diagnose | Add explicitly | Operating Modes | Separate triggers, DSCA sequence, low-risk pilot, and new-risk stop gate added. |
| Sources of truth | Retain and merge | Source Of Truth | Live WordPress, GitHub, Notion, Asana, Memory Wiki, LanceDB, and current runtime roles preserved. |
| Durable knowledge capture | Correct and preserve | Scope, Memory, Notion | Authorized publication remains complete and verifiable. Forced writes from review-only, diagnosis-only, incidental facts, or ordinary Q&A are retired as scope conflicts. |
| LanceDB and memory-layer map | Compress | Memory | Provider, supporting-context boundary, recall, compact writes, privacy, promotion, conflict resolution, and verification preserved without the table. |
| Notion standards | Retain and compress | Notion And Z-Knowledge | Approved OAuth route, no raw fallback, live schema, search, canonical update, read-back, routing, and frontmatter preserved. Journal procedure remains in `HEARTBEAT.md`. |
| Asana route and identity | Retain | Skills and Capability | Wilma PAT identity requirement, Jack-connector prohibition, Standard capability, and Advanced-agent boundary preserved; exact IDs remain in `TOOLS.md`. |
| Startup and skill discovery | Retain | Startup | KEY and TOOLS triggers, current context, relevant Skills, small-bite behavior, and browser distinction preserved. |
| Execution, security, and completion | Retain and merge | Execution and Security | Evidence, one-target pilot, live result, rollback, secrecy, outbound scan, accurate blockers, and complete handoff preserved. |
| Assignment continuity and communication | Retain | Communication | Managed acknowledgement, substantive progress, plain business explanation, evidence, and originating-channel handoff preserved. |
| Provider-alignment tail block | Merge | Source and Memory | Active provider, source verification, scope boundary, and compact-pointer behavior preserved without duplication. |

## Critical Coverage Gates

- Identity, website role, reporting, authority, and approval gates: covered.
- Get-er-Done and Diagnose modes: separate and explicit.
- Review-only, diagnosis-only, and no-write boundaries: covered.
- Exact site, target, authorization, rollback, read-before-write, and one-target pilot: covered.
- Plugin, theme, structure, deletion, bulk, client, credential, and production gates: covered.
- `wordpress-allzed` live route and proof-from-Wilma requirement: covered.
- Asana PAT identity, Standard toolset, and Advanced-agent boundary: covered.
- GitHub, Notion, Asana, live WordPress, Memory Wiki, and LanceDB ownership: covered.
- Codex Apps Notion OAuth, live schema, canonical update, and read-back: covered.
- Security, visible verification, rollback, completion, and handoff: covered.

## Planned Pilot Tests

- Fresh session injects the complete file with `truncated=false`.
- Wilma identifies her role, reporting line, and website business purpose.
- Get-er-Done and Diagnose/DSCA remain distinct.
- Review-only work does not authorize implementation, WordPress writes, or durable publishing.
- WordPress work confirms site, target, current content, authorization, rollback, route, and live result.
- Plugin, theme, structure, deletion, client-facing, credential, and production changes stop at the correct gate.
- Wilma distinguishes `wordpress-allzed` from unverified other-site access and proves capability from her runtime.
- Asana uses Wilma's PAT identity and respects the Standard/Advanced boundary.
- Completion reports evidence, rollback, authoritative record when required, and remaining gaps.

## Pilot Result

- Amanda passed every critical gate before Wilma was deployed.
- Deployed SHA-256: `f735583cd39fe450f755e321b5b1932a085644797b126f7730b959d16e5afd94`.
- Deployed size: 13,964 bytes / 189 lines.
- Backup: `/opt/openclaw/agents/wilma/backups/20260902T173328Z-agents-preservation-pilot`.
- Fresh GPT-5.6 Sol/Codex review-only session returned Wilma's identity, reporting, modes, no-write boundary, `wordpress-allzed` route, other-site proof requirement, pre-write checks, WordPress approval gates, Asana Standard/Advanced boundary, governed Notion route, forbidden fallbacks, and completion evidence.
- OpenClaw 2026.8.2 reported `rawChars=13955` and `injectionStatus=native_unverified`; it does not expose `injectedChars` or `truncated` for native AGENTS injection. The session correctly paraphrased the final Maintenance bullet, proving the file tail was available.
- The test used no tools or writes. Post-test hash matched, owner/mode remained `1000:1000` and `0644`, container health was healthy, and restart count remained zero.
