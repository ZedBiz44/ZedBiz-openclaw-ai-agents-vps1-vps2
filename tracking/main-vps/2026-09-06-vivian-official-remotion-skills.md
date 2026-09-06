# 2026-09-06 - Skill Added - Official Remotion Agent Skills

## Summary

- **Date:** 2026-09-06 Mountain Time
- **Added By:** Cody
- **Agent Receiving Skill:** Vivian
- **VPS:** main-vps / VPS1
- **Status:** tested and live on Vivian

## Skill Purpose

- Give Vivian the complete official Remotion guidance package for creating, marking up,
  previewing, rendering, captioning, upgrading, and maintaining Remotion video projects.
- Keep `z-video-production` and `z-audio-production` as the controlling ZedBiz workflows.

## Setup Details

- Canonical folder: `skills/remotion-official/`
- Live destination: `/opt/openclaw/agents/vivian/workspace/skills/`
- Upstream: `remotion-dev/remotion`, package `packages/skills`
- Upstream commit: `670b222bf46c4d73e590f0995c28b7dc43221953`
- Package version: `4.0.521`
- Files: twelve official skill folders plus `UPSTREAM.md`
- Compatibility corrections: removed the optional upstream `version` frontmatter
  field to match the shared OpenClaw skill contract, and changed sibling links from
  `./remotion-*` to `../remotion-*` where required. Removed eleven Git symlink
  placeholders that Windows checked out as plain text files.
- Dependencies: existing Node.js, Remotion project dependencies, FFmpeg, and OpenClaw.

## Commands Used

- Cloned the official Remotion repository with sparse checkout of `packages/skills`.
- Reviewed all 117 package files and searched for shell, network, credential, and paid-provider instructions.
- Copied the twelve skill folders into this repository.
- Deployed the folders into Vivian's mounted workspace skill directory.
- Used `openclaw skills --agent main` for discovery checks and a fresh local agent session for routing verification.

## Test Result

- Shared skill validator: all twelve skills passed.
- Live OpenClaw check: twelve `remotion-*` skills were eligible, model-visible,
  command-visible, unblocked, and had no missing requirements.
- Fresh-session route test: Vivian read `remotion-best-practices`, its provenance
  record, and `remotion-render`; she correctly returned version `4.0.521`, upstream
  commit `670b222bf46c4d73e590f0995c28b7dc43221953`, and no paid-provider approval for
  the read-only test.
- Local render proof: rendered frames 0-29 from the existing `ReviewRipple`
  composition to `workspace/tmp/remotion-skills-proof/vivian-remotion-proof.mp4`.
- Media verification: FFmpeg decoded the file without errors. Output was H.264
  video with AAC audio, 720x1280, 9:16, 50 fps, and 0.66 seconds for the 30-frame test.
- Visual verification: opening, middle, and closing frames rendered clearly with
  expected text, rating stars, review card, and presenter overlay.
- Spend: no Percify or other paid media provider was called.

## Failed Attempts and Corrections

- The first Linux staging extraction inherited Windows read-only flags and stopped
  before any files reached Vivian. Retried with ZIP extraction inside a temporary
  Alpine container to normalize permissions.
- The first container ownership command ran as the normal `node` user and could not
  change ownership. Retried as container root, then verified Vivian could read the files.
- Windows checked upstream router symlinks out as plain text placeholders. Removed
  them and used validated `../remotion-*` links to the sibling skill folders.
- The first fresh-session test correctly loaded the skills but could not report the
  package version after OpenClaw-required frontmatter normalization. Added a provenance
  record inside the router folder and the second fresh-session test passed.

## Known Limitations

- These are AI instructions, not a replacement video editor or API connection.
- Some optional examples mention AWS, Vercel, MapTiler, ElevenLabs, or remote media.
  Those services are not authorized merely because this package is installed.
- Remotion licensing depends on organization size and use; review the current official license before commercial production.

## SOP Impact

- No ZedBiz production SOP changed. The package adds specialist Remotion guidance under the existing video/audio controls.

## Rollback Note

- Remove only the twelve `remotion-*` folders from Vivian's workspace skills directory.
- Start a fresh OpenClaw session and verify `openclaw skills --agent main list --json`
  no longer reports those names.

## Links

- Official docs: https://www.remotion.dev/docs/ai/skills
- Upstream package: https://github.com/remotion-dev/remotion/tree/main/packages/skills
- GitHub Issue: Not created; this tracking record is the primary technical record.
- Notion page: Existing 2026-09-06 Cody daily journal entry.
- Related branch: `codex/vivian-remotion-official-skills`
- Related commit: the commit containing this tracking record and `skills/remotion-official/`
