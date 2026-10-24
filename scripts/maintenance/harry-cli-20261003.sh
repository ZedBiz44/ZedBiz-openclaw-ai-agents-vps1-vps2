#!/bin/bash
set -euo pipefail
export OP_SERVICE_ACCOUNT_TOKEN="$(cat /root/.openclaw-harry/.op.token)"
export HOME=/root/.openclaw-harry OPENCLAW_STATE_DIR=/root/.openclaw-harry OPENCLAW_CONFIG_PATH=/root/.openclaw-harry/openclaw.json
export NODE_OPTIONS=--max-old-space-size=1536
exec op run --env-file=/root/.openclaw-harry/.env -- /opt/openclaw-harry/node_modules/.bin/openclaw "$@"
