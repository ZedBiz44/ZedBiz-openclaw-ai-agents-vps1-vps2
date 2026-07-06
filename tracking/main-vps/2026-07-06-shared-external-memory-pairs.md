# Shared External Memory Pair Setup

Date: 2026-07-06
Agent: Cody
Status: Resolved

## Summary

- Configured Inga and Suzy to use Hindsight with the shared `internet-marketing` memory bank.
- Configured GohZed and Grogar to use Hindsight with the shared `ghl` memory bank.
- Added Harry to the same shared Mem0 area used by Edith and Terry.

## Live Changes

- VPS1 `inga`:
  - Installed `@vectorize-io/hindsight-openclaw`.
  - Set `plugins.slots.memory` to `hindsight-openclaw`.
  - Set Hindsight bank to `internet-marketing`.

- VPS2 `suzy`:
  - Installed `@vectorize-io/hindsight-openclaw`.
  - Set `plugins.slots.memory` to `hindsight-openclaw`.
  - Set Hindsight bank to `internet-marketing`.

- VPS1 `gohzed` and `grogar`:
  - Installed `@vectorize-io/hindsight-openclaw`.
  - Set `plugins.slots.memory` to `hindsight-openclaw`.
  - Set Hindsight bank to `ghl`.

- VPS2 `harry`:
  - Installed `@mem0/openclaw-mem0`.
  - Set `plugins.slots.memory` to `openclaw-mem0`.
  - Set Mem0 user to `zedbiz-vps1`.
  - Set shared collection to `mem0_vps1_agents`.

## Supporting Network Change

- Added a Caddy route on `marsha.zbiz.ca` for VPS2-to-Qdrant access at `/qdrant-api/*`.
- Restricted the route to VPS2 by client IP.
- Connected the Caddy container to the Mem0 Docker network.
- Updated `/opt/caddy/docker-compose.yml` so the Mem0 network attachment survives future container recreation.

## Verification

- `openclaw config validate` passed for:
  - `inga`
  - `gohzed`
  - `grogar`
  - `harry`
  - `suzy`

- Runtime checks:
  - `inga` initialized Hindsight with bank `internet-marketing`.
  - `suzy` initialized Hindsight with bank `internet-marketing`.
  - `gohzed` initialized Hindsight with bank `ghl`.
  - `grogar` initialized Hindsight with bank `ghl`.
  - `harry` registered and initialized `openclaw-mem0`.

- Service/container health:
  - VPS1 containers `inga`, `gohzed`, and `grogar` were running healthy after restart.
  - VPS2 services `openclaw-harry` and `openclaw-suzy` were active after restart.
  - VPS2 could reach `https://marsha.zbiz.ca/qdrant-api/collections` and received the expected Qdrant collections list.
