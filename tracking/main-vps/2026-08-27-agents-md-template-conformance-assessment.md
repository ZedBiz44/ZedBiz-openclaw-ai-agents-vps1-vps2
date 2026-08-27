# AGENTS.md Template Conformance Assessment

Date: 2026-08-27  
Verified by: Cody  
Status: Assessment complete; no live agent files changed

## Decision

The fleet is safer and more consistent than it was before the August overhaul, but none of the fourteen assessed live AGENTS.md files is a clean deployment of the approved Standard AGENTS.md Template.

Use Harry as the first controlled conversion. Verify his behavior in production, then roll the tested pattern through VPS2 and VPS1 in small batches.

## Scope

- Live read-only inspection of all top-level AGENTS.md files for the eleven VPS1 Docker agents and three VPS2 systemd agents.
- Comparison against `docs/templates/standard-agents-md-template.md`.
- Size inspection of the other top-level core Markdown files.
- No agent file, runtime, container, service, route, memory store, or credential was changed.

## What Now Passes Fleet-Wide

- Every assessed AGENTS.md has an explicit assignment or authority boundary.
- Every assessed AGENTS.md identifies authoritative sources or routing.
- Every assessed AGENTS.md contains capability or route verification guidance.
- Every assessed AGENTS.md contains memory and knowledge boundaries.
- Every assessed AGENTS.md contains verification or completion rules.
- Every assessed AGENTS.md contains security or confidentiality rules.
- Every assessed AGENTS.md tells the agent to acknowledge assignments.
- No assessed AGENTS.md contains forced arithmetic, eye-colour, or ice-cream tests.
- No assessed AGENTS.md contains unresolved template placeholders.

## Conformance Matrix

| Agent | Host | Bytes | Operating modes | Main gap | Priority |
|---|---|---:|---|---|---|
| Amanda | VPS1 | 13,574 | Not explicit | Add separate Get-er-Done and Diagnose sections | Medium |
| Edith | VPS1 | 12,365 | Not explicit | Add separate Get-er-Done and Diagnose sections | Medium |
| Gohzed | VPS1 | 13,162 | Not explicit | Add separate Get-er-Done and Diagnose sections | Medium |
| Grogar | VPS1 | 12,542 | Not explicit | Add modes; reduce broad mandatory activity capture | Medium |
| Inga | VPS1 | 11,545 | Not explicit | Add separate Get-er-Done and Diagnose sections | Medium |
| Maggie | VPS1 | 12,971 | Not explicit | Add modes and explicit communication/handoff rules | Medium |
| Marsha | VPS1 | 16,592 | Not explicit | Oversized and missing modes | High |
| Terry | VPS1 | 15,860 | Not explicit | Duplicate Purpose section and missing modes | High |
| Victor | VPS1 | 13,025 | Partial combined protocol | Split Get-er-Done and Diagnose into distinct rules | Medium |
| Vivian | VPS1 | 25,474 | Not explicit | Above the observed context-injection ceiling | Critical |
| Wilma | VPS1 | 13,039 | Not explicit | Add separate Get-er-Done and Diagnose sections | Medium |
| Frank | VPS2 | 23,214 | Both explicit | Oversized; obsolete tracker wording; forced publishing | Critical |
| Harry | VPS2 | 12,770 | Not explicit | Forced publishing and obsolete tracker wording | Pilot first |
| Suzy | VPS2 | 10,911 | Not explicit | Forced publishing; modes and handoff rules missing | High |

## Highest-Risk Findings

### Context size

- Vivian AGENTS.md is 25,474 bytes and Frank AGENTS.md is 23,214 bytes. Both exceed the observed 20,000-byte injection ceiling.
- Marsha AGENTS.md is 16,592 bytes and should be reduced before more policy is added.
- Terry AGENTS.md is 15,860 bytes and repeats the Purpose heading.

### Operating modes

- Frank is the only live agent with separate Get-er-Done Mode and Diagnose Mode sections.
- Victor has a combined Diagnose/Get-er-Done protocol and DSCA rule, but it does not clearly define the two distinct triggers and behaviors.
- The other twelve agents do not explicitly define both modes.

### Scope-conflicting publishing rules

- Frank, Harry, and Suzy still say every meaningful assignment must create or update a Notion Core Content record and mandatory Memory Wiki mirror.
- Their completion rule says a chat-only answer is incomplete.
- This conflicts with the approved template's assignment-scoped, authorization-aware publishing rules.
- Harry and Frank also retain obsolete content-tracker or operations-tracker wording.

### Core-file separation

- Inga SOUL.md is 8,547 bytes and Maggie SOUL.md is 8,429 bytes.
- Maggie MEMORY.md is 10,401 bytes and Suzy MEMORY.md is 8,795 bytes.
- Grogar SOUL.md is 4,848 bytes across 199 lines.
- These files are not automatically defective, but they are strong candidates for separating durable role identity from procedures, history, and generated memory.

## Recommended Rollout

### Harry pilot

- Back up Harry's current core files.
- Build his AGENTS.md from the canonical template.
- Preserve only Harry-specific role, host, channel, tool, and escalation rules.
- Remove obsolete tracker language and mandatory publishing for every assignment.
- Verify acknowledgement, Get-er-Done execution, Diagnose stopping behavior, read-only review boundaries, source routing, and durable handoff.

### VPS2 completion

- Apply the verified Harry pattern to Suzy.
- Rebuild Frank with the same pattern while reducing the file below the safe context budget.
- Confirm all three systemd agents still start, respond, use the right channels, and route records correctly.

### VPS1 rollout

- Convert Vivian first because the file is above the observed injection ceiling.
- Convert Marsha and Terry next because of size and duplication.
- Convert the remaining VPS1 agents in small role-based batches.
- Test one agent in each batch before proceeding.

### Core-file cleanup

- Review oversized SOUL.md and MEMORY.md files separately.
- Keep identity and behavioral character in SOUL.md.
- Keep durable distilled facts and pointers in MEMORY.md.
- Move repeatable procedures to skills or SOPs and keep generated memory out of the manually maintained policy surface.

## Acceptance Checks

- The live AGENTS.md is based on the canonical template and contains no unresolved placeholders.
- Get-er-Done and Diagnose are separate, explicit, and testable.
- Review-only work does not authorize implementation or publishing.
- GitHub remains the technical source of truth and Notion remains the operational summary layer.
- The agent verifies identity, route, tool access, and results before claiming completion.
- No forced personality tests, stale tracker names, false service assumptions, secrets, or blanket publishing mandates remain.
- The file stays inside the practical context budget with no duplicate policy blocks.
- The agent acknowledges promptly and provides a concise verified handoff.

## Records

- Canonical template: `docs/templates/standard-agents-md-template.md`
- Notion review: AI Agent Core MD File Review
- Notion guidelines: Agents MD Guidelines
- Assessment performed from live VPS1 and VPS2 files on 2026-08-27 Mountain Time.
