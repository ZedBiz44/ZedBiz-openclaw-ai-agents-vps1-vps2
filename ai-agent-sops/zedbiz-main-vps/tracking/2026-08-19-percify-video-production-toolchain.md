# 2026-08-19 - Percify Voice And Video Assembly Toolchain

## Current Status: Replaced And Retired On 2026-08-27

- The standalone `z-percify-voice-production` wrapper is retired from Terry and Vivian and removed from this repository.
- `z-audio-production` and `z-video-production` are the current canonical workflows. They retain Percify as an approved underlying provider while covering discovery, schema checks, credit controls, consent, audio quality, avatar/lip-sync ownership, and audio-to-video handoff.
- The `percify` MCP configuration remains enabled for Terry and Vivian. Only the redundant skill wrapper was removed.
- Post-removal verification confirmed both agents retain ready `z-audio-production` and `z-video-production` skills plus the configured `percify` MCP route.
- Technical record: [GitHub issue #201](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/201).

The remainder of this document is the original 2026-08-19 rollout record.

## Summary

- **Date:** 2026-08-19 Mountain Time
- **Added By:** Cody
- **Systems:** VPS1 OpenClaw and VPS4 OpenClaw
- **Agents Verified:** Vivian, Terry, Rocky
- **Status:** Tested

## Purpose

- Give the agents a secure Percify connection for voice, avatar, lip-sync, and other media jobs.
- Give VAs a reusable Percify voice-production skill instead of requiring them to know raw API calls.
- Give agents a reusable Remotion assembly template for scenes, narration, music, logos, and animated captions.
- Ensure FFmpeg has working `drawtext` support as a practical fallback for captions and labels.

## Files And Configuration

- `skills/z-percify-voice-production/SKILL.md`
- `skills/z-percify-voice-production/references/percify-voice-workflows.md`
- `docs/templates/zedbiz-remotion-video/`
- `scripts/install-zedbiz-video-ffmpeg.sh`
- Percify credentials remain in each agent's approved 1Password vault and are resolved into runtime environment variables; no credential value is committed.
- The MCP connector exposes only the approved Percify discovery, cost-estimation, generation, monitoring, and avatar tools.

## Verification

- Vivian: Percify model listing, balance lookup, model lookup, and cost estimate succeeded. Balance reported 3,000 credits and no credits were consumed.
- Terry: Percify model listing succeeded and returned 18 available media models. No credits were consumed.
- Rocky: Percify model listing succeeded through the live MCP connector. No credits were consumed.
- All three agents report `z-percify-voice-production` as eligible.
- All three agents passed an FFmpeg `drawtext` render.
- All three agents rendered the Remotion smoke-test video successfully.
- Vivian and Terry use the pinned shared BtbN FFmpeg build. Rocky's existing packaged FFmpeg already included `drawtext`.
- Ruby was intentionally excluded from final verification because separate work was in progress on her runtime.

## Rollback

- Remove or disable the `percify` MCP entry from the affected agent configuration.
- Remove the per-agent `z-percify-voice-production` skill folder.
- Remove the deployed Remotion template folder if assembly support is no longer wanted.
- On VPS1, restore the dated FFmpeg backup under `/opt/openclaw/shared/bin/` and recreate the affected containers so the bind mount uses the restored binary.

## Links

- **GitHub Issue:** `ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2#155`
- **Notion Main Page:** `https://www.notion.so/3c1a3e33d581812dbce0f627a558e8e4`
