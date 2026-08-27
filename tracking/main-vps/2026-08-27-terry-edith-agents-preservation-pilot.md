# Terry and Edith AGENTS.md Preservation-First Pilot

Date: 2026-08-27 Mountain Time  
Agent: Cody  
Status: Deployed and verified on Terry and Edith

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

## Deployment

### Terry

- Exact baseline hash rechecked before writing.
- Backup: `/opt/openclaw/agents/terry/backups/20260827T232014Z-agents-preservation-pilot`
- New SHA-256: `c9e8e30a9b1a8994c59d1268b2fd0f4e910a6c78524f18b71f3371c3340e314d`
- New size: 14,336 bytes / 169 lines
- Ownership and mode: `1000:1000`, `0644`
- No restart or configuration change was performed.

### Edith

- Terry passed all critical gates before Edith deployment began.
- Exact Edith baseline hash rechecked before writing.
- Backup: `/opt/openclaw/agents/edith/backups/20260827T232142Z-agents-preservation-pilot`
- New SHA-256: `c236d2497aa6ce7fb9cb2a021099b4cece4f137c2fcec010f3b7e037df3f2188`
- New size: 13,864 bytes / 158 lines
- Ownership and mode: `1000:1000`, `0644`
- No restart or configuration change was performed.

## Fresh-Session Verification

### Terry

- Provider/model: OpenAI GPT-5.6 Sol through the Codex harness.
- AGENTS.md injection: 14,325 characters; not truncated.
- Correctly returned role/reporting, Get-er-Done, Diagnose/DSCA, no-write boundary, Codex Apps Notion, stop-without-fallback, Sol versus Terra/Luna routes, Asana/Percify, layered testing proof, partial-pass rule, paid-media gate, audio/video boundary, PAT Asana identity, and completion verification.

### Edith

- Provider/model: OpenAI GPT-5.6 Sol through the Codex harness.
- AGENTS.md injection: 13,851 characters; not truncated.
- Correctly returned role/reporting, Amanda's Asana ownership, Get-er-Done, Diagnose/DSCA, research/review no-write boundary, Codex Apps Notion, stop-without-fallback, Sol/Terra/Luna Codex routes, resident Asana MCP, fact/inference/conflict/gap separation, personnel confidentiality, PAT Asana identity, and completion verification.

### Final Runtime State

- Both review-only tests completed without requested tools, writes, mutations, paid generation, or external delivery.
- Both live hashes matched the committed candidates after testing.
- Both containers were running and healthy with restart count zero.

## Rollback

- Restore the agent's `AGENTS.md.before` from its own timestamped backup directory.
- Restore ownership `1000:1000` and mode `0644`.
- Verify the baseline SHA-256, run a fresh-session read-back, and confirm container health.
