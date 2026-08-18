# 2026-08-18 - Feature Change - VPS1 Assignment Continuity Standard

## Summary

- **Date:** 2026-08-18 Mountain Time
- **Added By:** Cody
- **System:** main-vps, OpenClaw 2026.7.1
- **Feature Status:** tested and live

## Feature Purpose

- Standardizes immediate assignment acknowledgement on the proven Inga behavior.
- Prevents a separate written pre-work acknowledgement from ending a Codex/OpenClaw turn before substantive work begins.

## Implementation Notes

- Live file changed for every VPS1 agent: `/home/node/.openclaw/workspace/AGENTS.md`
- Agents: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma
- Reusable script: `ai-agent-sops/shared-scripts/configure-assignment-continuity.mjs`
- The script creates a timestamped sibling backup before writing and rolls back automatically if its managed-block checks fail.
- Removed conflicting or partial acknowledgement rules, including Amanda's Telegram instruction to use the `message` tool for every reply.
- No containers were restarted because OpenClaw reads the workspace policy for each new turn.

## Canonical Rule

```markdown
<!-- zedbiz-assignment-continuity:start -->
- Rely on the platform acknowledgement reaction for immediate receipt. Do not send a separate "I'm on it" acknowledgement message.
- Begin the assignment immediately. Send a written progress update only after substantive work has started, and always continue the same assignment after sending it.
- Let the platform manage its configured acknowledgement reaction; do not duplicate it with a manual reaction or empty text reply.
<!-- zedbiz-assignment-continuity:end -->
```

## Verification

- Wilma was the required one-agent pilot.
- Controlled fresh session `continuity-pilot-o6box0km` completed one `bash` tool call, returned `WILMA_CONTINUITY_OK`, made no acknowledgement-message call, reported zero tool failures, and completed normally.
- All eleven VPS1 agents contain one identical managed block with SHA-256 `516516708cb9d62e78d9295055f9cb7837e6d3fe897008fd0160476cd2b87597`.
- All eleven returned zero matches for the removed conflicting pre-work acknowledgement rules.
- All eleven retain `messages.ackReactionScope = all`.
- All eleven agent containers and Asana sidecars remained healthy.

## Rollback Note

- Each live file has a sibling `AGENTS.md.bak-assignment-continuity-*` backup.
- Restore the newest applicable backup for that agent. No restart is normally required; verify with a fresh controlled turn.

## Links

- GitHub Issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/148
- Notion page: https://app.notion.com/p/3c0a3e33d581812dbdb8c3d7e5bf93eb
