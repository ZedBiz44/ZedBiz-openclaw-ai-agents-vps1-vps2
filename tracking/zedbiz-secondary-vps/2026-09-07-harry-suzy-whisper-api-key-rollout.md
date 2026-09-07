# Harry and Suzy OpenAI Whisper Key Rollout

Date: 2026-09-07 MDT  
Added by: Cody  
Agents: Harry and Suzy  
VPS or system: VPS2, OpenClaw  
Related issue: #277  
Authoritative skill source: `skills/openai-whisper-api/`  
Skill source merge: #279, commit `33057a604c00e577ffb86c559594111f8f93a831`

## Purpose

Repair Harry and Suzy's OpenAI transcription skill so it uses the dedicated `OPENAI_WHISPER_API_KEY` credential instead of the general `OPENAI_API_KEY`.

## Files and Settings Changed

For each agent:

- Added the safe 1Password reference `op://openclaw-agents-shared/openai-whisper-key/credential` under `OPENAI_WHISPER_API_KEY` in the agent's protected `.env` file.
- Removed the redundant systemd drop-in that loaded unresolved secret references before the startup wrapper.
- Installed the approved workspace override at `~/.openclaw-<agent>/workspace/skills/openai-whisper-api/`.
- Set `scripts/transcribe.sh` executable.
- Restarted only the agent being repaired.

No API key value was printed or committed.

## Commands and Actions Used

- Verified the dedicated 1Password item through each service account using a one-way hash.
- Copied the approved skill files from the source merged in pull request #279.
- Ran `systemctl daemon-reload` and restarted `openclaw-harry`, then completed all checks before repeating the rollout for `openclaw-suzy`.
- Checked the final `openclaw-gateway` child process, not only the startup wrapper, to confirm both OpenAI variables resolved to real values.

## Test Results

Harry:

- Service active after restart.
- Workspace skill reported `Ready`, visible to the model, and available as a command.
- Primary environment variable reported as `OPENAI_WHISPER_API_KEY`.
- Missing-key test failed safely with `Missing OPENAI_WHISPER_API_KEY`.
- Real `gpt-4o-mini-transcribe` API request succeeded.
- Fresh OpenClaw agent session used the skill and replied `PASS`.
- Configuration validation passed. Two unrelated disabled-memory-plugin warnings remain.

Suzy:

- Service active after restart.
- Workspace skill reported `Ready`, visible to the model, and available as a command.
- Primary environment variable reported as `OPENAI_WHISPER_API_KEY`.
- Missing-key test failed safely with `Missing OPENAI_WHISPER_API_KEY`.
- Real `gpt-4o-mini-transcribe` API request succeeded.
- Fresh OpenClaw agent session used the skill and replied `PASS`.
- Configuration validation passed. One unrelated disabled-memory-plugin warning remains.

Both deployed `SKILL.md` and `transcribe.sh` files match the approved source hashes from pull request #279. No error-level service log entries appeared after the repair.

## Backups and Rollback

Harry backups:

- `/root/.openclaw-harry/.env.bak-whisper-api-20260907T100915-0600`
- `/etc/systemd/system/openclaw-harry.service.d/zcode-allocator.conf.bak-whisper-api-20260907T100915-0600`

Suzy backups:

- `/root/.openclaw-suzy/.env.bak-whisper-api-20260907T101422-0600`
- `/etc/systemd/system/openclaw-suzy.service.d/zcode-allocator.conf.bak-whisper-api-20260907T101422-0600`

There was no earlier workspace override to back up for either agent. To roll back, restore each agent's timestamped `.env` and systemd drop-in backup, remove only that agent's workspace override, run `systemctl daemon-reload`, and restart that agent.

## Result

Harry and Suzy now use the dedicated Whisper credential through `OPENAI_WHISPER_API_KEY`. Frank, Harry, and Suzy have each passed a real API request and a fresh-agent execution test.
