# VPS1 OpenClaw 2026.8.2 Full-Stack Update

> Branding follow-up: see `2026-09-01-vps1-openclaw-2026-8-2-branding-correction.md` and GitHub issue `#239` for the runtime identity and workspace-icon correction required by the 2026.8.2 Control UI.

Date: 2026-09-01 | Agent: Cody | Status: Complete With Host Maintenance Pending

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

- All eleven agents are healthy with zero restart counts on exact OpenClaw `2026.8.2`.
- Standard cohort: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha and Wilma use `ghcr.io/zedbiz44/openclaw-base:2026.8.2`, image `sha256:e4d1bc6332ad941f8a6b0c4fa3696aab8e7cef18363c9bdcf5b5c93f5ec38741`.
- Video cohort: Terry and Vivian use `zedbiz/openclaw-base:2026.8.2-video`, image `sha256:eadb34d2b644567f6fa99b4830efba4eb8c8632309b91e3c8a0e7ff34da6e248`.
- Victor uses `zedbiz-openclaw-victor:2026.8.2-ssh`, image `sha256:bae64d29a88e7dca82ab181d69a9ebf5bc503295039ff00365f5099a80f5fe6e`.
- Every agent passed the final audit for `session.dmScope=per-channel-peer`, `tools.sessions.visibility=tree`, Asana `streamable-http`, Caddy trust `172.18.0.0/16`, plugin currency, gateway reachability, event-loop health and skill-check execution.
- Core-aligned external plugins moved from `2026.7.1` to `2026.8.2`. Hindsight moved `0.10.0` to `0.11.1`, Mem0 moved `1.0.15` to `1.0.16`, Terry's Slack plugin moved to `2026.8.2`, and Marsha's pinned voice-call plugin moved to `2026.8.2`.
- Shared tools are current at `gog 0.38.1`, `ntn 0.22.12`, `summarize 0.21.11` and `mcporter 0.13.8`.
- Real model replies passed on the standard, video and Victor cohorts. Read-only Asana calls passed on Amanda, Terry and Victor.
- Amanda's browser-visible Control UI displayed Telegram and Discord sessions. Device pairing, the Agents Dashboard, restart page and a real Dashboard-triggered restart completed successfully.
- The Dashboard is reachable without an outer authentication challenge and exposes agent connection links. Follow-up security issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/237.

## Runtime Corrections Found During Rollout

- Wilma still had retired per-site WordPress environment and direct-MCP bindings after the newer restricted on-demand WordPress skill replaced them. The retired bindings were removed after preserving the original backup. The current `wordpress-allzed` and on-demand 1Password route remain.
- Victor's Compose file hard-coded the old `2026.7.1` special image even after `.env` was updated. Compose was corrected to `2026.8.2`; the rollout script now validates and updates Victor's image pin.
- Terry's Slack plugin and Marsha's pinned voice-call plugin required explicit capability/version handling. The rollout script now includes those cases.
- VPS2 issue #234 was amended: `goplaces 1.0.2` was an unrelated npm package. The official `openclaw/goplaces` version installed in the VPS1 image is `0.4.9`; VPS2 needs a separate correction.

## Recovery Evidence

- Offline archives are stored in `/opt/openclaw/backups/2026-09-01-openclaw-2026.8.2/`.
- Final archive checksums: Amanda `c8c77166…44be6`; Edith `34905c5e…6dda9`; Gohzed `dc250dcb…7573`; Grogar `e6966504…abe2`; Inga `cc5b6347…220a`; Maggie `6667d2b6…dd0a`; Marsha `1f372a56…0add`; Terry `07e8d1f2…b8cd`; Vivian `bdb681c6…18e4`; Wilma `770497b8…56e7`; Victor `0f82db61…ed60`.
- Wilma's pre-cleanup archive and Victor's pre-Compose-fix archive were preserved separately from the final rerun backups.

## Remaining Host Maintenance

- VPS1 still has 31 Ubuntu/Docker-related package updates and reports that a reboot is required.
- `jackadmin` does not have passwordless sudo, so host package installation and reboot could not be completed through the authorized SSH route.
- This does not block the OpenClaw fleet: all eleven agents and integrations are healthy. It is a separate administrator-authority maintenance action.
