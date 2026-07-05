# 2026-06-10 - Agent Key Files Added Across VPS1 and VPS2

Date: 2026-06-10 Mountain Time
Agent: Cody
Status: Complete

## Summary

- Added personal `*-KEY.md` files for agents that did not already have them.
- Preserved the existing `MAGGIE-KEY.md` and `VICTOR-KEY.md` content.
- Fixed VPS1 ownership on live `AGENTS.md` files and key files so the running agent user can read and update them.
- Left VPS2 ownership as `root:root` because the VPS2 OpenClaw services run as root.

## VPS1 Changes

- Server: `187.77.210.223`
- Agent workspace pattern: `/opt/openclaw/agents/{agent}/workspace`
- Created missing key files:
  - `AMANDA-KEY.md`
  - `GOHZED-KEY.md`
  - `GROGAR-KEY.md`
  - `INGA-KEY.md`
  - `MARSHA-KEY.md`
  - `TERRY-KEY.md`
  - `VIVIAN-KEY.md`
  - `WILMA-KEY.md`
- Existing key files preserved:
  - `MAGGIE-KEY.md`
  - `VICTOR-KEY.md`
- Ownership set to UID/GID `1000:1000` for:
  - Each live `AGENTS.md`
  - Each `*-KEY.md`
- Permissions set to `644` for the same files.

## VPS2 Changes

- Server: `2.24.104.80`
- Agent workspace pattern: `/root/.openclaw-{agent}/workspace`
- Created key files:
  - `HARRY-KEY.md`
  - `SUZY-KEY.md`
  - `EDITH-KEY.md`
- Ownership kept as `root:root`.
- Permissions set to `644`.

## Verification

- VPS1: Verified from the running Terry container as UID `1000` that `/home/node/.openclaw/workspace/TERRY-KEY.md` is readable and contains the `3+3=6` test line.
- VPS2: Verified `HARRY-KEY.md`, `SUZY-KEY.md`, and `EDITH-KEY.md` are readable and contain the `3+3=6` test line.

## Ownership Decision

- VPS1 should not leave these files as `root:root` because the agents run against workspaces owned by UID/GID `1000:1000`. Root-owned files may be readable, but they can block future agent updates.
- VPS2 should keep these files as `root:root` because Harry, Suzy, and Edith currently run as root via systemd.

## Notes

- `zara` exists under `/opt/openclaw/agents/zara`, but no `workspace` folder was present during this change, so no `ZARA-KEY.md` file was created.
