# Edith ZMMW browser and registry recovery

Verified by Cody on October 13, 2026 (America/Edmonton), authorized by Jack's "fix edith and the issues" request. Scope is Edith on VPS1, not the outdated secondary-VPS placement in the root orientation. Parent issue: [#455](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/455).

## Browser

Confirmed Chromium was not running. The profile's SingletonLock named prior container 8dce42528d0a; Edith's actual container hostname was 8ecda56412d9. Inspected overlapping mounts and browser processes before changing locks. Moved only three stale singleton symlinks into Edith's private browser-lock-backup-20261013 directory under private/folder-cleanup/zmmw. No profile data deletion, container restart, model or security change.

`docker exec edith openclaw browser start --json` returned running, CDP ready and page ready. Rendered zedloyalty.com redirected to /lander with parking ads. This does not establish that the Drive folder belongs to that domain. Edith subsequently rendered a formerly blank Bio preview and published/read back its source-backed Website and Connection; total rose from 41 to 42 of 48 targets at 18:38 MDT. Work remains active, not complete.

Browser rollback: preserve the symlink backup. Do not restore stale locks over a running browser. A restoration requires browser-idle validation and a separate reason; blindly restoring the known stale lock recreates the fault. Existing October 16 reminder covers temporary browser evidence only, not operational records.

## Mirror diagnosis and repair

Twelve pairs had equal code, title, URL, status and empty bodies; one row reflected record_reserved and the other record_confirmed seconds later. Code queried Notion again for every event and discarded successful create IDs. A delayed query index can therefore create duplicates. The deterministic test reproduces this defect; historical Notion indexing latency itself was not logged.

Added persisted page identity and pre-create intent in /data/mirror-identities.sqlite3, scoped ONLY to ZMMW-40000 codes and topics. Read existing pages directly after create, validate identity/parent, refuse uncertain POST retries, and preserve other lanes' behavior. The SQLite file persists on the existing data volume. It is operational state, not purgeable temporary evidence.

Deployed source is services/z-code-allocator/app/mirror_worker.py. The mirror-only overlay image is zedbiz-z-code-allocator:1.3.0-edith-mirror1, based on the existing 1.3.0 image. Dockerfile content:

```dockerfile
FROM zedbiz-z-code-allocator:1.3.0
COPY app/mirror_worker.py /app/app/mirror_worker.py
```

Only z-code-notion-mirror's Compose image/build changed. `docker compose config --quiet` passed; `docker compose build z-code-notion-mirror` succeeded; `docker compose up -d --no-deps z-code-notion-mirror` recreated only the mirror. Allocator and Edith were not restarted. Image ID: sha256:65614526f8297c94a15402d9f749138bc83acd81018337298204f35d0e1bac45.

Backups: /opt/zedbiz-services/z-code-allocator/backups/edith-mirror-20261013 contains original compose and source. Private data backup: /data/repair-edith-20261013/allocator-before.sqlite3 and per-code JSON before-images on the data volume. Credentials were neither printed nor committed. Do not restore the full allocator snapshot over new allocations. For application rollback, compare current Compose against the backup, restore only this mirror image/build and source if no intervening edits, then recreate only the mirror. Retain identity state. No production rollback was exercised because it would reintroduce the known defect.

Reconciliation kept each original record_reserved row, archived the identical record_confirmed duplicate (reversible, not deleted), seeded its original page ID and mirrored authoritative owning data. Pilot succeeded before remaining eleven. Per-code audit entries and before-images preserved. All twelve independently queried afterward: exactly one active row each, owning URL matches allocator. No briefs, Connections, allocations or ownership changed.

Affected suffixes under ZMMW-40000: 100007-010, 100012-010, 100017-010, 100015-010, 100014-010, 100013-011, 100037-010, 100039-010, 100036-010, 100043-010, 100041-010, 100045-010. Row rollback would unarchive only the saved duplicate ID after confirming the current owner; it intentionally restores a duplicate, so is not a normal recovery action.

## Tests

- Five unittest cases passed against deployed module: delayed index/recreated client, uncertain create, changed/archived identity, topic identity, unaffected lane.
- Three existing normalized-registry tests passed by direct invocation: record title/relation, initial topic title, inaccessible linked-page fallback.
- Full pytest suite was not run: pytest is absent in the production image. No dependency installation was performed.
- Two audited admin_resync_record events for the pilot completed once each (outbox 476 and 477, 00:41:49/50 UTC October 14); repeated live query still found exactly one row.
- PRAGMA quick_check returned ok for allocator and identity databases.
- The first live-test query used a wrong column name, z_code; corrected to aggregate_key and reran successfully. This was a verification-script error, not a service error.

## ZedNow routing decision

Existing ZedNow Z1PS/30001/topic100006 belongs to the Parked Marketing Automation Product and its canonical Services companion, not the whole marketing website. Preserve code Z1PS-30001-100006-010, topic, aliases, Product and Services.

Supported admin review resolution dismissed review-edith-20261013-zmmw-zednow-venture-brief with an audited decision approving distinct Name-Key ZedNow-Marketing-Website under ZMMW/40000. Review status read back dismissed and old lookup unchanged. Edith must search existing briefs, then use a new stable allocation request and normal confirmation for the distinct source-backed Venture/Website pair; no manual code reassignment. Handoff waits for her current six-source browser continuation to end, to avoid interruption or duplicate workers.

## Remaining work

Edith owns remaining source verification/publication, one site at a time under z-small-bite-task. Cody owns post-repair sampling and the guarded routing handoff. ZedContact/ZedLoyalty domain identity may still need Jack's confirmation; do not infer ownership from a guessed hostname. Twenty-minute monitor remains active. Full completion requires all target outcomes and real destination relations verified. This source PR records the deployed hotfix; merging does not authorize a fleet or other-lane rollout.
