#!/usr/bin/env bash
set -euo pipefail
umask 077
BASE=/opt/openclaw/services/hindsight
DEST="$BASE/backups/postgres"
mkdir -p "$DEST"
exec 9>"$DEST/.backup.lock"
flock -n 9 || exit 0
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT="$DEST/hindsight-$STAMP.dump.enc"
TMP="$OUT.partial"
trap 'rm -f -- "$TMP"' EXIT
docker exec hindsight-db pg_dump -U hindsight -d hindsight -Fc --no-owner --no-acl | openssl enc -aes-256-cbc -salt -pbkdf2 -pass file:"$BASE/.backup-key" -out "$TMP"
test -s "$TMP"
mv -- "$TMP" "$OUT"
sha256sum "$OUT" > "$OUT.sha256"
printf '%s\n' "$OUT"
# Keep two weeks of scheduled backups; upgrade snapshots are in a separate folder.
find "$DEST" -maxdepth 1 -type f -name 'hindsight-*.dump.enc*' -mtime +14 -delete
