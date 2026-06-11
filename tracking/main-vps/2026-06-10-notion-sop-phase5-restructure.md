# Notion SOP Phase 5 Restructure + Docker Base Image Update

**Date:** 2026-06-10 MDT
**Author:** Manus
**Session Type:** Documentation / Architecture Clarification

---

## What Was Done

### Phase 5 Renamed to "OpenClaw Version Upgrades"
The VPS1 SOP database Phase 5 has been renamed from its previous label to "OpenClaw Version Upgrades" to clearly scope all update and upgrade procedures under one phase group.

### Phase 5.1 -- OpenClaw Update Procedure (VPS1)
Notion page: https://app.notion.com/p/37ba3e33d581816584cdf6b622a0d944

Completely rewrote the update procedure to reflect the actual architecture:
- Added critical architecture warning at the top: agents run `ghcr.io/zedbiz44/openclaw-base:latest`, NOT the official image directly
- Replaced the incorrect `docker compose pull` workflow with the correct Dockerfile rebuild workflow
- 8-step procedure: update Dockerfile in GitHub > pull to VPS > rebuild image > update .env if needed > restart test agent > verify > run doctor > fleet rollout
- Retained all safety rules, ownership rules, pre-restart checklist, post-restart verification, fleet rollout rule, and version-specific notes
- Added cross-reference link to Phase 5.2 Docker Base Image Creation page

### Phase 5.2 -- Docker Base Image Creation
Notion page: https://app.notion.com/p/376a3e33d5818094855ad5479fa056ba

Updated the page to reflect current state:
- Removed stale "Test" section at top
- Updated tool count from 17 to 18 (added `debugpy`)
- Added `debugpy` to the tools table (Python debugging for remote attach, added per OpenClaw 2026.5.x Python Debugging Skill)
- Added note about `OPENCLAW_IMAGE_PIP_PACKAGES` and `OPENCLAW_IMAGE_APT_PACKAGES` as a new OpenClaw 2026.6.x feature
- Added cross-reference link back to Phase 5.1 Update Procedure
- Corrected image tag references to use `[version]` placeholder instead of hardcoded `2026.5.28`

---

## Architecture Clarification (Victor's Discrepancy)
Victor flagged that the SOP said to use `ghcr.io/openclaw/openclaw:2026.6.5` directly but all agents were running `ghcr.io/zedbiz44/openclaw-base:latest`. This was investigated and confirmed:
- The ZedBiz base image IS the OpenClaw image -- it is `ghcr.io/openclaw/openclaw:[version]` with 18 extra tools layered on top via Dockerfile
- Switching agents to the official image directly would strip all custom tools
- Correct update path: bump `ARG OPENCLAW_VERSION` in Dockerfile.base, rebuild, restart agents
- The image is stored locally on VPS1 only (GHCR push still pending write:packages token)

---

## Tool Version Audit (Pending Next Build)
Compared current image tool versions against latest GitHub releases:

| Tool | Current | Latest |
|---|---|---|
| yt-dlp | 2026.03.17 | 2026.06.09 |
| rclone | 1.69.3 | 1.74.3 |
| gh | 2.74.1 | 2.94.0 |
| yq | 4.45.4 | 4.53.3 |
| pandoc | 3.7.0.2 | 3.10 |
| uv | 0.7.8 | 0.11.20 |
| glow | 2.1.0 | 2.1.2 |
| eza | 0.21.3 | 0.23.4 |
| duf | 0.8.1 | 0.9.1 |
| fzf | 0.62.0 | 0.73.1 |
| freeze | 0.1.6 | 0.2.2 |
| vhs | 0.9.0 | 0.11.0 |
| git-cliff | 2.9.0 | 2.13.1 |
| just | 1.40.0 | 1.52.0 |
| grex | 1.4.5 | 1.4.6 |
| gron | 0.7.1 | 0.7.1 (no change) |
| ffprobe | 7.0.2 | 7.0.2 (no change) |

New tool to add: `debugpy` 1.8.21 (Python debugging, referenced by OpenClaw Python Debugging Skill)

Dockerfile.base and agent rebuild are pending Jack's go-ahead.
