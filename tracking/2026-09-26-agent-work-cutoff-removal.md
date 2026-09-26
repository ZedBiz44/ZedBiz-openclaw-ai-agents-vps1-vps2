# Agent timer audit — September 26, 2026

## Verified changes

Jack directed removal of arbitrary agent work cutoffs, first for Edith, then the assignment and fleet, and an inventory of historical timing changes.

- All 15 hosted OpenClaw agents now use `agents.defaults.timeoutSeconds=0` (documented unlimited execution).
- All 16 IMAP account overrides are removed. They now inherit that unlimited agent default. Most had been 120 seconds; Harry had 600 seconds. Edith briefly had 600 seconds during this repair before it was removed.
- 67 scheduled agent-job overrides changed from 300, 900 or 1200 seconds to zero. Includes disabled pilot jobs so re-enabling them does not restore a cutoff. Schedules, owners, prompts and delivery routes were preserved.
- A fresh read-back covered all 15 configurations and 147 scheduled jobs: no nonzero configured whole-agent/email/agent-job cutoff remained.
- Ruby uses a separate Hermes runtime. Her 1800-second inactivity stop, 900-second warning, 60-turn limit and 14400-second stale-work threshold were removed. The elapsed run budget is explicitly null. Obsolete 04:00/six-hour session-reset configuration was removed; installed Hermes described it as inert legacy data.
- Edith's 900-second legacy dispatcher limit and 960-second process kill, 2700-second continuous-turn limit and 2760-second kill, and two 7200-second test launchers were removed. Amanda's 600-second coordinator limit and 660-second kill were removed. Ruby's timed review deferral and Edith's successor-expediting helper were retired. The 55-minute backup renewal and timed follow-up creation in Edith's legacy dispatcher were removed. Her already-paused legacy dispatcher was not restarted.
- Today's two completed recovery-launch scripts now specify zero for future execution. Past run receipts and original backups retain the historical values.
- The no-cutoff policy is saved in all 16 hosted agents' AGENTS.md files and this workspace's Agent-Execution-Policy.md. Old continuous-work installers in the source copies found by the audit are retired.

There are **98 OpenClaw configuration/job changes** in `Agent-Timer-Removal-Register.csv`, plus Ruby's settings and the script changes documented below.

## Edith's assignment result

Edith finished the recovery run naturally after approximately six minutes. Asana task 1218889338462783 is completed at 14:19:52 MDT. The new page was independently fetched and verified as Submitted under the correct round-two intake:
https://www.notion.so/3e7a3e33d5818159bbd4fc758ff873d7

Filing Verification and Content Review remain Pending. Those reviews are separate work. No second snapshot or replacement task was created by this repair.

## Responsibility and original evidence

The September 4 IMAP rollout record credits Cody with the fleet setup (`tracking/2026-09-04-openclaw-imap-email-fleet-rollout.md`, issue 252). That record does not identify who selected the exact original 120-second value, so exact authorship remains unproven. The 600-second Edith replacement today was added in this task and subsequently removed following Jack's correction.

The earlier no-time-limit instruction was already preserved in Edith's September 18 project files. Adding a replacement ten-minute limit today did not follow that instruction.

## Remaining limits and specific reasons

This is **not a claim that every timer in every platform has been removed**.

| Item | Current state | Reason / next work |
| --- | --- | --- |
| OpenClaw exec command default | Built-in 1800 seconds still exists. `tools.exec.timeoutSeconds=0` is rejected by the installed configuration schema. | Individual exec calls support `timeoutSeconds:0`; the policy now requires it. This is a known unresolved framework default, not a verified global removal. A tested upstream/schema or tool-hook change is needed for unconditional enforcement. |
| Ruby terminal commands | Built-in foreground limit remains; zero is explicitly rejected. | Long commands must use the supported tracked background route. Do not claim the command framework is globally untimed. |
| Ruby already-running turn | A turn already started can retain the old captured inactivity budget. | Saved config and the per-turn dotenv override apply without forcing interruption. No active turn was killed to apply settings. Fresh gateway-process behavior after reload/restart was not independently tested. |
| Network connect / API requests | Retained; exact authored settings listed below. | Detect unreachable endpoints or stalled individual calls so an agent receives an error. They do not intentionally impose an overall assignment duration. Uncertain writes must be reconciled before retry. |
| Provider stream liveness | Runtime watchdogs remain. | Detect a model connection that stops producing responses. No evidence justified disabling detection of broken network streams. |
| Approved reporting intervals | Preserved. | They decide when a report starts; they do not terminate an agent's work. Marsha's ten-minute status monitor explicitly records Jack's authorization. |
| Business due dates | Preserved. | Planning targets in Asana; not automatic execution stops. |
| Original backups, historical logs and finished receipts | Original values retained as evidence, excluded from active-code cleanup. | They show what happened. Policy forbids reinstalling retired timing behavior from them. |

