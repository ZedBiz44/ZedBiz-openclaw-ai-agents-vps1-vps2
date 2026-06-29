# VPS2 Shared Wiki Rsync Repair

Date: 2026-06-29 | Agent: Cody | Status: active

## Summary

- Repaired the VPS2 scheduled rsync job that transfers Harry, Frank, and Suzy personal wiki research into the VPS1 shared wiki.
- Confirmed the shared wiki path: `/opt/openclaw/shared/knowledge/wiki`.
- Confirmed the VPS2 sync script path: `/root/bin/sync-vps2-wikis-to-vps1.sh`.

## Issue

- Cron was firing `/root/bin/sync-vps2-wikis-to-vps1.sh` every 30 minutes.
- The script had no shebang and started with `set -uo pipefail`.
- Cron executed it with `/bin/sh` (`dash`), which does not support `pipefail`.
- Because no MTA is installed, the cron error output was discarded.
- The log file `/root/sync-vps2-wikis-to-vps1.log` had not updated since 2026-06-19.

## Fix

- Backed up the existing script to `/root/bin/sync-vps2-wikis-to-vps1.sh.bak-20260629-102446`.
- Added `#!/usr/bin/env bash` so cron runs the script with Bash.
- Changed `rsync -az` to `rsync -rz` to avoid permission/timestamp preservation failures on the shared wiki destination.
- Ran the sync manually after patching.

## Verification

- Manual sync ran at 2026-06-29 10:24:58 MDT and completed at 2026-06-29 10:24:59 MDT.
- New log section showed files being added from Suzy, Frank, and Harry with no new rsync permission warnings.
- Verified June 28 research files by relative path and SHA-256 hash from each VPS2 personal wiki against the shared wiki:
  - Harry: 2/2 matched, 0 changed, 0 missing.
  - Frank: 10/10 matched, 0 changed, 0 missing.
  - Suzy: 57/57 matched, 0 changed, 0 missing.
- Ran shared wiki compile/lint through the Terry container:
  - Compile: 364 pages, 21 indexes updated.
  - Standard lint: 0 errors, 75 warnings.

## Follow-Up

- ZedBiz custom frontmatter lint still reports metadata issues on shared research pages. That is a separate wiki-governance cleanup from the rsync transfer repair.
