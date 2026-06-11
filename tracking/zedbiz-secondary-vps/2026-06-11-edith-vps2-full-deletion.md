# 2026-06-11 | Cody | VPS2 Edith Full Deletion

2026-06-11 | Cody | Status: Done

## Summary

- Deleted the inactive VPS2 Edith agent from `srv1677638` / VPS2.
- Updated the Notion `Agent Deletion - VPS2` SOP with an explicit wiki sync / cron cleanup checkpoint.
- Removed Edith-specific runtime, service, state, sync, certificate, and stale migration/session remnants from VPS2.
- No changes were made to Harry, Suzy, or Frank service ownership, live ports, or shared host tools.

## Removed From VPS2

- `openclaw-edith.service`
- `/etc/systemd/system/openclaw-edith.service`
- `/etc/systemd/system/openclaw-edith.service.d`
- `/opt/openclaw-edith`
- `/root/.openclaw-edith`
- Edith source line from `/root/bin/sync-vps2-wikis-to-vps1.sh`
- Stale Edith Caddy certificate cache under `/var/lib/caddy`
- Copied Edith-era workspace, memory, session, cache, and migration remnants inside Frank and Suzy state folders
- Frank package metadata was corrected from `openclaw-edith` to `openclaw-frank`

## Local Backups

Backups were copied to the local Codex project workspace before deletion:

- `backups/openclaw-edith-deletion-20260611-113203.tar.gz`
- `backups/frank-edith-remnants-20260611-114001.tar.gz`
- `backups/deep-edith-remnants-20260611-114343.tar.gz`
- `backups/suzy-edith-session-remnants-20260611-114536.tar.gz`

Remote temporary backup archives were removed from VPS2 after local copy.

## Verification

- `systemctl` lists only `openclaw-harry`, `openclaw-suzy`, and `openclaw-frank` as OpenClaw services.
- No `openclaw-edith` unit file remains.
- No `/opt`, `/root`, `/etc/systemd/system`, `/etc/caddy`, `/root/bin`, or `/var/lib/caddy` path matched `*edith*`.
- Content scan across `/root/.openclaw-*`, `/opt/openclaw-*`, Caddy, systemd, cron, `/root/bin`, backups, and Caddy storage returned `0` Edith matches, excluding normal software dependency folders.
- Caddy remained active and validated successfully.
- VPS2 wiki sync script passed syntax check and now syncs only Suzy and Harry.
- Public endpoint checks:
  - `https://harry.zbiz.ca` returned `200` from `2.24.104.80`.
  - `https://suzy.zbiz.ca` returned `200` from `2.24.104.80`.
  - `https://frank.zbiz.ca` returned `200` from `2.24.104.80`.
  - `https://edith.zbiz.ca` returned `200` from `187.77.210.223`, not VPS2.

## Note

`edith.zbiz.ca` currently resolves away from VPS2. This deletion removed Edith remnants from VPS2 only.
