#!/usr/bin/env bash
set -euo pipefail

readonly AGENT_ROOT="/opt/openclaw/agents/terry"
readonly SHARED_TOOL="/opt/openclaw/shared/tools/z-gemini-video-mcp"
readonly SKILL_TARGET="$AGENT_ROOT/workspace/skills/z-video-analysis"
readonly STAGE_ROOT="${1:-}"
readonly SECRET_REFERENCE='op://openclaw-agents-shared/gemini-video-api-key/credential'

if [[ -z "$STAGE_ROOT" || ! -f "$STAGE_ROOT/service/package-lock.json" || ! -f "$STAGE_ROOT/skill/SKILL.md" ]]; then
  echo "Usage: deploy-gemini-video-terry.sh <verified-stage-directory>" >&2
  exit 2
fi

for required in "$AGENT_ROOT/.env" "$AGENT_ROOT/docker-compose.yml" "$AGENT_ROOT/op-start-terry.sh"; do
  [[ -f "$required" ]] || { echo "Required Terry file is missing: $required" >&2; exit 3; }
done

if [[ -e "$SHARED_TOOL" ]] || docker exec -u root terry test -e /home/node/.openclaw/workspace/skills/z-video-analysis; then
  echo "A Gemini video deployment path already exists. Stop and inspect it before replacing anything." >&2
  exit 4
fi

readonly BACKUP_ID="$(date -u +%Y%m%dT%H%M%SZ)"
readonly BACKUP_ROOT="$AGENT_ROOT/backups/$BACKUP_ID-gemini-video"
mkdir -p "$BACKUP_ROOT"
cp -a "$AGENT_ROOT/.env" "$BACKUP_ROOT/.env"
cp -a "$AGENT_ROOT/docker-compose.yml" "$BACKUP_ROOT/docker-compose.yml"
docker exec -u node terry cp /home/node/.openclaw/openclaw.json "/home/node/.openclaw/openclaw.json.bak-gemini-video-$BACKUP_ID"

docker run --rm \
  -v "$STAGE_ROOT/service:/source:ro" \
  -v /opt/openclaw/shared:/shared \
  alpine:3.20 \
  sh -lc 'mkdir -p /shared/tools && cp -a /source /shared/tools/z-gemini-video-mcp'
docker run --rm \
  -v "$STAGE_ROOT/skill:/source:ro" \
  -v "$AGENT_ROOT/workspace/skills:/skills" \
  alpine:3.20 \
  sh -lc 'cp -a /source /skills/z-video-analysis'
docker exec -u root terry sh -lc \
  'find /opt/openclaw/shared/tools/z-gemini-video-mcp /home/node/.openclaw/workspace/skills/z-video-analysis -type d -exec chmod 755 {} +; find /opt/openclaw/shared/tools/z-gemini-video-mcp /home/node/.openclaw/workspace/skills/z-video-analysis -type f -exec chmod 644 {} +'

if ! grep -q '^GEMINI_API_KEY=' "$AGENT_ROOT/.env"; then
  printf '\nGEMINI_API_KEY=%s\n' "$SECRET_REFERENCE" >> "$AGENT_ROOT/.env"
fi

if ! grep -q '^[[:space:]]*GEMINI_API_KEY:' "$AGENT_ROOT/docker-compose.yml"; then
  sed -i '/^[[:space:]]*PERCIFY_API_KEY:/a\      GEMINI_API_KEY: ${GEMINI_API_KEY}' "$AGENT_ROOT/docker-compose.yml"
fi

docker exec -u root terry sh -lc 'cd /opt/openclaw/shared/tools/z-gemini-video-mcp && npm ci --omit=dev'
docker exec -u root terry chown -R 1000:1000 \
  /opt/openclaw/shared/tools/z-gemini-video-mcp \
  /home/node/.openclaw/workspace/skills/z-video-analysis

docker exec -u node terry openclaw mcp add gemini-video \
  --command node \
  --arg /opt/openclaw/shared/tools/z-gemini-video-mcp/server.mjs \
  --env 'GEMINI_API_KEY=${GEMINI_API_KEY}' \
  --include analyze_youtube_video \
  --timeout 600 \
  --approval auto \
  --no-probe

"$AGENT_ROOT/op-start-terry.sh" restart

echo "Terry Gemini video deployment installed. Backup: $BACKUP_ROOT"
