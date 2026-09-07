#!/usr/bin/env bash
set -euo pipefail

readonly INSTALL_ROOT="/opt/openclaw-harry"
readonly STATE_ROOT="/root/.openclaw-harry"
readonly TOOL_ROOT="/opt/openclaw-shared/tools/z-gemini-video-mcp"
readonly SKILL_ROOT="$STATE_ROOT/workspace/skills/z-video-analysis"
readonly STAGE_ROOT="${1:-}"
readonly SECRET_REFERENCE='op://openclaw-agents-shared/gemini-video-api-key/credential'

if [[ -z "$STAGE_ROOT" || ! -f "$STAGE_ROOT/service/package-lock.json" || ! -f "$STAGE_ROOT/skill/SKILL.md" ]]; then
  echo "Usage: deploy-gemini-video-harry.sh <verified-stage-directory>" >&2
  exit 2
fi

for required in "$STATE_ROOT/.env" "$STATE_ROOT/openclaw.json" "$INSTALL_ROOT/start-harry.sh"; do
  [[ -f "$required" ]] || { echo "Required Harry file is missing: $required" >&2; exit 3; }
done

if [[ -e "$TOOL_ROOT" || -e "$SKILL_ROOT" ]]; then
  echo "A Gemini video deployment path already exists. Stop and inspect it before replacing anything." >&2
  exit 4
fi

readonly BACKUP_ID="$(date -u +%Y%m%dT%H%M%SZ)"
readonly BACKUP_ROOT="$STATE_ROOT/backups/$BACKUP_ID-gemini-video"
mkdir -p "$BACKUP_ROOT"
cp -a "$STATE_ROOT/.env" "$BACKUP_ROOT/.env"
cp -a "$STATE_ROOT/openclaw.json" "$BACKUP_ROOT/openclaw.json"
cp -a "$INSTALL_ROOT/start-harry.sh" "$BACKUP_ROOT/start-harry.sh"

mkdir -p "$(dirname "$TOOL_ROOT")"
cp -a "$STAGE_ROOT/service" "$TOOL_ROOT"
cp -a "$STAGE_ROOT/skill" "$SKILL_ROOT"

if ! grep -q '^GEMINI_API_KEY=' "$STATE_ROOT/.env"; then
  printf '\nGEMINI_API_KEY=%s\n' "$SECRET_REFERENCE" >> "$STATE_ROOT/.env"
fi

cd "$TOOL_ROOT"
npm ci --omit=dev

HOME="$STATE_ROOT" OPENCLAW_STATE_DIR="$STATE_ROOT" OPENCLAW_CONFIG_PATH="$STATE_ROOT/openclaw.json" \
  "$INSTALL_ROOT/node_modules/.bin/openclaw" mcp add gemini-video \
  --command node \
  --arg "$TOOL_ROOT/server.mjs" \
  --env 'GEMINI_API_KEY=${GEMINI_API_KEY}' \
  --include analyze_youtube_video \
  --timeout 600 \
  --approval auto \
  --no-probe

systemctl restart openclaw-harry
systemctl is-active --quiet openclaw-harry

export OP_SERVICE_ACCOUNT_TOKEN="$(cat "$STATE_ROOT/.op.token")"
op run --env-file="$STATE_ROOT/.env" -- env \
  HOME="$STATE_ROOT" \
  OPENCLAW_STATE_DIR="$STATE_ROOT" \
  OPENCLAW_CONFIG_PATH="$STATE_ROOT/openclaw.json" \
  "$INSTALL_ROOT/node_modules/.bin/openclaw" mcp probe gemini-video --json

echo "Harry Gemini video deployment completed. Backup: $BACKUP_ROOT"
