# 2026-09-14 | Ruby | Notion MCP writes auto-declined after Gemini video `--approval auto`

## Summary

- **Date:** 2026-09-14 Mountain Time
- **Added By:** Ruby
- **Systems:** VPS1 Docker OpenClaw, VPS2 native OpenClaw, Notion Codex MCP, Gemini video MCP
- **GitHub issue:** https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/350
- **Status:** Repair applied. Stay-fixed docs and scripts updated.

## Cause

On OpenClaw 2026.9.4, `mcp.servers.gemini-video.codex.defaultToolsApprovalMode=auto` (from the 2026-09-09 video MCP wiring / `openclaw mcp add ... --approval auto`) turns on global MCP elicitations. Interactive Codex Notion writes were auto-declined as `user rejected MCP tool call`. No approve button was created. Reads still worked. Scheduled 6 AM journals used a never-ask path and still wrote.

This was not a dead Notion OAuth login.

## Fix applied (live agents)

Remove **only** `gemini-video.codex.defaultToolsApprovalMode`. Keep the `gemini-video` MCP server. Do not re-login to Notion. No further settings changes or restarts after this record.

## Stay-fixed (so a rebuild cannot put it back)

- `scripts/deploy-gemini-video-terry.sh` — `--approval auto` removed
- `scripts/deploy-gemini-video-harry.sh` — `--approval auto` removed
- `scripts/deploy-gemini-video-rocky.sh` — `--approval auto` removed
- `services/z-gemini-video-mcp/README.md` — install rule recorded
- Notion Gemini Video Fleet Setup SOP — rule recorded
- VPS1 Agent Creation SOP docs — rule recorded

After any future video install or OpenClaw rebuild, confirm live `openclaw.json` has no `defaultToolsApprovalMode` under `mcp.servers.gemini-video`.

## Verification vs change-only

Jack confirmed no extra restarts are needed. This table is the honest record.

### Passed live verification (named tests)

| Agent | Host | Change applied | Notion write + read-back | Gemini video check |
| --- | --- | --- | --- | --- |
| Amanda | VPS1 | Yes | Passed. Jack confirmed a Notion journal write published. | Passed. Jack confirmed the video analysis still worked. |

Amanda was the only named agent given both tests before fleet rollout.

### Change applied only (flag removed + managed restart; no named per-agent Notion write/read-back in this record)

VPS1: Marsha, Victor, Wilma, Inga, GohZed, Grogar, Maggie, Vivian, Terry, Edith

VPS2: Frank, Harry, Suzy

Jack later confirmed the fleet works after that rollout. That is a fleet-level confirm, not a per-agent Notion write/read-back log.

### Not in this OpenClaw change

Ruby (Hermes / VPS3). Ruby writes Notion through her own connection.

## What was not done

- No connected-app policy change.
- No Notion re-login.
- No video MCP uninstall.
- No extra restarts after Jack confirmed the repair.

## Links

- Issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/350
- Gemini SOP: https://app.notion.com/p/3d4a3e33d581817695a9cbea1aa655c5
- VPS1 Agent Creation SOP: https://app.notion.com/p/f24a3e33d5818256accd0185fe925af2
\n