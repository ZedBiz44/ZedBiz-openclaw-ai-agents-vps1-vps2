# 2026-09-07 - Feature Change - Frank Whisper API Key Repair

## Summary

- **Date:** 2026-09-07 Mountain Time
- **Added By:** Cody
- **System:** VPS2 and OpenClaw
- **Feature Status:** Tested

## Feature Purpose

- This repair makes Frank's `openai-whisper-api` skill use the dedicated `OPENAI_WHISPER_API_KEY`.
- It prevents Frank from sending an unresolved 1Password reference to OpenAI as though it were an API key.

## Implementation Notes

- Added the dedicated `OPENAI_WHISPER_API_KEY` reference to `/root/.openclaw-frank/.env`.
- Removed Frank's redundant `zcode-allocator.conf` systemd drop-in because it loaded unresolved secret references before the existing `op run` wrapper.
- Added a durable workspace override at `/root/.openclaw-frank/workspace/skills/openai-whisper-api`.
- Changed the skill requirement and script to use only `OPENAI_WHISPER_API_KEY`.
- Restored executable permission on `scripts/transcribe.sh`.
- Reloaded systemd and restarted only `openclaw-frank`.
- Harry and Suzy were not changed.

## Verification

- Frank's service returned active after restart.
- The final OpenClaw gateway child process received a resolved dedicated key whose safe fingerprint matched the 1Password value.
- `openclaw skills info openai-whisper-api --agent main` reported Ready, visible, and available from the workspace skill path.
- The script rejected a test with `OPENAI_WHISPER_API_KEY` removed, proving there is no fallback to `OPENAI_API_KEY`.
- A live `gpt-4o-mini-transcribe` API request completed successfully.
- A fresh isolated Frank session discovered and executed the repaired skill, created the transcript file, and returned `PASS`.
- `openclaw config validate` passed with one unrelated existing disabled-plugin warning.
- The OpenClaw platform checks and Bash syntax check passed. The shared-skill validator was not used as the release gate because this is an intentionally OpenClaw-specific package with required OpenClaw metadata.
- No secret value was printed, saved in this repository, or added to GitHub or Notion.

## Rollback Note

- Restore `/root/.openclaw-frank/.env.bak-whisper-api-20260907T093745-0600` to `/root/.openclaw-frank/.env`.
- Restore `/etc/systemd/system/openclaw-frank.service.d/zcode-allocator.conf.bak-whisper-api-20260907T093745-0600` to `zcode-allocator.conf`.
- Remove `/root/.openclaw-frank/workspace/skills/openai-whisper-api`.
- Run `systemctl daemon-reload`, restart `openclaw-frank`, and repeat the live checks.

## Links

- GitHub Issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/277
- Notion page: https://app.notion.com/p/3d4a3e33d58181499fa1d70e2b6a8f71
- Related commit: Added by the repair branch.

