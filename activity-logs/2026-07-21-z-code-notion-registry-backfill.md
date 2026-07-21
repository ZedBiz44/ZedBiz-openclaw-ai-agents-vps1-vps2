# 2026-07-21 - Z-Code Notion Registry Backfill

## Summary

- **Date:** 2026-07-21 Mountain Time
- **Agent:** Cody
- **Issue:** [#80](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/80)
- **Result:** All historical SQLite allocations are now represented in the human-facing Notion `Z-Code-Registry`.

## Root Cause

The bootstrap importer inserted historical records into authoritative SQLite and wrote aggregate audit events, but it did not enqueue per-record `sync_outbox` events. The Notion worker only mirrored outbox events, so the 349 bootstrap records never appeared in Notion.

## Changes

- Added `app.backfill_registry`, an idempotent SQLite-to-Notion backfill and reconciliation command.
- Added explicit `Source = Bootstrap` handling while preserving `Source = Allocator` for live events.
- Added retry handling for Notion HTTP 429 and server errors.
- Added an automated idempotency and source-label test.
- Documented the pilot-first and complete-reconciliation commands.

## Safety And Rollback

- SQLite backup: `/opt/zedbiz-services/z-code-allocator/data/backups/zcode-pre-notion-backfill-20260721.db`
- Backup SHA-256: `6dce223ed439d9897043b5c3c476d3ad3e1f957e98b211853c071be75eca07ca`
- Pre-backfill Notion registry export: `/opt/zedbiz-services/z-code-allocator/data/backups/notion-registry-before-backfill-20260721.json`
- Source backups: `/opt/zedbiz-services/z-code-allocator/backups/notion-backfill-20260721/`
- The backfill did not modify SQLite allocations.

## Pilot

- Backfilled one historical record first: `Z1PS-30001-100001-050`.
- Verified it appeared in Notion with `Source = Bootstrap`, `Status = Active`, the exact original Notion URL, and no duplicate.

## Final Verification

- Authoritative SQLite records: 359
- Notion registry rows: 359
- Unique Notion Z-Codes: 359
- Bootstrap rows: 349
- Allocator rows: 10
- Active rows: 358
- Abandoned rows: 1
- Missing authoritative codes: 0
- Extra registry codes: 0
- Duplicate registry codes: 0
- SQLite `PRAGMA quick_check`: `ok`
- Allocator remained healthy during the mirror-only deployment and backfill.

## Server Access

- VPS1 host: `187.77.210.223`
- SSH user: `jackadmin`
- Authoritative database: `/opt/zedbiz-services/z-code-allocator/data/zcode.db`
- The database is intentionally not exposed as a public browser interface.
- Human access is through the Notion registry; agent access is through the allocator API.
