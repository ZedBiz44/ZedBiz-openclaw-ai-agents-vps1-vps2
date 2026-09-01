# VPS1 OpenClaw 2026.8.2 Full-Stack Update

Date: 2026-09-01 | Agent: Cody | Status: In Progress

## Authority And Scope

- Jack authorized Get-er-Done execution for the complete VPS1 OpenClaw fleet.
- Target OpenClaw release: exact stable `2026.8.2`, signed release commit `0965053fe6b9341776df147a6934b7485c60b5ca`.
- Update every installed or actively used VPS1 component with a verified stable compatible release.
- Preserve mounted agent state, identities, credentials, schedules, integrations, routes, branding, and recovery artifacts.
- New providers and unused capabilities are not added merely because packages exist.
- Destructive cleanup remains outside this update.

## Related Records

- GitHub workstream: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/235
- VPS2 comparison: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/234
- Notion plan: https://app.notion.com/p/3cea3e33d58180db830ddc12e6892cf2

## VPS2 Lessons Added Before VPS1 Mutation

- A public HTTP status is not enough. Verify the browser-visible Control UI and explain every non-200 response.
- Configure and verify local reverse-proxy attribution with narrow trusted proxy sources.
- Verify each browser pairing route separately where pairing is required.
- Test the Agents Dashboard, restart page, restart API authentication, and one real dashboard-triggered restart.
- Re-verify the agent version, image digest, route, credentials, integrations, and model response after that restart.

## Read-Only Baseline

- Host: `srv1404026`, Ubuntu kernel `6.8.0-134-generic`.
- Docker Engine: `29.6.1`; Docker Compose: `5.3.1`.
- Capacity: 193 GB filesystem, 127 GB available; 15 GB RAM; 4 GB swap.
- Eleven OpenClaw agent containers are healthy with zero restart counts on `2026.7.1`.
- Image cohorts:
  - Standard shared base: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Wilma.
  - Video refresh image: Terry and Vivian.
  - Docker/SSH derivative: Victor.
- The host has stable operating-system, Docker, Compose, containerd, Tailscale, 1Password CLI, Python, and kernel updates available and already reports that a reboot is required.
- All eleven external plugin trees contain old core-aligned packages; Mem0, Hindsight, voice, and Slack have separate installed versions.
- Current configurations do not explicitly set the approved session visibility. Most do not explicitly set direct-message scope. No agent currently declares the local Caddy sources as trusted proxies.
- Doctor baseline shows the Asana MCP schema probe failing where transport is not explicitly declared as `streamable-http`.
- Multiple enabled skills have missing binaries. Marsha is the only agent in the initial count with no enabled missing requirement.
- The live base Dockerfile includes Chromium, rsync, SQLite, and global Asana/Notion packages that were not yet reconciled to GitHub main. The canonical Dockerfile is being corrected before build.

## Build Inputs

- Canonical branch: `codex/vps1-openclaw-2026-8-2`.
- Shared base output: `ghcr.io/zedbiz44/openclaw-base:2026.8.2` and local immutable digest after build.
- Video cohort output: `zedbiz/openclaw-base:2026.8.2-video`.
- Victor output: `zedbiz-openclaw-victor:2026.8.2-ssh`.
- Exact Dockerfile checksums and resulting image IDs/digests are recorded in issue #235 after build.

## Test Gate

- Amanda is the standard-base test agent because she exercises the largest fleet cohort, the advanced Asana sidecar, Discord/Telegram, browser, external plugins, LanceDB memory, skills, and public routing.
- Terry is the first video-cohort verification.
- Victor is the first Docker/SSH derivative verification.
- Fleet rollout stops on migration failure, config validation failure, Doctor error, plugin capability request, unhealthy container, route failure, wrong image, state-write failure, failed model response, failed memory/session test, or dashboard/restart regression.

## Recovery

- Create a dated backup outside every writable agent state tree before its first recreation.
- Capture checksums and verify the archive can be listed and read.
- Retain the three known-good image artifacts and all current state until acceptance.
- Roll back code with the prior immutable image first when it can safely read current state.
- Restore state only through a separate offline recovery when code rollback cannot consume migrated state.

## Completion Evidence

- Every discovered component must end as Updated, Already Current, or Blocked with an exact reason.
- Record Git commits, Dockerfile checksums, image digests, agent versions, plugin versions, skill results, Doctor results, route results, model proofs, dashboard/restart proof, backups, host package state, reboot result, and remaining advisory items.
