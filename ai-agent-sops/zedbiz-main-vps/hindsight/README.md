# Central Hindsight operations

Production owner: ZedBiz infrastructure operator. Verified 2026-09-14 by Cody. Related issue: #311.

## Deployed layout

- VPS1: `/opt/openclaw/services/hindsight`.
- API: Hindsight 0.10.0 with FlashRank 0.2.10; pinned upstream digest in Dockerfile.
- Database: separate PostgreSQL 18.6/pgvector, pinned image in `database.compose.json`; durable volume `hindsight-pg18-data`.
- Database network is internal only, with no host port. API retains the existing loopback ports and public proxy route.
- Agent memory policies and the nine automatic summary definitions are unchanged.

## Service operation

Production API Compose is installed as `build/docker-compose.yml` beside Dockerfile. Database Compose is installed as `upgrade-0100/database.compose.json`. Use the correct project names:

```bash
docker compose -p hindsight-storage -f /opt/openclaw/services/hindsight/upgrade-0100/database.compose.json up -d
docker inspect --format '{{.State.Health.Status}}' hindsight-db
docker compose -p hindsight-central -f /opt/openclaw/services/hindsight/build/docker-compose.yml up -d --no-build
curl --fail http://127.0.0.1:8898/health
```

Start the API after the database is healthy. For planned shutdown, stop the API before stopping the database; give each 60 seconds. Do not use `down -v` on production storage. Compose files reference private host environment files; their contents must never be committed. The API DB URL and PostgreSQL credentials must agree. Existing provider/API credentials stay in the original `.env`.

## Backup and restore

The installed `backup-postgres.sh` runs every six hours through jackadmin's crontab. It retains encrypted logical backups for roughly fourteen days under `backups/postgres`. Its encryption key is the private file `.backup-key` in the service directory. Backups and key are currently on VPS1 only; off-server recovery is not yet provided.

Restore drills must target a new, explicitly named temporary database, never overwrite the live `hindsight` database. Example after creating a dedicated test database:

```bash
set -o pipefail
openssl enc -d -aes-256-cbc -pbkdf2 \
  -pass file:/opt/openclaw/services/hindsight/.backup-key \
  -in /absolute/path/to/selected.dump.enc | \
  docker exec -i hindsight-db pg_restore -U hindsight \
    -d hindsight_restore_test --no-owner --no-acl --exit-on-error
```

Verify source checksum first, successful restore, migration version, and counts for memory_units, documents, banks and mental_models. Delete only the temporary test database when finished. A checksum detects accidental corruption; it is not an independent authenticity guarantee.

## Rollback boundary

The stopped old container `hindsight-rollback-091-20260914` has restart disabled and is disconnected from the agent network. Original volume `hindsight-data` is preserved. Upgrade backups are in `backups/upgrade-0100-20260914`, including final.dump, original configuration and old-pg0-cold.tar with checksums.

That old database represents the cutover point. Once production accepts new writes, starting it would lose newer activity. Pause writes and reconcile/export those changes before any rollback. Do not point the old 0.9.1 application at the migrated database without a tested compatibility plan. Preserve the encryption key separately before treating off-server backup as complete.

## Acceptance evidence

See `../tracking/2026-09-14-hindsight-server-0100-upgrade.md` for counts, agent receipt and restore evidence. The September 14 tests prove upgrade functionality and a recoverable local backup; they do not establish long-term performance or authorize enabling additional automatic recall.
