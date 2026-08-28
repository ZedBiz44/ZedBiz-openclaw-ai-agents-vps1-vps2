#!/usr/bin/env bash
set -euo pipefail

workspace_gid="11298561585567"
expected_skill_hash="${EXPECTED_SKILL_HASH:?EXPECTED_SKILL_HASH is required}"
source_root="/opt/zedbiz-asana-http-mcp"
verify_script="${source_root}/verify-vps2-agent.mjs"

for spec in "harry:4110" "suzy:4210" "frank:4310"; do
  agent="${spec%%:*}"
  port="${spec##*:}"
  state_dir="/root/.openclaw-${agent}"
  openclaw_dir="/opt/openclaw-${agent}"
  openclaw_bin="${openclaw_dir}/node_modules/.bin/openclaw"
  openclaw_config="${state_dir}/openclaw.json"
  openclaw_env="${state_dir}/.env"
  skill_file="${state_dir}/workspace/skills/z-asana-agent-control/SKILL.md"
  legacy_name="zedbiz-asana-agent-control"

  systemctl is-active --quiet "zedbiz-asana-mcp@${agent}.service"
  systemctl is-active --quiet "openclaw-${agent}.service"
  ss -ltn "sport = :${port}" | tail -n +2 | grep -q "127.0.0.1:${port}"
  curl -fsS "http://127.0.0.1:${port}/healthz" | jq -e '.ok == true' >/dev/null

  grep -Fxq "ASANA_ACCESS_TOKEN=op://agent-${agent}/asana-api-key-${agent}/credential" "$openclaw_env"
  grep -Fxq "MCP_AUTH_TOKEN=op://agent-${agent}/asana-api-key-${agent}/credential" "$openclaw_env"
  grep -Fxq "MCP_BIND_HOST=127.0.0.1" "$openclaw_env"
  jq -e --arg url "http://127.0.0.1:${port}/mcp" \
    '.mcp.servers.asana.url == $url and .mcp.servers.asana.headers.Authorization == "Bearer ${ASANA_ACCESS_TOKEN}"' \
    "$openclaw_config" >/dev/null

  test -f "$skill_file"
  test "$(sha256sum "$skill_file" | awk '{print $1}')" = "$expected_skill_hash"
  ! find "${state_dir}/workspace/skills" -mindepth 1 -maxdepth 1 -iname "${legacy_name}*" -print -quit | grep -q .
  if rg -uu -l "$legacy_name" "${state_dir}/workspace/skills" "${state_dir}/backups" 2>/dev/null | grep -q .; then
    echo "Retired skill reference remains for ${agent}" >&2
    exit 1
  fi

  export OP_SERVICE_ACCOUNT_TOKEN="$(tr -d '\r\n' < "${state_dir}/.op.token")"
  expected_email="$(op read "op://agent-${agent}/email-address-${agent}/credential")"
  export MCP_AUTH_TOKEN="$(op read "op://agent-${agent}/asana-api-key-${agent}/credential")"
  preflight="$(node "$verify_script" "$agent" "http://127.0.0.1:${port}/mcp" "$expected_email" "$workspace_gid")"
  unset OP_SERVICE_ACCOUNT_TOKEN MCP_AUTH_TOKEN expected_email

  HOME="$state_dir" OPENCLAW_STATE_DIR="$state_dir" OPENCLAW_CONFIG_PATH="$openclaw_config" "$openclaw_bin" mcp list 2>/dev/null | grep -q 'asana'
  HOME="$state_dir" OPENCLAW_STATE_DIR="$state_dir" OPENCLAW_CONFIG_PATH="$openclaw_config" "$openclaw_bin" skills list 2>/dev/null | grep -q 'z-asana-agent-control'
  ! HOME="$state_dir" OPENCLAW_STATE_DIR="$state_dir" OPENCLAW_CONFIG_PATH="$openclaw_config" "$openclaw_bin" skills list 2>/dev/null | grep -q "$legacy_name"

  jq --arg port "$port" '. + {service_bind:("127.0.0.1:" + $port),openclaw_mcp_route:"asana",skill:"z-asana-agent-control",legacy_skill:"absent"}' <<<"$preflight"
done
