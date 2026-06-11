# 2026-06-10 | Manus | Edith Migration to VPS1

**Date:** 2026-06-10 (MST)
**Agent:** Manus
**Status:** Staged and healthy (DNS cutover pending)

---

## Summary

Edith has been migrated from VPS2 to VPS1. Victor completed the container build and staging. This log records the VPS1 side of the migration.

---

## VPS1 Edith Container Details

| Item | Value |
|---|---|
| Container name | `edith` |
| Port | `3011` (bound to `127.0.0.1`) |
| Image | `ghcr.io/zedbiz44/openclaw-base:latest` |
| OpenClaw version | `2026.6.5` |
| Workspace | `/opt/openclaw/agents/edith/` |
| Health | `healthy` (verified) |
| Caddy block | `edith.zbiz.ca { reverse_proxy edith:3011 }` |

## Files Inserted by Victor

- AGENTS.md
- SOUL.md
- IDENTITY.md
- TOOLS.md
- USER.md
- HEARTBEAT.md
- MEMORY.md
- EDITH-KEY.md

## Pending

- DNS: `edith.zbiz.ca` A record update in Cloudflare -> `187.77.210.223` (Jack)
- Codex OAuth setup (Jack browser required)
- Discord token/channel configuration
- Email credentials configuration
