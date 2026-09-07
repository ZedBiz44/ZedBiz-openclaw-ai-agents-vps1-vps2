# 2026-09-07 | Cody | Gemini Video Analysis Pilot

## Summary

- **Date:** 2026-09-07 Mountain Time
- **Added By:** Cody
- **Agents:** Terry first, then Harry and Rocky
- **Systems:** VPS1, VPS2, VPS4, OpenClaw, Gemini API, 1Password
- **Status:** Live and verified on all three agents

## Purpose

Give approved ZedBiz agents a reusable tool that can watch a public YouTube video, understand the audio and visible content, answer questions, and return useful timestamps.

## Approved Inputs

- Google account: `jzedbiz@gmail.com`
- Google project: `zedbiz-gemini-video`
- Secret reference: `op://openclaw-agents-shared/gemini-video-api-key/credential`
- Public test video: `https://www.youtube.com/watch?v=eylReF4JPT0`
- Jack confirmed that prepaid credits were purchased.

No secret value is stored in this repository or record.

## Files

- `services/z-gemini-video-mcp/`
- `skills/z-video-analysis/SKILL.md`
- `tracking/main-vps/2026-09-07-gemini-video-analysis-pilot.md`

## Safety

- Terry was tested first. Harry and Rocky were changed only after Terry passed.
- The MCP tool accepts public HTTPS YouTube URLs only.
- The Interactions API request uses `store: false`.
- An ambiguous submitted request is not automatically repeated.
- Existing agent configuration is backed up before change.

## Test Record

### Package checks

- Six local automated tests passed.
- `npm audit` reported zero known vulnerabilities.
- The Skill package validator passed.

### Terry — Passed

- Runtime: VPS1 Docker agent, OpenClaw `2026.8.2`.
- The existing `op run` startup route resolved `GEMINI_API_KEY` without printing it.
- MCP discovery returned `gemini-video__analyze_youtube_video` with no diagnostic errors.
- One live agent call inspected the full `00:00–17:30` test video.
- Gemini usage: 95,806 input tokens, 3,699 output tokens, 859 thought tokens, no cached tokens.
- Retries: zero.

### Harry — Passed

- Runtime: VPS2 native systemd agent, OpenClaw `2026.8.2`.
- Harry's existing 1Password account already had access to the shared Gemini item.
- MCP discovery returned `gemini-video__analyze_youtube_video` with no diagnostic errors.
- One live agent call inspected the full `00:00–17:30` test video.
- Gemini usage: 95,727 input tokens, 3,241 output tokens, 162 thought tokens, no cached tokens.
- Retries: zero.

### Rocky — Passed after configuration repair

- Runtime: VPS4 native user service, OpenClaw `2026.8.2`.
- Rocky's existing 1Password account already had access to the shared Gemini item.
- The first request was rejected with HTTP 400 because a recovery command had saved an apostrophe instead of the environment placeholder. It did not inspect the video and returned no Gemini usage.
- The placeholder was corrected to `${GEMINI_API_KEY}` and Rocky's Gateway was restarted.
- The next live agent call inspected the full `00:00–17:30` test video.
- Gemini usage: 95,700 input tokens, 3,433 output tokens, 839 thought tokens, no cached tokens.
- Successful live-analysis retries after the configuration repair: one.

### Result quality

All three successful reports:

- identified the visible WordPress tools and dashboards;
- separated what was shown from what the presenter claimed;
- marked sales, speed, and performance claims as unverified;
- included useful timestamps and ZedBiz actions; and
- reported the model and available usage data.

No video file was uploaded or downloaded. The source remained on YouTube, and every successful Interactions API request used `store: false`.

## Rollback

Restore the timestamped pre-change files, remove only the new Gemini tool and Skill folders, and restart each agent through its normal protected service.

- Terry backup: `/opt/openclaw/agents/terry/backups/20260907T192003Z-gemini-video`
- Harry backup: `/root/.openclaw-harry/backups/20260907T193415Z-gemini-video`
- Rocky backup: the timestamped `*-gemini-video` folder under `/home/openclaw/.openclaw/backups/` created before the first Rocky install attempt.

The tracked Terry rollback script is `scripts/rollback-gemini-video-terry.sh`. Harry and Rocky must be restored through their native systemd startup routes rather than Terry's Docker route.

## Links

- GitHub issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/286
- Notion SOP: https://app.notion.com/p/3d4a3e33d581817695a9cbea1aa655c5
