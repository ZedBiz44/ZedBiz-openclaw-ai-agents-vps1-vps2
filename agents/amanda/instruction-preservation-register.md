# Amanda AGENTS.md Instruction Preservation Register

Date: 2026-09-02 | Agent: Cody | Status: Candidate ready for pilot

## Baseline

- Live file: `/opt/openclaw/agents/amanda/workspace/AGENTS.md`
- Runtime workspace: `/home/node/.openclaw/workspace`
- Baseline SHA-256: `d350f0f249be6329a3a56119ac909ba8ddfe2870a1e4ea4d382d52d3f1d5fbe6`
- Baseline size: 19,786 bytes / 252 lines
- Runtime: healthy on `ghcr.io/zedbiz44/openclaw-base:2026.8.2`
- Verified configuration: GPT-5.6 Sol primary; Terra, Luna, Gemini Flash Lite, and DeepSeek fallbacks; `asana` MCP; LanceDB; Discord and Telegram.
- Structural defect: the prior `TOOLS.md` content was appended under `## Tools`, while no live top-level `TOOLS.md` or `HEARTBEAT.md` existed.

## Disposition Standard

- Retain: keep the governing rule in `AGENTS.md`.
- Compress: preserve the behavior with shorter wording.
- Relocate: keep the trigger or boundary here; move details to the owning file, Skill, or SOP.
- Merge: consolidate overlapping rules without changing the behavior.
- Retire: remove only when stale, contradictory, unsafe, or misplaced, and record why.

## Preservation Map

| Prior rule or section | Disposition | Destination | Decision |
|---|---|---|---|
| Purpose, role, reporting, authority, and priorities | Retain and reorder | Purpose, Setup, Role | Put identity, authority, and approval boundaries before procedures. |
| Asana ownership and task quality | Retain and clarify | Asana Operating Standards | Owners, outcomes, due dates, blockers, approved-project breakdown, handoffs, and reviews preserved. Blanket task creation narrowed so ordinary Q&A does not silently create work. |
| PAT identity and route verification | Retain | Skills and Capability | Amanda identity, workspace preflight, Jack-connector prohibition, and real-call proof preserved; exact IDs moved to `TOOLS.md`. |
| Advanced Asana control | Retain and correct | Skills and `TOOLS.md` | Advanced capability and approval gates preserved. Stale separate `asana-team` routing retired because live configuration exposes one `asana` server. |
| Get-er-Done and Diagnose | Add explicitly | Operating Modes | Separate triggers, DSCA sequence, pilot, and new-risk stop gate added. |
| Routing and sources of truth | Retain and merge | Source Of Truth | Asana, GitHub, Notion, Wiki, LanceDB, live evidence, and originating-channel ownership preserved. |
| Notion and Z-Knowledge | Retain and compress | Notion And Z-Knowledge | Approved Codex Apps OAuth, no fallback, search, live schema, canonical update, read-back, attribution, and URL evidence preserved. |
| Durable knowledge capture | Correct and preserve | Scope, Memory, Notion | Explicitly authorized publication remains required. Forced writes from review-only, diagnosis-only, incidental facts, or ordinary Q&A are retired as scope conflicts. |
| LanceDB quick-recall activity | Compress and narrow | Memory | Provider, recall, compact pointers, update-before-duplicate, write verification, privacy, and source verification preserved. Writes require authorization and utility. |
| Startup and skills | Retain | Startup | Current context, relevant files, skill discovery, complete skill read, small-bite trigger, and managed-browser distinction preserved. |
| Execution, security, and completion | Retain and merge | Execution and Security | Evidence, least privilege, backup, one-agent pilot, user-facing proof, read-back, secrecy, outbound scan, honest blockers, rollback, and completion report preserved. |
| Assignment continuity | Retain | Communication | Managed acknowledgement and progress behavior retained under the same marker. |
| Telegram delivery safeguard from retained live history | Restore | Communication | Use `message` directly; never fall back to session lookup or `sessions_send`. This prevents the prior cold-start reply failure. |
| Z-small-bite and provider-alignment tail blocks | Merge | Startup and Memory | Triggers, live-provider use, authority checks, compact pointers, and verification preserved without duplicate tail sections. |
| Appended local tool notes | Relocate | `agents/amanda/TOOLS.md` | Runtime, channel, email, Asana identity, toolset, knowledge route, and memory facts preserved outside the always-loaded policy. |
| Daily journal procedure in appended tool notes | Relocate | `agents/amanda/HEARTBEAT.md` | First-session Mountain Time journal rule and concise activity updates preserved in the recurring-check file. |
| Duplicate or contradictory Asana paragraphs | Merge or retire | `TOOLS.md` and Skills | Single current route retained; earlier two-route wording removed. No credential value is stored. |

## Critical Coverage Gates

- Identity, role, reporting, authority, and escalation: covered.
- Get-er-Done and Diagnose modes: separate and explicit.
- Review-only, diagnosis-only, and no-write boundaries: covered.
- Advanced Asana identity, route, toolset, and approval gates: covered.
- Task quality, project flow, blockers, VA handoffs, and oversight: covered.
- GitHub, Notion, Asana, runtime, Memory Wiki, and LanceDB ownership: covered.
- Codex Apps Notion OAuth, search, schema, canonical update, and read-back: covered.
- Telegram direct-delivery safeguard: restored.
- Backup, pilot, live verification, ownership, permissions, rollback, and handoff: covered.

## Planned Pilot Tests

- Fresh session injects the complete file with `truncated=false`.
- Amanda identifies her role, reporting line, and Asana ownership.
- Get-er-Done and Diagnose/DSCA remain distinct.
- Review-only work does not authorize implementation or durable writes.
- Asana work uses Amanda's PAT identity and one current `asana` route; advanced changes retain confirmation gates.
- Telegram replies use `message`, not session lookup or `sessions_send`.
- Governed Notion uses approved Codex Apps OAuth and stops without an unsafe fallback.
- Completion requires evidence, source-of-truth updates when required, rollback, and stated gaps.

## Pilot Result

- Pending live deployment and fresh-session verification.