## Project and historical coverage

Read all 51 task descriptions returned for Agent Key-Info Snapshots, with no next page. The only work-limit mentions documented withdrawn restrictions and historical 180/300-second launches. No new deadline was imposed. This check does not certify hidden Asana rules or every nested subtask description.

Searched accessible project source/config files under the local Codex-Projects directories for agent-timeout and process-kill patterns, excluding dependencies/build outputs, credential directories, historical backup trees, and files larger than 1 MB. The completed search found 24 candidate files; first-party deployment copies were corrected. A prior broad filesystem walk stalled and was cancelled; it was not counted as a completed audit. The candidate filenames are preserved in historical-timer-files.txt.

This cannot certify every past conversation, deleted script, inaccessible machine, cloud platform or third-party internal limit. The other computer's requested chat was not exposed in the current task list. The saved project instructions did corroborate Jack's previous no-timer instruction.

## Verification and repair exceptions

- All edited OpenClaw configs passed validation; all changed job values passed live API read-back. A separate fleet read-back confirmed the final state.
- Edith logs confirmed the unlimited agent default and removed IMAP override were hot-reloaded; her IMAP watcher reconnected. No deliberate fleet restart was performed.
- Four targeted tests passed: nested termination timers removed correctly; network error timeout preserved; current helpers have no kill deadlines; retired successor performs no Asana writes. Python syntax was checked before remote script writes.
- Cron CLI rejected `--timeout-seconds 0`; the supported gateway `cron.update` API accepted zero and was verified. No positive replacement was used.
- Victor and Wilma backup-directory permissions initially stopped changes before mutation. Their successful retry stored protected backups in `private/no-work-cutoffs-20260926`.
- Edith's root-owned historical test launcher initially rejected a write. The exact files were subsequently edited as their existing owner; no broader ownership or permission change was made.

## Agent-by-agent register

| Agent | Server | Default | Mail overrides removed | Scheduled cutoffs removed |
| --- | --- | --- | --- | --- |
| amanda | VPS1 | unlimited | 2 | 4 |
| marsha | VPS1 | unlimited | 1 | 5 |
| victor | VPS1 | unlimited | 1 | 20 |
| wilma | VPS1 | unlimited | 1 | 3 |
| grogar | VPS1 | unlimited | 1 | 3 |
| gohzed | VPS1 | unlimited | 1 | 3 |
| inga | VPS1 | unlimited | 1 | 4 |
| maggie | VPS1 | unlimited | 1 | 3 |
| terry | VPS1 | unlimited | 1 | 3 |
| vivian | VPS1 | unlimited | 1 | 3 |
| edith | VPS1 | unlimited | 1 | 3 |
| harry | VPS2 | unlimited | 1 | 3 |
| suzy | VPS2 | unlimited | 1 | 4 |
| frank | VPS2 | unlimited | 1 | 3 |
| rocky | VPS4 | unlimited | 1 | 3 |

## Retained configured connection and tool timeouts

