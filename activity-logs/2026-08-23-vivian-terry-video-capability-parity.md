# Vivian and Terry Video Capability Parity

Date: 2026-08-23  
Author: Cody  
Status: Complete

## Purpose

Bring Vivian and Terry on VPS1 to the same practical video-production execution level as Rocky: native file and shell tools, local FFmpeg assembly and inspection, browser/image/video tools, and live Percify MCP tools.

## Root Cause

Both agents already had `tools.profile: full`, the video skill, FFmpeg, Chromium, provider credentials, and a Percify server entry. Their OpenAI models were explicitly pinned to the Codex agent runtime, which replaces OpenClaw's native execution and MCP tool layer. The VPS1 OpenClaw image also lacked support for the required Percify `streamable-http` transport.

## Changes

- Added `docker/Dockerfile.openclaw-refresh` to preserve the ZedBiz base image tools while refreshing `/app` from the supported upstream OpenClaw image.
- Built the VPS1-local image `zedbiz/openclaw-base:2026.7.1-2-video`.
- Updated Terry and Vivian to use that image.
- Set the OpenAI Sol, Terra, and Luna model entries to `agentRuntime.id: openclaw`.
- Set Percify transport to `streamable-http`.
- Restarted each agent through its normal 1Password-backed launcher.
- No paid media generation was submitted.

## Verification

### Terry

- Container: running and healthy.
- Fresh agent harness: `openclaw`.
- Native tools present: `read`, `edit`, `write`, `apply_patch`, `exec`, and `process`.
- Creative tools present: image generation and video generation.
- Percify probe: 11 approved tools, no diagnostics.
- Live agent proof: `TERRY_PARITY_OK`.
- Terry personally rendered, inspected, and deleted a one-second H.264/AAC test video and completed a read-only Percify avatar-list call with zero tool failures.

### Vivian

- Container: running and healthy.
- Fresh agent harness: `openclaw`.
- Native tools present: `read`, `edit`, `write`, `apply_patch`, `exec`, and `process`.
- Creative tools present: image generation and video generation.
- Percify probe: 11 approved tools, no diagnostics.
- Live agent proof: `VIVIAN_PARITY_OK`.
- Vivian personally rendered, inspected, and deleted a one-second H.264/AAC test video and completed a read-only Percify avatar-list call with zero tool failures.

## Backups and Rollback

Backups are stored on VPS1 under:

- `/opt/openclaw/agents/terry/backups/20260823T233555Z-video-capability-activation/`
- `/opt/openclaw/agents/vivian/backups/20260823T233555Z-video-capability-activation/`

Rollback:

- Restore each backed-up `openclaw.json` and `.env`.
- Restart through `op-start-terry.sh restart` or `op-start-vivian.sh restart`.
- Re-run config validation, container health, fresh-session tool inventory, and a no-spend proof.
