#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 || ! "$1" =~ ^(terry|vivian)$ ]]; then
  echo "Usage: $0 <terry|vivian> <backup-directory-inside-container>" >&2
  exit 2
fi

agent="$1"
backup_dir="$2"
key="${MANUS_VPS1_KEY:-$HOME/.ssh/Manus_key}"
host="${MANUS_VPS1_HOST:-jackadmin@187.77.210.223}"
launcher="/opt/openclaw/agents/$agent/op-start-$agent.sh"

ssh -o BatchMode=yes -o ConnectTimeout=15 -i "$key" "$host" "
  docker exec --user node '$agent' bash -lc '
    set -euo pipefail
    test -f \"$backup_dir/openclaw.json\"
    test -f \"$backup_dir/AGENTS.md\"
    cp -p \"$backup_dir/openclaw.json\" /home/node/.openclaw/openclaw.json
    cp -p \"$backup_dir/AGENTS.md\" /home/node/.openclaw/workspace/AGENTS.md
    chmod 600 /home/node/.openclaw/openclaw.json
  '
  bash '$launcher' restart
  docker inspect -f 'HEALTH={{if .State.Health}}{{.State.Health.Status}}{{end}}' '$agent'
"
