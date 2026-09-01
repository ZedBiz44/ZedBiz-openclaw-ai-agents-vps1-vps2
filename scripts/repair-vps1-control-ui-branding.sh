#!/usr/bin/env bash
set -euo pipefail

# OpenClaw 2026.8.2 reads the agent name from runtime identity and the sidebar
# image from a conventional icon inside the agent workspace. The older VPS1
# branding hook only patched static Control UI files.

declare -A DISPLAY_NAMES=(
  [amanda]="Amanda"
  [edith]="Edith"
  [gohzed]="Gohzed"
  [grogar]="Grogar"
  [inga]="Inga"
  [maggie]="Maggie"
  [marsha]="Marsha"
  [terry]="Terry"
  [victor]="Victor"
  [vivian]="Vivian"
  [wilma]="Wilma"
)

agents=(amanda edith gohzed grogar inga maggie marsha terry victor vivian wilma)

wait_healthy() {
  local container="$1"
  local attempts=24
  local status=""

  for ((i = 1; i <= attempts; i++)); do
    status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container" 2>/dev/null || true)"
    if [[ "$status" == "healthy" || "$status" == "running" ]]; then
      printf '%s\n' "[branding] ${container}: ${status}"
      return 0
    fi
    sleep 5
  done

  printf '%s\n' "[branding] ${container}: failed health wait (last status: ${status:-missing})" >&2
  return 1
}

for agent in "${agents[@]}"; do
  name="${DISPLAY_NAMES[$agent]}"

  if ! docker inspect "$agent" >/dev/null 2>&1; then
    printf '%s\n' "[branding] ${agent}: container not found" >&2
    exit 1
  fi

  docker exec "$agent" sh -lc '
    set -eu
    branding=/app/dist/control-ui/branding
    workspace=/home/node/.openclaw/workspace
    mkdir -p "$workspace/avatars" "$workspace/assets"
    cp "$branding/avatar.png" "$workspace/avatars/openclaw.png"
    cp "$branding/avatar.png" "$workspace/favicon.png"
    cp "$branding/avatar.png" "$workspace/assets/logo.png"
    if [ -f "$branding/favicon.svg" ]; then
      cp "$branding/favicon.svg" "$workspace/favicon.svg"
    fi
    chmod 644 "$workspace/avatars/openclaw.png" "$workspace/favicon.png" "$workspace/assets/logo.png"
    [ ! -f "$workspace/favicon.svg" ] || chmod 644 "$workspace/favicon.svg"
  '

  docker exec "$agent" openclaw agents set-identity \
    --agent main \
    --name "$name" \
    --avatar avatars/openclaw.png \
    --json >/dev/null

  if ! docker exec "$agent" grep -q 'OPENCLAW_2026_8_2_RUNTIME_IDENTITY' /home/node/.openclaw/workspace/post-start.sh; then
    docker exec -i "$agent" sh -c 'cat >> /home/node/.openclaw/workspace/post-start.sh' <<'POST_START_BLOCK'

# OPENCLAW_2026_8_2_RUNTIME_IDENTITY
# The 2026.8.2 Control UI reads identity from agent config and the sidebar icon
# from the workspace. Keep both populated after every container recreation.
if [ -f "$BRANDING_DIR/avatar.png" ]; then
  mkdir -p /home/node/.openclaw/workspace/avatars /home/node/.openclaw/workspace/assets
  cp "$BRANDING_DIR/avatar.png" /home/node/.openclaw/workspace/avatars/openclaw.png
  cp "$BRANDING_DIR/avatar.png" /home/node/.openclaw/workspace/favicon.png
  cp "$BRANDING_DIR/avatar.png" /home/node/.openclaw/workspace/assets/logo.png
  chmod 644 /home/node/.openclaw/workspace/avatars/openclaw.png \
    /home/node/.openclaw/workspace/favicon.png \
    /home/node/.openclaw/workspace/assets/logo.png
fi
if [ -f "$BRANDING_DIR/favicon.svg" ]; then
  cp "$BRANDING_DIR/favicon.svg" /home/node/.openclaw/workspace/favicon.svg
  chmod 644 /home/node/.openclaw/workspace/favicon.svg
fi
openclaw agents set-identity --agent main --name "$AGENT_NAME" \
  --avatar avatars/openclaw.png >/dev/null 2>&1 || true
POST_START_BLOCK
  fi

  docker restart "$agent" >/dev/null
  wait_healthy "$agent"

  docker exec "$agent" openclaw agents list --json | grep -q "\"identityName\": \"$name\""
  docker exec "$agent" test -s /home/node/.openclaw/workspace/favicon.png
  docker exec "$agent" test -s /home/node/.openclaw/workspace/avatars/openclaw.png
  printf '%s\n' "[branding] ${agent}: identity and workspace icon verified"
done

printf '%s\n' '[branding] all VPS1 agents repaired and healthy'
