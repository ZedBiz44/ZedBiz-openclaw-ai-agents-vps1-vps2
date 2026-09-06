# 2026-09-06 - Skill Added - Official Remotion Agent Skills on Rocky

## Summary

- Date: 2026-09-06 Mountain Time
- Added By: Cody
- Agent Receiving Skills: Rocky
- VPS: VPS4 / `srv1849801`
- Status: tested and live on Rocky

## Skill Purpose

- Give Rocky the same complete official Remotion guidance package already tested on Vivian.
- Keep `z-video-production` and `z-audio-production` as the controlling ZedBiz production workflows.

## Source and Installation

- Approved source folder: `skills/remotion-official/`
- Live destination: `/home/openclaw/.openclaw/workspace/skills/`
- Upstream: `remotion-dev/remotion`, package `packages/skills`
- Upstream commit: `670b222bf46c4d73e590f0995c28b7dc43221953`
- Package version: `4.0.521`
- Installed folders: all twelve `remotion-*` skills
- Archive SHA-256: `95a0b4dc5d579e404e24690f7c6d2b97826181a61e7f286f7089dbe8c252a268`
- Owner and permissions: `openclaw:openclaw`; folders `755`; files `644`

## Verification

- Rocky was running OpenClaw `2026.8.2`; his user Gateway remained active.
- Before installation, the live workspace contained zero `remotion-*` skill folders.
- After installation, `openclaw skills --agent main check --json` reported all twelve skills as eligible, model-visible, command-visible, unblocked, and without missing requirements.
- A fresh Rocky session loaded all twelve skills into its prompt.
- For a build-and-render request, Rocky selected `remotion-best-practices` and `remotion-render`, read their installed files and provenance record, and returned package version `4.0.521` and the correct upstream commit.
- The fresh-session run used Rocky's normal `xai/grok-4.6` route and completed with zero tool failures.

## Local Render Proof

- Existing project: `/home/openclaw/.openclaw/workspace/video-production/zedbiz-remotion-video`
- `npm run typecheck` passed.
- Remotion rendered the existing sixty-frame smoke composition locally without calling Percify or another media-generation provider.
- FFmpeg decoded the output without errors.
- Output: H.264 video plus AAC stereo audio, `360x640`, vertical format, `30 fps`, `2.048` seconds, `124446` bytes.
- Output SHA-256: `afb18e5862e56672cb0a85f7285c96f58271144082dfc17181d737e3575c244e`
- A middle frame was visually checked and clearly displayed `ZedBiz video template is working`.

## Failed Attempts and Corrections

- The stored VPS4 key file includes inventory text before its private-key block. SSH rejected the complete file, so a restricted temporary runtime copy containing only the key block was used. The stored key was not changed.
- Rocky does not have the `unzip` command. The first extraction stopped before copying any live skills. The existing Python ZIP extractor was used instead; no new package was installed.
- A plain administrative shell did not include Rocky's OpenClaw installation on `PATH`. The verified executable at `/home/openclaw/.npm-global/bin/openclaw` was used under the `openclaw` account.

## Boundaries and Rollback

- No paid media provider was called.
- Vivian was not changed during this rollout.
- These skills provide Remotion instructions; they do not replace Remotion or add a separate editing API.
- To roll back, remove only the twelve `remotion-*` folders from `/home/openclaw/.openclaw/workspace/skills/`, start a fresh session, and verify those names are no longer reported.

## Links

- Official docs: https://www.remotion.dev/docs/ai/skills
- Upstream package: https://github.com/remotion-dev/remotion/tree/main/packages/skills
- Vivian rollout: `tracking/main-vps/2026-09-06-vivian-official-remotion-skills.md`

