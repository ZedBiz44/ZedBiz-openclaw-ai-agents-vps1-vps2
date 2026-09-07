# VPS1 Fleet Dedicated Whisper API Rollout

Date: 2026-09-07 | Agent: Cody | Status: Resolved

## Purpose

Give every active VPS1 OpenClaw agent the approved `openai-whisper-api` workspace skill and route transcription billing through the dedicated `OPENAI_WHISPER_API_KEY` secret reference.

## Scope

- VPS: VPS1 at Hostinger
- Agents: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma
- Skill source: merged PR #279
- Marsha's earlier rollout record: merged PR #282
- Fleet workstream: issue #283

## What Changed

Each agent now has these approved workspace files:

- `/home/node/.openclaw/workspace/skills/openai-whisper-api/SKILL.md`
- `/home/node/.openclaw/workspace/skills/openai-whisper-api/scripts/transcribe.sh`
- `/home/node/.openclaw/workspace/skills/openai-whisper-api/UPSTREAM.md`

Each agent's OpenClaw configuration enables `skills.entries.openai-whisper-api`. The skill declares `OPENAI_WHISPER_API_KEY` as its primary environment variable. The secret value was not displayed, copied into GitHub, or written into the workspace skill.

## Approved File Evidence

- `SKILL.md` SHA-256: `eea5a6a23f4774f9ce3863a0dcf1980bcb1abd8e4fb3a3817d602d17d34b426c`
- `scripts/transcribe.sh` SHA-256: `22cbd52cc59af763209bc8dedec488781c69e6714144dffc45efa38ccf0247f8`
- `UPSTREAM.md` SHA-256: `008a9ae6ffc8d86d7c6a70887df02d8e852e46954abeb1c5ef27e4631ce0707e`
- Safely resolved dedicated-key fingerprint: `5685f55fecde`

The fingerprint proves the same dedicated secret resolved for each agent without exposing the API key.

## Verification

| Agent | Real API transcription | Fresh agent session | Tool failures | Config | Configured channels |
| --- | --- | --- | --- | --- | --- |
| Amanda | Pass | Pass | 0 | Valid | Pass |
| Edith | Pass | Pass | 0 | Valid | Pass |
| Gohzed | Pass | Pass | 0 | Valid | Pass |
| Grogar | Pass | Pass | 0 | Valid | Pass |
| Inga | Pass | Pass | 0 | Valid | Pass |
| Maggie | Pass | Pass | 0 | Valid | Pass |
| Marsha | Pass | Pass | 0 | Valid | Pass |
| Terry | Pass | Pass | 0 | Valid | Pass |
| Victor | Pass | Pass | 0 | Valid | Pass |
| Vivian | Pass | Pass | 0 | Valid | Pass |
| Wilma | Pass | Pass | 0 | Valid | Pass |

The real API check used `gpt-4o-mini-transcribe`. OpenClaw also reported the skill as an eligible `openclaw-workspace` skill, visible to the model and available as a command.

The final audit checked only configured channels. Marsha's Slack entry is not configured and was correctly excluded; her configured Discord and Telegram channels are running and pass their probes.

## Attempts And Corrections

- Amanda was completed with the initial restart-based procedure.
- Edith exposed a quoting problem in the first automation attempt. The change was rolled back.
- Two more Edith restart checks failed and were rolled back. Repeated restarts then tripped the restart-loop protection and stopped Discord.
- Edith's Discord channel was restored directly and verified running, connected, and probe-successful.
- Live OpenClaw documentation confirmed that `skills.*` changes hot-apply under hybrid reload mode and do not require a gateway restart.
- The fleet procedure was corrected to stage the test audio first, deploy the approved files, apply the configuration, verify the container start time was unchanged, then run the API, fresh-session, config, health, and channel tests.
- One temporary ffmpeg generation problem and one over-strict negative-test harness result caused safe rollbacks before the final procedure was used.
- The revised rollout completed Edith, Gohzed, Grogar, Inga, Maggie, Terry, Victor, Vivian, and Wilma without container restarts.
- Vivian logged one slow SQLite transaction warning during testing. Her transcription test, agent session, health, and configured channel checks still passed.

## Configuration Backups

- Amanda: `/home/node/.openclaw/openclaw.json.bak-whisper-api-20260907T103554-0600`
- Edith: `/home/node/.openclaw/openclaw.json.bak-whisper-api-norestart-20260907T105652-0600`
- Gohzed: `/home/node/.openclaw/openclaw.json.bak-whisper-api-norestart-20260907T105913-0600`
- Grogar: `/home/node/.openclaw/openclaw.json.bak-whisper-api-norestart-20260907T110018-0600`
- Inga: `/home/node/.openclaw/openclaw.json.bak-whisper-api-norestart-20260907T110119-0600`
- Maggie: `/home/node/.openclaw/openclaw.json.bak-whisper-api-norestart-20260907T110242-0600`
- Terry: `/home/node/.openclaw/openclaw.json.bak-whisper-api-norestart-20260907T110339-0600`
- Victor: `/home/node/.openclaw/openclaw.json.bak-whisper-api-norestart-20260907T110536-0600`
- Vivian: `/home/node/.openclaw/openclaw.json.bak-whisper-api-norestart-20260907T110632-0600`
- Wilma: `/home/node/.openclaw/openclaw.json.bak-whisper-api-norestart-20260907T110733-0600`
- Marsha: tracked in PR #282; her configuration was already enabled and the workspace override was the material rollout change.

## Rollback

For an agent deployed with the no-restart procedure:

- Restore that agent's listed `openclaw.json` backup.
- Remove only `/home/node/.openclaw/workspace/skills/openai-whisper-api`.
- Allow OpenClaw's hybrid watcher to apply the restored `skills.*` configuration.
- Re-run config, health, fresh-session, and configured-channel checks.

For Marsha, remove only the workspace override as recorded in PR #282. Do not remove or reveal the shared secret reference.

## Result

All eleven active VPS1 OpenClaw agents now use the dedicated `OPENAI_WHISPER_API_KEY` route for the `openai-whisper-api` skill. Live service health and configured communication channels remained operational.
