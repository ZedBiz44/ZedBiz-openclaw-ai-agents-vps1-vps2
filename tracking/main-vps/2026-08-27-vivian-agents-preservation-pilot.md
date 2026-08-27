# Vivian AGENTS.md Preservation-First Pilot

Date: 2026-08-27 Mountain Time  
Agent: Cody  
Status: Deployed and verified on Vivian

## Purpose

Convert Vivian's oversized AGENTS.md to the canonical structure without silently losing essential instructions.

## Baseline

- Live SHA-256: `81e41c94207a00e230e7f7a0b220127c6b3fe5cff7be4e058b3f5769a0b244d5`
- Live size: 25,579 bytes / 313 lines
- Container: healthy
- Runtime routes: Sol through Codex; Terra and Luna through OpenClaw
- Resident MCP servers: Asana and Percify
- Memory: LanceDB

## Method

- Inventory every current section and material rule.
- Classify each as retain, compress, relocate, merge, or retire.
- Correct stale dynamic facts from live runtime evidence.
- Keep a concise trigger in AGENTS.md when detailed procedure belongs in a skill, TOOLS.md, HEARTBEAT.md, MEMORY.md, or GitHub SOP.
- Reject silent deletion and record every retirement reason.
- Validate size, critical-rule coverage, duplicates, placeholders, and prohibited stale routes before deployment.
- Back up the exact live file, deploy Vivian only, test a fresh session, and retain immediate rollback.

## Files

- `agents/vivian/AGENTS.md`
- `agents/vivian/instruction-preservation-register.md`
- `tracking/main-vps/2026-08-27-vivian-agents-preservation-pilot.md`

## Scope Boundary

No other agent, core file, runtime configuration, service, model mapping, memory store, skill, route, or credential is in scope.

## Deployment

- Exact baseline hash was rechecked before writing.
- Backup: `/opt/openclaw/agents/vivian/backups/20260827T224716Z-agents-preservation-pilot`
- New SHA-256: `65a4592f176c112a1d8162bcb27abd79748b7a4d98e5131d875fe1d14bf0b4cc`
- New size: 13,117 bytes / 155 lines
- Ownership and mode: `1000:1000`, `0644`
- Deployment used the exact candidate committed in GitHub.
- No restart or configuration change was performed by the deployment step.

## Static Verification

- One H1.
- Zero duplicate headings.
- Zero unresolved placeholders.
- Below the 16 KB deployment stop.
- All critical preservation gates passed.

## Fresh-Session Verification

- Provider/model: OpenAI GPT-5.6 Sol through the Codex harness.
- AGENTS.md injection: 13,108 characters, not truncated.
- Vivian correctly identified:
  - her role and Jack/Marsha reporting line;
  - Get-er-Done and Diagnose behavior;
  - Sol/Codex Apps OAuth as the governed Notion route;
  - stop-without-fallback behavior when that route fails;
  - the paid-media approval gate;
  - Vivian's PAT-backed Asana identity boundary;
  - ordinary Q&A as not authorizing durable writes;
  - the approved dry narration master and separate video/audio responsibilities;
  - the runtime media path and GitHub/Notion source ownership;
  - the verified completion standard.
- The review-only test made no requested write, external delivery, or paid generation.
- The live file hash still matched the committed candidate after the fresh session.
- The container returned healthy.

## Runtime Observation

- Docker recorded a restart event during the verification window after transient health-check failures.
- The pilot deployment command itself did not restart or recreate Vivian.
- After the event, Vivian returned healthy, retained the new hash, and continued to load the file without truncation.

## Rollback

- Restore `AGENTS.md.before` from the backup directory to Vivian's workspace.
- Set ownership to `1000:1000` and mode to `0644`.
- Verify the restored baseline SHA-256, run a fresh-session read-back, and confirm container health.
