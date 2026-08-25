#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || ! "$1" =~ ^(terry|vivian)$ ]]; then
  echo "Usage: $0 <terry|vivian>" >&2
  exit 2
fi

agent="$1"
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
key="${MANUS_VPS1_KEY:-$HOME/.ssh/Manus_key}"
host="${MANUS_VPS1_HOST:-jackadmin@187.77.210.223}"
remote_tmp="/tmp/${agent}-combined-tool-policy"
override="$repo_dir/agents/$agent/combined-tool-override.json"
policy="$repo_dir/policies/combined-tool-policy.md"
updater="$repo_dir/scripts/apply_combined_tool_policy.js"
launcher="/opt/openclaw/agents/$agent/op-start-$agent.sh"

for file in "$override" "$policy" "$updater"; do
  [[ -f "$file" ]] || { echo "Missing required file: $file" >&2; exit 1; }
done

ssh -o BatchMode=yes -o ConnectTimeout=15 -i "$key" "$host" "mkdir -p '$remote_tmp'"
scp -q -i "$key" "$override" "$policy" "$updater" "$host:$remote_tmp/"

result=$(ssh -o BatchMode=yes -o ConnectTimeout=15 -i "$key" "$host" "
  docker cp '$remote_tmp/combined-tool-override.json' '$agent:/tmp/combined-tool-override.json' &&
  docker cp '$remote_tmp/combined-tool-policy.md' '$agent:/tmp/combined-tool-policy.md' &&
  docker cp '$remote_tmp/apply_combined_tool_policy.js' '$agent:/tmp/apply_combined_tool_policy.js' &&
  docker exec --user node '$agent' node /tmp/apply_combined_tool_policy.js \
    /home/node/.openclaw/openclaw.json \
    /home/node/.openclaw/workspace/AGENTS.md \
    /tmp/combined-tool-policy.md \
    /tmp/combined-tool-override.json \
    /home/node/.openclaw/backups
")
printf '%s\n' "$result"

config_changed=$(printf '%s' "$result" | jq -r '.configChanged')
if [[ "$config_changed" == "true" ]]; then
  ssh -o BatchMode=yes -o ConnectTimeout=15 -i "$key" "$host" "bash '$launcher' restart"
fi

ssh -o BatchMode=yes -o ConnectTimeout=15 -i "$key" "$host" "
  docker inspect -f 'HEALTH={{if .State.Health}}{{.State.Health.Status}}{{end}}' '$agent' &&
  docker exec '$agent' bash -lc '
    jq -c \"{sol:.agents.defaults.models[\\\"openai/gpt-5.6-sol\\\"].agentRuntime.id,terra:.agents.defaults.models[\\\"openai/gpt-5.6-terra\\\"].agentRuntime.id,luna:.agents.defaults.models[\\\"openai/gpt-5.6-luna\\\"].agentRuntime.id}\" /home/node/.openclaw/openclaw.json &&
    sha256sum /home/node/.openclaw/workspace/AGENTS.md &&
    grep -q \"BEGIN ZEDBIZ COMBINED TOOL POLICY\" /home/node/.openclaw/workspace/AGENTS.md
  '
"
