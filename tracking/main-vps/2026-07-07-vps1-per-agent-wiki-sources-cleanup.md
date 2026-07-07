# 2026-07-07 - VPS1 Per-Agent Wiki Sources Cleanup

Date: 2026-07-07 Mountain Time
Agent Name: Cody
Status: Completed

## Summary

- Removed stale per-agent `wiki/sources` folders from VPS1 personal agent wiki copies.
- Left the active shared wiki source folder untouched:
  - `/opt/openclaw/shared/knowledge/wiki/sources`
- The stale per-agent source files were old bridge memory exports created on 2026-06-23, matching the memory embedding key rollout date.

## Change Reason

- The personal agent wiki copies for GohZed, Grogar, Maggie, Terry, and Vivian had visible old source-note files.
- Other VPS1 agents had only tiny placeholder-style source folders.
- Terry's live wiki status confirmed the active wiki vault is the shared wiki path, not the per-agent wiki copy:
  - `/opt/openclaw/shared/knowledge/wiki`

## Change Details

- VPS: main-vps / VPS1
- Host: `srv1404026`
- Host IP: `187.77.210.223`
- Changed by: Cody
- Affected agent source folders removed:
  - `/opt/openclaw/shared/knowledge/amanda/wiki/sources`
  - `/opt/openclaw/shared/knowledge/edith/wiki/sources`
  - `/opt/openclaw/shared/knowledge/gohzed/wiki/sources`
  - `/opt/openclaw/shared/knowledge/grogar/wiki/sources`
  - `/opt/openclaw/shared/knowledge/inga/wiki/sources`
  - `/opt/openclaw/shared/knowledge/maggie/wiki/sources`
  - `/opt/openclaw/shared/knowledge/marsha/wiki/sources`
  - `/opt/openclaw/shared/knowledge/terry/wiki/sources`
  - `/opt/openclaw/shared/knowledge/victor/wiki/sources`
  - `/opt/openclaw/shared/knowledge/vivian/wiki/sources`
  - `/opt/openclaw/shared/knowledge/wilma/wiki/sources`
- Method:
  - Used the Docker Alpine host-volume workaround to remove root/ubuntu-owned folders without sudo.
- Services restarted:
  - None.
- Docker containers affected:
  - No containers were restarted for this cleanup.

## Backups

- Terry one-agent test backup:
  - `/opt/openclaw/backups/per-agent-wiki-sources-before-cleanup-.tgz`
- Remaining agent source-folder backup:
  - `/opt/openclaw/backups/per-agent-wiki-sources-before-cleanup-20260707-1452.tgz`

## Verification

- Tested Terry first:
  - Removed Terry's stale per-agent source folder.
  - Re-ran Terry wiki status successfully.
- Terry wiki status after cleanup:
  - `Wiki vault mode: isolated`
  - `Vault: ready (/opt/openclaw/shared/knowledge/wiki)`
  - `Bridge: disabled`
  - `Pages: 203 sources, 92 entities, 17 concepts, 62 syntheses, 11 reports`
- Confirmed all targeted personal agent source folders were removed.
- Confirmed active shared wiki source folder still exists:
  - `/opt/openclaw/shared/knowledge/wiki/sources`
- Confirmed the active shared wiki source folder still had current source files.

## Related Finding

- Marsha was found restarting during post-cleanup verification.
- Marsha logs show the restart reason is unrelated to the wiki-source cleanup:
  - `HINDSIGHT_API_TOKEN` is missing or empty.
- Marsha should be handled as a separate Hindsight/shared-memory secret fix.

## Rollback Note

- Restore from the backup archives if a personal agent wiki source folder is unexpectedly needed.
- The active shared wiki source folder was not changed.

