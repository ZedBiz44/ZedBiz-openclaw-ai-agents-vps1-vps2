#!/bin/sh
set -eu

cd /opt/zedbiz-services/z-code-allocator
action="${1:-status}"

case "$action" in
  status)
    docker ps -a --filter name=z-code-db-emergency --format '{{.Names}}|{{.Status}}'
    ;;
  start)
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    docker exec -i z-code-allocator python - "$stamp" <<'PY'
import sqlite3
import sys
s = sqlite3.connect('/data/zcode.db')
d = sqlite3.connect(f'/data/backups/zcode-pre-raw-{sys.argv[1]}.db')
s.backup(d)
d.close()
s.close()
PY
    docker compose stop z-code-allocator z-code-notion-mirror
    docker compose --profile emergency-db up -d z-code-db-emergency
    echo "Emergency editor started. Allocation and mirror processing are paused."
    ;;
  stop)
    docker compose --profile emergency-db stop z-code-db-emergency
    check=$(docker run --rm -v "$PWD/data:/data" zedbiz-z-code-allocator:1.1.0 \
      python -c 'import sqlite3; print(sqlite3.connect("/data/zcode.db").execute("PRAGMA quick_check").fetchone()[0])')
    test "$check" = "ok"
    docker compose up -d z-code-allocator z-code-notion-mirror z-code-admin
    sleep 5
    docker exec z-code-notion-mirror python -m app.backfill_registry --require-complete
    echo "Emergency editor stopped. Integrity and complete Notion reconciliation passed."
    ;;
  *)
    echo "Usage: $0 start|stop|status" >&2
    exit 2
    ;;
esac
