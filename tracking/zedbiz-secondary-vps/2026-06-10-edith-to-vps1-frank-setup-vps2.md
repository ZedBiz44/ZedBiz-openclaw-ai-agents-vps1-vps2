# 2026-06-10 | Manus | Edith Migration to VPS1 + Frank Setup on VPS2

**Date:** 2026-06-10 (MST)
**Agent:** Manus
**Status:** Complete (DNS cutover pending Jack/Cloudflare)

---

## Summary

Edith was staged on VPS1 by Victor (container `edith`, port 3011, healthy). This session completed the remaining infrastructure work:

- VPS2 Caddy updated: `edith.zbiz.ca` -> `frank.zbiz.ca`
- Frank service created and started on VPS2 (port 4300)
- Edith service stopped and disabled on VPS2
- Frank workspace identity files written (IDENTITY.md, AGENTS.md, SOUL.md, TOOLS.md)
- DNS changes required in Cloudflare (Jack to action)

---

## VPS1 - Edith (New Home)

| Item | Value |
|---|---|
| Container | `edith` |
| Port | `3011` |
| Image | `ghcr.io/zedbiz44/openclaw-base:latest` |
| Caddy block | `edith.zbiz.ca { reverse_proxy edith:3011 }` |
| Health | Healthy (verified) |
| DNS target | `187.77.210.223` (VPS1) |

---

## VPS2 - Frank (Edith's Former Slot)

| Item | Value |
|---|---|
| Service | `openclaw-frank.service` (enabled, running) |
| Port | `4300` |
| Workspace | `/root/.openclaw-frank/` |
| Config | `/root/.openclaw-frank/openclaw.json` |
| Caddy block | `frank.zbiz.ca { reverse_proxy localhost:4300 }` |
| HTTP status | 200 OK (verified) |
| DNS target | `2.24.104.80` (VPS2) |

---

## Changes Made on VPS2

- `/etc/caddy/Caddyfile`: replaced `edith.zbiz.ca` with `frank.zbiz.ca`, reloaded Caddy
- `/etc/systemd/system/openclaw-frank.service`: created from edith service template
- `/opt/openclaw-frank/`: copied from `/opt/openclaw-edith/`, start script renamed/updated
- `/root/.openclaw-frank/`: copied from `/root/.openclaw-edith/`, paths updated
- `/root/.openclaw-frank/openclaw.json`: `edith.zbiz.ca` -> `frank.zbiz.ca` in allowedOrigins and workspace paths
- Workspace identity files: IDENTITY.md, AGENTS.md, SOUL.md, TOOLS.md written for Frank
- `openclaw-edith.service`: stopped and disabled
- `openclaw-frank.service`: enabled and started

---

## DNS Changes Required (Jack/Cloudflare)

| Record | Type | Old Value | New Value | Action |
|---|---|---|---|---|
| `edith.zbiz.ca` | A | `2.24.104.80` (VPS2) | `187.77.210.223` (VPS1) | **Update** |
| `frank.zbiz.ca` | A | (does not exist) | `2.24.104.80` (VPS2) | **Create** |

---

## Pending Items

- Cloudflare DNS cutover (Jack)
- Codex OAuth setup for Edith on VPS1 (Jack browser required)
- Codex OAuth setup for Frank on VPS2 (Jack browser required)
- Frank role/identity definition (Jack to assign)
- Agent Registry: add Frank entry, update Edith entry (VPS -> VPS1, URL -> edith.zbiz.ca)