| Agent | Setting | Value | Purpose |
| --- | --- | --- | --- |
| amanda | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| marsha | `channels.discord.voice.connectTimeoutMs` | 60000 | Detect a connection that cannot be established. |
| marsha | `plugins.entries.hindsight-openclaw.config.recallTimeoutMs` | 20000 | Return control when a memory lookup service stalls. |
| marsha | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| marsha | `tools.media.audio.timeoutSeconds` | 120 | Bound an individual external media-processing request. |
| victor | `plugins.entries.active-memory.config.timeoutMs` | 15000 | Return control when a memory lookup service stalls. |
| victor | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| wilma | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| grogar | `plugins.entries.hindsight-openclaw.config.recallTimeoutMs` | 20000 | Return control when a memory lookup service stalls. |
| grogar | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| gohzed | `plugins.entries.hindsight-openclaw.config.recallTimeoutMs` | 20000 | Return control when a memory lookup service stalls. |
| gohzed | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| inga | `plugins.entries.hindsight-openclaw.config.recallTimeoutMs` | 20000 | Return control when a memory lookup service stalls. |
| inga | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| inga | `env.shellEnv.timeoutMs` | 5000 | Bound an individual external tool request; return a diagnosable error. |
| maggie | `plugins.entries.hindsight-openclaw.config.recallTimeoutMs` | 20000 | Return control when a memory lookup service stalls. |
| maggie | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| terry | `agents.defaults.mediaModels.video.timeoutMs` | 180000 | Bound an individual external media-processing request. |
| terry | `mcp.servers.percify.connectionTimeoutMs` | 10000 | Detect a connection that cannot be established. |
| terry | `mcp.servers.percify.requestTimeoutMs` | 180000 | Bound an individual external tool request; return a diagnosable error. |
| terry | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| vivian | `agents.defaults.mediaModels.video.timeoutMs` | 180000 | Bound an individual external media-processing request. |
| vivian | `mcp.servers.percify.connectionTimeoutMs` | 10000 | Detect a connection that cannot be established. |
| vivian | `mcp.servers.percify.requestTimeoutMs` | 180000 | Bound an individual external tool request; return a diagnosable error. |
| vivian | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| edith | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| harry | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| suzy | `plugins.entries.hindsight-openclaw.config.recallTimeoutMs` | 20000 | Return control when a memory lookup service stalls. |
| suzy | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| frank | `plugins.entries.hindsight-openclaw.config.recallTimeoutMs` | 20000 | Return control when a memory lookup service stalls. |
| frank | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| rocky | `secrets.providers.onepassword_openrouter.timeoutMs` | 15000 | Bound an individual external tool request; return a diagnosable error. |
| rocky | `secrets.providers.onepassword_telegram.timeoutMs` | 15000 | Bound an individual external tool request; return a diagnosable error. |
| rocky | `secrets.providers.onepassword_slack_app.timeoutMs` | 15000 | Bound an individual external tool request; return a diagnosable error. |
| rocky | `secrets.providers.onepassword_slack_bot.timeoutMs` | 15000 | Bound an individual external tool request; return a diagnosable error. |
| rocky | `agents.defaults.mediaModels.video.timeoutMs` | 600000 | Bound an individual external media-processing request. |
| rocky | `mcp.servers.percify.connectionTimeoutMs` | 10000 | Detect a connection that cannot be established. |
| rocky | `mcp.servers.percify.requestTimeoutMs` | 180000 | Bound an individual external tool request; return a diagnosable error. |
| rocky | `mcp.servers.canva.requestTimeoutMs` | 60000 | Bound an individual external tool request; return a diagnosable error. |
| rocky | `mcp.servers.gemini-video.requestTimeoutMs` | 600000 | Bound an individual external tool request; return a diagnosable error. |
| rocky | `plugins.entries.hindsight-openclaw.config.recallTimeoutMs` | 60000 | Return control when a memory lookup service stalls. |

## Script file register

