#!/bin/sh

# Purpose: Set the VPS1 OpenClaw gateway baseline to 3 GiB RAM with 1 GiB
# swap headroom (4 GiB combined Docker memory+swap limit).
# Added by: Cody
# Date added: 2026-08-26 Mountain Time
# Tested on: VPS1, /opt/openclaw/agents
# Rollback: restore each docker-compose.yml.bak-memory-* file and rerun
# `docker compose up -d --no-deps <agent>` from that agent directory.

set -eu

all_agents="grogar edith gohzed terry maggie inga marsha vivian victor amanda wilma"
agents="${*:-$all_agents}"
stamp="$(date +%Y%m%d-%H%M%S)"

compose_up() {
  agent_dir="$1"
  service="$2"

  if grep -q '=op://' "$agent_dir/.env" 2>/dev/null; then
    if [ -r "$agent_dir/.op.token" ]; then
      unset OP_CONNECT_HOST OP_CONNECT_TOKEN
      OP_SERVICE_ACCOUNT_TOKEN="$(tr -d '\r\n' <"$agent_dir/.op.token")"
      export OP_SERVICE_ACCOUNT_TOKEN
    elif [ -r /opt/openclaw/1password-connect/op-token.txt ]; then
      op_token="$(tr -d '\r\n' </opt/openclaw/1password-connect/op-token.txt)"
      case "$op_token" in
        ops_*)
          unset OP_CONNECT_HOST OP_CONNECT_TOKEN
          OP_SERVICE_ACCOUNT_TOKEN="$op_token"
          export OP_SERVICE_ACCOUNT_TOKEN
          ;;
        *)
          OP_CONNECT_TOKEN="$op_token"
          OP_CONNECT_HOST="${OP_CONNECT_HOST:-http://127.0.0.1:8080}"
          export OP_CONNECT_HOST OP_CONNECT_TOKEN
          ;;
      esac
    fi
    if ! (cd "$agent_dir" && op run --env-file=.env -- docker compose up -d --no-deps "$service"); then
      if [ -r "$agent_dir/.env.resolved" ] &&
         ! grep -q '=op://' "$agent_dir/.env.resolved"; then
        echo "$service: live vault resolution failed; using protected .env.resolved fallback" >&2
        (cd "$agent_dir" && docker compose --env-file .env.resolved up -d --no-deps "$service")
      else
        return 1
      fi
    fi
  else
    (cd "$agent_dir" && docker compose up -d --no-deps "$service")
  fi
}

for agent in $agents; do
  case " $all_agents " in
    *" $agent "*) ;;
    *) echo "Unknown VPS1 agent: $agent" >&2; exit 2 ;;
  esac

  dir="/opt/openclaw/agents/$agent"
  compose="$dir/docker-compose.yml"
  backup="$compose.bak-memory-$stamp"

  test -f "$compose" || { echo "Missing: $compose" >&2; exit 1; }
  cp "$compose" "$backup"

  # Only change the gateway's first resource pair. The agent's sidecar limit
  # remains unchanged.
  sed -i '0,/mem_limit: \(2g\|3g\)/s//mem_limit: 3g/' "$compose"
  sed -i '0,/memswap_limit: \(2560m\|4g\)/s//memswap_limit: 4g/' "$compose"

  if ! grep -q '^[[:space:]]*mem_limit: 3g$' "$compose" ||
     ! grep -q '^[[:space:]]*memswap_limit: 4g$' "$compose" ||
     ! docker compose -f "$compose" config -q; then
    cp "$backup" "$compose"
    echo "Validation failed; restored $backup" >&2
    exit 1
  fi

  compose_up "$dir" "$agent"

  memory="$(docker inspect "$agent" --format '{{.HostConfig.Memory}}')"
  memory_swap="$(docker inspect "$agent" --format '{{.HostConfig.MemorySwap}}')"
  status="$(docker inspect "$agent" --format '{{.State.Status}}')"

  if [ "$memory" != "3221225472" ] ||
     [ "$memory_swap" != "4294967296" ] ||
     [ "$status" != "running" ]; then
    cp "$backup" "$compose"
    compose_up "$dir" "$agent"
    echo "Live verification failed for $agent; rolled back" >&2
    exit 1
  fi

  echo "$agent: 3 GiB RAM, 4 GiB combined RAM+swap, running; backup=$backup"
done
