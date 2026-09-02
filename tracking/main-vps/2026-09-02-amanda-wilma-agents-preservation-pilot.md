# Amanda and Wilma AGENTS.md Preservation-First Pilot

Date: 2026-09-02 Mountain Time | Agent: Cody | Status: Deployed and verified

## Purpose

Apply the proven preservation-first method to Amanda and Wilma without silently deleting accumulated operating rules or cloning one role into the other.

## Baselines

| Agent | SHA-256 | Size | Runtime | Memory | Verified resident MCPs |
|---|---|---:|---|---|---|
| Amanda | `d350f0f249be6329a3a56119ac909ba8ddfe2870a1e4ea4d382d52d3f1d5fbe6` | 19,786 bytes / 252 lines | Healthy, OpenClaw 2026.8.2 | LanceDB | `asana` |
| Wilma | `efb735c6ecd6d70db0e7b346ab43b0d9ab54cb48c510a1961a553c24021c164b` | 13,144 bytes / 140 lines | Healthy, OpenClaw 2026.8.2 | LanceDB | `asana`, `wordpress-allzed` |

## Baseline Findings

- Amanda crossed the observed 20,000-character bootstrap ceiling risk zone at 19,786 bytes.
- Amanda's complete local tool sheet had been appended to `AGENTS.md`; the live top-level `TOOLS.md` and `HEARTBEAT.md` were missing.
- Amanda's retained historical backup contained an essential Telegram delivery rule that was no longer in the current live file.
- Amanda contained contradictory Asana routing: an earlier separate `asana-team` instruction and a later single-`asana` Advanced toolset instruction. Live configuration exposes only `asana`.
- Wilma remained near the target size but lacked separate Get-er-Done and Diagnose sections.
- Wilma's current live resident website route is `wordpress-allzed`. Other-site access must not be claimed from stale documentation or host-side setup alone.

## Candidate Results

| Agent | Candidate | Structural result |
|---|---:|---|
| Amanda | 14,000 bytes / 185 lines | One H1; explicit modes; tool manual relocated; Telegram safeguard restored; current single Asana route preserved. |
| Wilma | 13,964 bytes / 189 lines | One H1; explicit modes; site/target/rollback gates prioritized; resident versus unverified WordPress routes distinguished. |

Supporting relocations for Amanda:

- `agents/amanda/TOOLS.md` restores current runtime, channel, Asana identity/toolset, Notion route, email, and memory facts outside the bootstrap contract.
- `agents/amanda/HEARTBEAT.md` restores the approved first-session Mountain Time journal rule and routine-check boundaries.

## Method

- Inspect live files, history, runtime configuration, resident MCPs, channels, skills, memory provider, image, ownership, and health.
- Classify every material rule as retain, compress, relocate, merge, or retire.
- Put role, authority, operating modes, scope, and approval gates before specialist procedures.
- Keep changing identities, endpoints, and commands in `TOOLS.md`; recurring routines in `HEARTBEAT.md`; reusable procedures in Skills or GitHub SOPs.
- Commit and push the candidates before deployment.
- Back up and deploy Amanda first. Deploy Wilma only if Amanda passes all critical static and fresh-session gates.

## Scope Boundary

- Amanda: `AGENTS.md`, plus restoration of the missing `TOOLS.md` and `HEARTBEAT.md` needed to preserve relocated content.
- Wilma: top-level `AGENTS.md` only.
- No runtime configuration, service, model, plugin, credential, memory store, Skill, or other agent is changed.

## Required Verification

- Exact baseline hash is rechecked before each write.
- Backup is stored outside the active workspace.
- Candidate hash and size match GitHub.
- One H1, zero duplicate H2 headings, zero unresolved placeholders, and all critical coverage gates pass.
- Ownership and mode are correct.
- Fresh session loads the whole `AGENTS.md` with `truncated=false` and returns agent-specific policy gates.
- Container stays healthy with no restart introduced by this file-only deployment.
- GitHub and Notion records are updated and re-read.

## Deployment And Fresh-Session Results

### Amanda

- Exact baseline hash was rechecked before writing.
- Backup: `/opt/openclaw/agents/amanda/backups/20260902T173126Z-agents-preservation-pilot`.
- New AGENTS SHA-256: `35c3dc93dcd8b49d14f691c87d1bf398fd87d99351cc23fa549513417c894258`.
- New size: 14,000 bytes / 185 lines.
- Restored `TOOLS.md`: 2,743 bytes; restored `HEARTBEAT.md`: 993 bytes.
- Fresh GPT-5.6 Sol/Codex review-only sessions used no tools or writes and returned all critical Amanda-specific policy gates, including the final Maintenance rule.

### Wilma

- Amanda passed before Wilma deployment began.
- Exact baseline hash was rechecked before writing.
- Backup: `/opt/openclaw/agents/wilma/backups/20260902T173328Z-agents-preservation-pilot`.
- New AGENTS SHA-256: `f735583cd39fe450f755e321b5b1932a085644797b126f7730b959d16e5afd94`.
- New size: 13,964 bytes / 189 lines.
- Fresh GPT-5.6 Sol/Codex review-only session used no tools or writes and returned all critical Wilma-specific policy gates, including the final Maintenance rule.

### Runtime Result

- Both files remained owner `1000:1000`, mode `0644`.
- Both containers remained healthy on `ghcr.io/zedbiz44/openclaw-base:2026.8.2` with restart count zero. No restart or configuration change was performed.
- OpenClaw 2026.8.2 reports native AGENTS injection as `native_unverified`; Amanda showed `rawChars=13991` and Wilma `rawChars=13955`, with no `injectedChars` or `truncated` value. Correct end-of-file paraphrases provide direct tail-availability evidence without misreporting the absent field.

## Rollback

- Restore each changed file from its agent-specific timestamped backup directory.
- Restore ownership `1000:1000` and mode `0644`.
- Verify the baseline SHA-256, run a fresh-session policy read-back, and confirm container health.
