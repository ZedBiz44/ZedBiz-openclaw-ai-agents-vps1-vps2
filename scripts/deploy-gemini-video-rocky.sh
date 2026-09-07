#!/usr/bin/env bash
set -euo pipefail

readonly RUNTIME_USER="openclaw"
readonly RUNTIME_HOME="/home/openclaw"
readonly STATE_ROOT="$RUNTIME_HOME/.openclaw"
readonly TOOL_ROOT="$RUNTIME_HOME/.local/share/openclaw-tools/z-gemini-video-mcp"
readonly SKILL_ROOT="$STATE_ROOT/workspace/skills/z-video-analysis"
readonly START_WRAPPER="$RUNTIME_HOME/bin/openclaw-gateway-discord"
readonly OPENCLAW_BIN="$RUNTIME_HOME/.npm-global/bin/openclaw"
readonly STAGE_ROOT="${1:-}"

if [[ -z "$STAGE_ROOT" || ! -f "$STAGE_ROOT/service/package-lock.json" || ! -f "$STAGE_ROOT/skill/SKILL.md" ]]; then
  echo "Usage: deploy-gemini-video-rocky.sh <verified-stage-directory>" >&2
  exit 2
fi

for required in "$STATE_ROOT/openclaw.json" "$START_WRAPPER" "$OPENCLAW_BIN"; do
  [[ -f "$required" ]] || { echo "Required Rocky file is missing: $required" >&2; exit 3; }
done

if [[ -e "$TOOL_ROOT" || -e "$SKILL_ROOT" ]]; then
  echo "A Gemini video deployment path already exists. Stop and inspect it before replacing anything." >&2
  exit 4
fi

readonly BACKUP_ID="$(date -u +%Y%m%dT%H%M%SZ)"
readonly BACKUP_ROOT="$STATE_ROOT/backups/$BACKUP_ID-gemini-video"
mkdir -p "$BACKUP_ROOT"
cp -a "$STATE_ROOT/openclaw.json" "$BACKUP_ROOT/openclaw.json"
cp -a "$START_WRAPPER" "$BACKUP_ROOT/openclaw-gateway-discord"

mkdir -p "$(dirname "$TOOL_ROOT")"
cp -a "$STAGE_ROOT/service" "$TOOL_ROOT"
cp -a "$STAGE_ROOT/skill" "$SKILL_ROOT"
chown -R "$RUNTIME_USER:$RUNTIME_USER" "$TOOL_ROOT" "$SKILL_ROOT"
find "$TOOL_ROOT" "$SKILL_ROOT" -type d -exec chmod u+rwx,go+rx {} +
find "$TOOL_ROOT" "$SKILL_ROOT" -type f -exec chmod u+rw,go+r {} +

if ! grep -q '^export GEMINI_API_KEY=' "$START_WRAPPER"; then
  sed -i '/^exec /i export GEMINI_API_KEY="$(op read '\''op://openclaw-agents-shared/gemini-video-api-key/credential'\'')"' "$START_WRAPPER"
fi

cd "$TOOL_ROOT"
runuser -u "$RUNTIME_USER" -- env HOME="$RUNTIME_HOME" npm ci --omit=dev

runuser -u "$RUNTIME_USER" -- env HOME="$RUNTIME_HOME" "$OPENCLAW_BIN" mcp add gemini-video \
  --command node \
  --arg "$TOOL_ROOT/server.mjs" \
  --env 'GEMINI_API_KEY=${GEMINI_API_KEY}' \
  --include analyze_youtube_video \
  --timeout 600 \
  --approval auto \
  --no-probe

systemctl --user -M openclaw@ restart openclaw-gateway.service
systemctl --user -M openclaw@ is-active --quiet openclaw-gateway.service

echo "Rocky Gemini video deployment completed. Backup: $BACKUP_ROOT"
