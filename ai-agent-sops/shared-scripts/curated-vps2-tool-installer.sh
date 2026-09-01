#!/usr/bin/env bash
set -Eeuo pipefail

AGENT="${1:-}"
EXPECTED_VERSION="${2:-}"

if [[ ! "$AGENT" =~ ^[a-z0-9-]+$ ]] || [[ ! "$EXPECTED_VERSION" =~ ^[0-9]{4}\.[0-9]+\.[0-9]+([.-][A-Za-z0-9]+)*$ ]]; then
  echo "Usage: curated-vps2-tool-installer.sh agent-slug exact-core-version" >&2
  exit 64
fi

INSTALL_DIR="/opt/openclaw-${AGENT}"
STATE_DIR="/root/.openclaw-${AGENT}"
CONFIG_PATH="${STATE_DIR}/openclaw.json"
ENV_FILE="${STATE_DIR}/.env"
OP_TOKEN_FILE="${STATE_DIR}/.op.token"
BIN="${INSTALL_DIR}/node_modules/.bin/openclaw"
SERVICE="openclaw-${AGENT}"
WORKSPACE="${STATE_DIR}/workspace"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG_DIR="/root/openclaw-tool-update-logs"
LOG_FILE="${LOG_DIR}/${AGENT}-${STAMP}.log"
BACKUP_DIR="/root/backups/curated-vps2-tools/${AGENT}-${STAMP}"

for required in "$BIN" "$CONFIG_PATH" "$ENV_FILE" "$OP_TOKEN_FILE"; do
  test -e "$required" || { echo "Missing required path: $required" >&2; exit 1; }
done

export OP_SERVICE_ACCOUNT_TOKEN="$(tr -d '\r\n' < "$OP_TOKEN_FILE")"
export HOME="$STATE_DIR"
export OPENCLAW_STATE_DIR="$STATE_DIR"
export OPENCLAW_CONFIG_PATH="$CONFIG_PATH"

run() {
  /usr/bin/op run --env-file="$ENV_FILE" -- "$@"
}

mkdir -p "$LOG_DIR" "$BACKUP_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

CORE_VERSION="$(run "$BIN" --version | awk '{print $2}')"

if [[ "$CORE_VERSION" != "$EXPECTED_VERSION" ]]; then
  echo "Refusing plugin update: core is $CORE_VERSION but expected $EXPECTED_VERSION." >&2
  echo "Update and verify the OpenClaw core first, then rerun this installer." >&2
  exit 1
fi

echo "Agent: $AGENT"
echo "OpenClaw core: $CORE_VERSION"
echo "State: $STATE_DIR"
echo "Log: $LOG_FILE"

tar -czf "$BACKUP_DIR/plugin-state-before.tar.gz" -C "$STATE_DIR" openclaw.json npm
sha256sum "$BACKUP_DIR/plugin-state-before.tar.gz" > "$BACKUP_DIR/SHA256SUMS"

run "$BIN" config validate
run "$BIN" plugins update --all --dry-run

update_args=(--all)
if [[ "${ACCEPT_PLUGIN_CAPABILITIES:-0}" == "1" ]]; then
  update_args+=(--accept-capabilities --acknowledge-install-policy-warning)
fi
run "$BIN" plugins update "${update_args[@]}"

if ! run "$BIN" plugins doctor; then
  echo "Plugin doctor reported a configuration warning; continuing to the post-upgrade structural probe."
fi
run "$BIN" doctor --post-upgrade --json

if command -v clawhub >/dev/null 2>&1 && test -d "$WORKSPACE"; then
  if ! (cd "$WORKSPACE" && run clawhub update --all); then
    echo "ClawHub did not overwrite a locally modified skill; review the reported skill manually."
  fi
fi

skills_json="$(run "$BIN" skills check --json)"
echo "$skills_json" | jq '{eligible:(.eligible|length),disabled:(.disabled|length),blocked:(.blocked|length),missing:(.missingRequirements|length)}'
blocked="$(echo "$skills_json" | jq '(.blocked|length) + (.missingRequirements|length)')"
test "$blocked" -eq 0 || { echo "Blocked or missing skill requirements remain." >&2; exit 1; }

systemctl restart "$SERVICE"
sleep 8
systemctl is-active --quiet "$SERVICE"
run "$BIN" gateway status --json | jq -e --arg version "$CORE_VERSION" '.rpc.ok == true and .rpc.version == $version' >/dev/null
run "$BIN" plugins update --all --dry-run
run "$BIN" doctor --post-upgrade --json

echo "Curated VPS2 plugin and skill update complete."
echo "Backup: $BACKUP_DIR"
echo "Log: $LOG_FILE"

