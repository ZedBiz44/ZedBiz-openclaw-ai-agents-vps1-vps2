# Terry and Edith AGENTS.md Preservation-First Pilot

Date: 2026-08-27 Mountain Time  
Agent: Cody  
Status: Candidates prepared; live deployment pending

## Purpose

Apply the verified Vivian preservation-first method to Terry and Edith without cloning role-specific wording or silently losing instructions.

## Baselines

| Agent | SHA-256 | Size | Runtime | Memory | Model routes |
|---|---|---:|---|---|---|
| Terry | `1003f05ef12035ce7963195fbeff0f17009d0021a9e69cdc5a7157712007d914` | 15,860 bytes / 186 lines | Healthy, `zedbiz/openclaw-base:2026.7.1-2-video` | Mem0 | Sol Codex; Terra/Luna OpenClaw |
| Edith | `3d9fae533f4dcebc9d334ea41664a511021acb8d24284e9618d3d4c9b886c53e` | 12,365 bytes / 120 lines | Healthy, `ghcr.io/zedbiz44/openclaw-base:latest` | Mem0 | Sol/Terra/Luna Codex |

## Candidate Results

| Agent | Candidate size | Structural result |
|---|---:|---|
| Terry | 14,336 bytes | One H1; Combined Tool Policy merged; explicit modes; testing/QC and media test rules preserved. |
| Edith | 13,864 bytes | One H1; explicit modes; research, personnel, knowledge, and Asana ownership rules prioritized. |

## Method

- Inspect live files, core-file ownership, runtime mappings, resident MCPs, channels, skills, memory provider, and health.
- Classify every prior section and material rule as retain, compress, relocate, merge, or retire.
- Put role, authority, modes, assignment behavior, and approval gates near the beginning.
- Keep changing paths, identities, and procedures in their owning files while retaining governing triggers in AGENTS.md.
- Back up and deploy one agent at a time from the exact committed GitHub candidate.
- Run a new isolated session after each deployment and stop before deploying the second agent if the first fails a critical gate.

## Scope Boundary

Only Terry and Edith top-level `AGENTS.md` files are in scope. No other core file, agent, runtime configuration, service, model mapping, memory store, skill, route, or credential may be changed.

## Required Verification

- Exact baseline hash rechecked before each write.
- Backup stored outside the active workspace.
- Candidate hash and size match GitHub.
- One H1, zero duplicate headings, zero unresolved placeholders, and all critical gates pass.
- Ownership and mode preserved.
- Fresh session loads without truncation and returns the agent-specific policy gates.
- Container remains or returns healthy and the live hash matches the candidate.
- GitHub and Notion records are updated and re-read.

## Rollback

- Restore the agent's `AGENTS.md.before` from its own timestamped backup directory.
- Restore ownership `1000:1000` and mode `0644`.
- Verify the baseline SHA-256, run a fresh-session read-back, and confirm container health.
