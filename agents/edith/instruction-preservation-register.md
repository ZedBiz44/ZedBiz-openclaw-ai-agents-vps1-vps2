# Edith AGENTS.md Instruction Preservation Register

Date: 2026-08-27  
Agent: Cody  
Status: Deployed and verified on Edith

## Baseline

- Live file: `/opt/openclaw/agents/edith/workspace/AGENTS.md`
- Runtime workspace: `/home/node/.openclaw/workspace`
- Baseline SHA-256: `3d9fae533f4dcebc9d334ea41664a511021acb8d24284e9618d3d4c9b886c53e`
- Baseline size: 12,365 bytes / 120 lines
- Runtime: Edith healthy on `ghcr.io/zedbiz44/openclaw-base:latest`
- Verified routes: Sol/Terra/Luna → Codex; Asana resident MCP; Mem0 active memory slot; Discord configured.

## Disposition Standard

- Retain: keep the rule in AGENTS.md.
- Compress: preserve the behavior with shorter wording.
- Relocate: keep the trigger or boundary here; detailed procedure remains in the owning file, skill, or SOP.
- Merge: consolidate duplicate or overlapping rules.
- Retire: remove only when stale, contradictory, unsafe, or a template artifact; record why.

## Preservation Map

| Prior section or rule | Disposition | Destination | Decision |
|---|---|---|---|
| Purpose and core-file ownership | Retain and compress | Purpose | File ownership, small-bite trigger, Jack authority, and safety boundaries preserved. |
| Role, Authority, And Ownership | Retain and reorder | Identity/Role | Research, knowledge, personnel context, reporting, Amanda's Asana ownership, originating chat, and release approvals preserved. |
| Research And Knowledge Standards | Retain | Research/Knowledge | Facts/inferences/gaps, cross-referencing, source dates, internal lookup, citations, missing information, and authorized ingestion preserved. |
| Routing And Sources Of Truth | Retain and expand accurately | Sources/Routing | Live, GitHub, Wiki, Notion, Asana, skills, and low-risk ambiguity behavior preserved. |
| Z-Knowledge And Notion | Merge | Knowledge/Notion | Skill triggers, durable layers, canonical parent, frontmatter, titles, daily journal, and concise Core Master naming preserved. |
| Durable Knowledge Capture | Compress | Knowledge/Notion | Authorization, Codex OAuth, no fallback, schema, search, attribution, entity routing, sanitized records, and exact evidence preserved. |
| Mandatory new-entity and fact capture | Narrow | Knowledge/Notion | Applies only when durable publication is authorized; ordinary research and Q&A do not silently write. |
| Memory Discipline | Compress and correct | Memory/Continuity | Mem0 recall, compact pointers, layer ownership, privacy, provider verification, Markdown/SQLite distinction, and conflict handling preserved. |
| Mandatory Mem0 write for every assignment | Narrow | Memory/Continuity | Recall remains relevant-context behavior; writes require authorization and utility. Forced review/research-only writes retired as conflicting. |
| Hindsight-specific provider wording | Retire as irrelevant | None | Edith uses Mem0; Hindsight completion behavior does not belong in her policy. |
| Decisions, Safety, And Approval | Retain and move earlier | Identity/Authority, Execution, Security | Priority, evidence, smallest change, approval gates, privacy, secret scanning, and honest results preserved. |
| Execution And Completion | Retain | Execution/Completion | Conditional bootstrap loading, skills, preservation, single-example test, exact locations, read-back, and completion gaps preserved. |
| Communication | Retain and move earlier | Assignment/Communication | Managed acknowledgement block preserved; direct, concise, source-aware reporting and heading rules retained. |
| Maintenance | Retain and strengthen | Maintenance/Context Budget | Adds explicit size, disposition, duplicate scan, rollback, and no-append controls. |
| Provider And Durable Knowledge Alignment | Merge | Sources and Memory | Provider support role, source verification, authorization, and compact-pointer behavior preserved without duplication. |
| Separate operating modes absent | Add from approved standard | Operating Modes | Get-er-Done and Diagnose triggers and DSCA behavior now explicit. |
| Current runtime mappings and resident MCP | Correct from live evidence | Model/Tool Routing | Sol/Terra/Luna are Codex; Asana is resident; Notion is Codex Apps OAuth; Discord is configured. |
| Detailed paths, channel setup notes, identity, journal checklist, and recurring checks | Relocate | TOOLS.md, IDENTITY.md, HEARTBEAT.md | AGENTS retains boundaries and triggers while changing facts remain in owning files. |

## Critical Coverage Gates

- Identity, role, reporting, Amanda task ownership, authority, and confidentiality: covered.
- Get-er-Done and Diagnose modes: separate and explicit.
- Review-only, diagnosis-only, research-only, and no-write boundaries: covered.
- External publishing, personnel, executive, destructive, production, paid, client, credential, legal, financial, and privacy gates: covered.
- Facts/inferences/gaps, citations, source dates, canonical records, parents, relations, and read-back: covered.
- GitHub, Notion, Asana, runtime, Memory Wiki, and Mem0 ownership: covered.
- Sol/Terra/Luna Codex, Codex Apps Notion, resident Asana, Discord, and stop-without-fallback behavior: covered.
- Assignment continuity, originating-channel behavior, verification, and handoff: covered.
- Daily Journal, Notion frontmatter, Core Master naming, and exact record evidence: covered.
- Private-memory and personnel-context boundaries: covered.

## Planned Pilot Tests

- Fresh-session injection reports no truncation.
- Edith identifies her role, reporting lines, and Amanda's Asana ownership.
- Diagnose request stops before implementation.
- Get-er-Done request describes smallest complete result and one-record pilot behavior.
- Ordinary research/review does not authorize durable writes.
- Governed Notion uses Codex Apps OAuth and stops without fallback on failure.
- Edith identifies Sol/Terra/Luna as Codex routes, Asana as resident MCP, and Notion as a Codex App.
- Research answer separates fact, inference, conflicting evidence, and gap.
- Personnel context remains restricted to the approved audience and scope.
- Asana work uses Edith's PAT-backed identity and respects Amanda's coordination ownership.
- Completion reports sources, exact locations, read-back, confidentiality, and remaining gaps.

## Verified Pilot Result

- Deployed SHA-256: `c236d2497aa6ce7fb9cb2a021099b4cece4f137c2fcec010f3b7e037df3f2188`
- Deployed size: 13,864 bytes / 158 lines
- Backup: `/opt/openclaw/agents/edith/backups/20260827T232142Z-agents-preservation-pilot`
- OpenClaw system prompt report: 13,851 AGENTS.md characters injected; `truncated=false`.
- Fresh GPT-5.6 Sol/Codex session returned Edith's role, Jack/Marsha reporting, Amanda's Asana ownership, both operating modes, no-write boundary, governed Notion route, all-Codex model mapping, resident Asana MCP, research evidence categories, personnel confidentiality, PAT identity rule, and completion standard.
- The test prompt prohibited tools, writes, mutation, and external delivery. The session completed normally.
- Post-test live hash matched the committed candidate; ownership remained `1000:1000`, mode `0644`, restart count zero, and container healthy.
