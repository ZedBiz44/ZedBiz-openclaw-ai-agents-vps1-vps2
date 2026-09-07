#!/usr/bin/env bash
set -euo pipefail

readonly AGENT_ROOT="/opt/openclaw/agents/terry"
readonly BACKUP_ROOT="${1:-}"

if [[ -z "$BACKUP_ROOT" || "$BACKUP_ROOT" != "$AGENT_ROOT"/backups/*-gemini-video ]]; then
  echo "Usage: rollback-gemini-video-terry.sh /opt/openclaw/agents/terry/backups/<id>-gemini-video" >&2
  exit 2
fi

readonly RESOLVED_BACKUP="$(readlink -f "$BACKUP_ROOT")"
case "$RESOLVED_BACKUP" in
  "$AGENT_ROOT"/backups/*-gemini-video) ;;
  *) echo "Backup path is outside Terry's approved backup folder." >&2; exit 3 ;;
esac

[[ -f "$RESOLVED_BACKUP/.env" && -f "$RESOLVED_BACKUP/docker-compose.yml" ]] || {
  echo "The requested Terry backup is incomplete." >&2
  exit 4
}

cp -a "$RESOLVED_BACKUP/.env" "$AGENT_ROOT/.env"
cp -a "$RESOLVED_BACKUP/docker-compose.yml" "$AGENT_ROOT/docker-compose.yml"

docker exec -u node terry openclaw mcp unset gemini-video 2>/dev/null || true
docker exec -u root terry rm -rf -- \
  /opt/openclaw/shared/tools/z-gemini-video-mcp \
  /home/node/.openclaw/workspace/skills/z-video-analysis
"$AGENT_ROOT/op-start-terry.sh" restart

echo "Terry Gemini video deployment removed using $RESOLVED_BACKUP"