- `continuous_edith.py` — changed; original preserved at `timer-audit-backups-20260926\continuous_edith.py`.
- `install_continuous_edith.py` — changed; original preserved at `timer-audit-backups-20260926\install_continuous_edith.py`.
- `edith_natural_test.py` — changed; original preserved at `timer-audit-backups-20260926\edith_natural_test.py`.
- `.agents\quality-remediation\project-dispatch.py` — changed; original preserved at `timer-audit-backups-20260926\.agents_quality-remediation_project-dispatch.py`.
- `.agents\quality-remediation\amanda-project-dispatch.py` — changed; original preserved at `timer-audit-backups-20260926\.agents_quality-remediation_amanda-project-dispatch.py`.
- `.agents\quality-remediation\ruby-review-defer.py` — changed; original preserved at `timer-audit-backups-20260926\.agents_quality-remediation_ruby-review-defer.py`.
- `.agents\ruby-review-defer.py` — changed; original preserved at `timer-audit-backups-20260926\.agents_ruby-review-defer.py`.
- `D:\Google Drive\Documents\Codex-Projects\Asana-Organization\fast_continuation.py` — changed; original preserved at `D:\Google Drive\Documents\Codex-Projects\Asana-Organization\timer-audit-backups-20260926\c1a0ee760bc6-fast_continuation.py`.
- `D:\Google Drive\Documents\Codex-Projects\Asana-Organization\.agents\quality-remediation\project-dispatch.py` — changed; original preserved at `D:\Google Drive\Documents\Codex-Projects\Asana-Organization\timer-audit-backups-20260926\fdf685d582d0-project-dispatch.py`.
- `D:\Google Drive\Documents\Codex-Projects\VPS1-Agents-Hostinger-gemini-video\docker\asana-http-mcp\deploy\edith\project-dispatch.py` — changed; original preserved at `D:\Google Drive\Documents\Codex-Projects\Asana-Organization\timer-audit-backups-20260926\8f886bae0a18-project-dispatch.py`.
- `D:\Google Drive\Documents\Codex-Projects\VPS1-Agents-Hostinger-gemini-video\docker\asana-http-mcp\deploy\edith\continuous-work\install_continuous_edith.py` — changed; original preserved at `D:\Google Drive\Documents\Codex-Projects\Asana-Organization\timer-audit-backups-20260926\59cdb5d9b484-install_continuous_edith.py`.
- `D:\Google Drive\Documents\Codex-Projects\VPS1-Agents-Hostinger-gemini-video\docker\asana-http-mcp\deploy\edith\continuous-work\continuous_edith.py` — changed; original preserved at `D:\Google Drive\Documents\Codex-Projects\Asana-Organization\timer-audit-backups-20260926\aa2e06d9d66d-continuous_edith.py`.
- `D:\Google Drive\Documents\Codex-Projects\VPS1-Agents-Hostinger-gemini-video\docker\asana-http-mcp\deploy\edith\amanda-project-dispatch.py` — changed; original preserved at `D:\Google Drive\Documents\Codex-Projects\Asana-Organization\timer-audit-backups-20260926\0f005ea088d6-amanda-project-dispatch.py`.
- `D:\Google Drive\Documents\Codex-Projects\Github\harry-imap-fix\docker\asana-http-mcp\deploy\edith\project-dispatch.py` — changed; original preserved at `D:\Google Drive\Documents\Codex-Projects\Asana-Organization\timer-audit-backups-20260926\61b354b2fe27-project-dispatch.py`.
- `D:\Google Drive\Documents\Codex-Projects\Github\harry-imap-fix\docker\asana-http-mcp\deploy\edith\continuous-work\install_continuous_edith.py` — changed; original preserved at `D:\Google Drive\Documents\Codex-Projects\Asana-Organization\timer-audit-backups-20260926\7f5c36743ba8-install_continuous_edith.py`.
- `D:\Google Drive\Documents\Codex-Projects\Github\harry-imap-fix\docker\asana-http-mcp\deploy\edith\continuous-work\continuous_edith.py` — changed; original preserved at `D:\Google Drive\Documents\Codex-Projects\Asana-Organization\timer-audit-backups-20260926\f9c82b1c055a-continuous_edith.py`.
- `D:\Google Drive\Documents\Codex-Projects\Github\harry-imap-fix\docker\asana-http-mcp\deploy\edith\amanda-project-dispatch.py` — changed; original preserved at `D:\Google Drive\Documents\Codex-Projects\Asana-Organization\timer-audit-backups-20260926\921fa7a5a5da-amanda-project-dispatch.py`.

Live scripts changed: Edith `continuous_edith.py`, `edith-project-dispatch.py`, `edith_natural_test.py`, `edith_natural_test_fresh.py`, `fast_continuation.py`, plus private recovery `run.py` and `run-attempt2.py`; Amanda `amanda-project-dispatch.py`; Ruby `ruby-review-defer.py`. Backups are under the corresponding workspace timer-removal-backup-20260926 directories or beside the private recovery scripts.

## Evidence files

- Agent-Timer-Removal-Register.csv — every OpenClaw before/after setting and job ID.
- agent-timer-audit-before.json and agent-timer-audit-after.json — filtered non-secret inventory.
- agent-timer-changes.jsonl — change receipts, including initially failed attempts.
- ruby-timer-changes.json and ruby-legacy-reset-removal.json.
- local-timer-script-changes.json, historical-script-timer-changes.json and remote-script-timer-changes.jsonl.
- agent-timer-policy-changes.jsonl — all 16 policy read-backs.

