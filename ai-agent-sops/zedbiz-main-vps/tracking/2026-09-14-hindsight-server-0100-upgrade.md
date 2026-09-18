# Central Hindsight 0.10.0 upgrade

Date: 2026-09-14 MDT | Agent: Cody | Status: Deployed and verified

## Authorized change and result

Jack requested the central Hindsight server 0.10.0 upgrade immediately after review of the embedded database durability risk. VPS1 now runs `zedbiz/hindsight:0.10.0-flashrank-20260914` and separate PostgreSQL 18.6. FlashRank remains 0.2.10. API and database containers are healthy. The database reports fsync, full_page_writes and synchronous_commit on.

No agent connector, automatic retain/recall, Active Memory assignment, shared-bank mission or mental-model refresh policy changed. Rocky's separate VPS4 service was outside scope.

## Migration and preservation

- Built the pinned upstream 0.10.0 image with the existing FlashRank package.
- Restored a production snapshot into isolated PostgreSQL and tested a candidate API with background workers disabled.
- Paused old API writes, took a final logical snapshot, cleanly stopped and preserved the original container and embedded volume.
- Restored the final snapshot into the new database, applied migrations through the candidate, checked counts, then started the normal API with workers enabled.
- Final snapshot and post-migration counts matched exactly: 17,278 memory units, 584 documents, five banks and nine mental models. Knowledge pages and directives were zero.
- Migration head: `f3a5b7c9d1e2`.

## Verification

- Internal and authenticated public health routes: healthy; database connected; zero pool waiters at check.
- OpenAPI service version: 0.10.0.
- Candidate recalls: zedbiz-shared 10 results/0.416s; internet-marketing 12/0.267s; ghl 15/0.326s. These are small smoke tests, not a comparative benchmark.
- Marsha's actual OpenClaw turn completed successfully and returned 23 results through `agent_knowledge_recall`.
- Agent run ID: `ea38eebb-6f1e-499c-9c3d-e73d5fa9fb3f`; turn ID: `01a0a109-1461-79e1-aeb9-e6998afa3f79`. Receipt confirmed the successful tool name.
- Production synthetic retain, exact-value recall and reflect all passed. The temporary live test bank was deleted afterward. Candidate test data was discarded before the final restore.
- First encrypted production backup `hindsight-20260914T174846Z.dump.enc` was fully decrypted and restored into a temporary database: 17,278 memories, 584 documents, nine models and expected migration head. Temporary restore database removed afterward.

## Recovery and limits

Upgrade backup directory: `/opt/openclaw/services/hindsight/backups/upgrade-0100-20260914`. Includes baseline/final logical dumps (133,376,275 bytes each), original configuration, stopped-volume archive and checksums. Private files remain on the server.

Encrypted scheduled backups run every six hours and retain about fourteen days. The old container and original embedded volume remain preserved. Backups are local to VPS1; no off-server copy was created. A rollback after new production writes requires reconciliation, not simply restarting the stale old database.

Long-term load and the nine automatic summary refresh definitions remain separate review items. This upgrade does not prove additional automatic recall is safe to enable.

Technical workstream: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/311
