#!/usr/bin/env bash
set -euo pipefail

agents=(amanda edith gohzed grogar inga maggie marsha terry victor vivian wilma)

for agent in "${agents[@]}"; do
  case "${agent}" in
    terry|vivian) expected_image="zedbiz/openclaw-base:2026.8.2-video" ;;
    victor) expected_image="zedbiz-openclaw-victor:2026.8.2-ssh" ;;
    *) expected_image="ghcr.io/zedbiz44/openclaw-base:2026.8.2" ;;
  esac

  health="$(docker inspect "${agent}" --format '{{.State.Health.Status}}')"
  restarts="$(docker inspect "${agent}" --format '{{.RestartCount}}')"
  image="$(docker inspect "${agent}" --format '{{.Config.Image}}')"
  version="$(docker exec "${agent}" openclaw --version | awk '{print $2}')"
  config="$(docker exec "${agent}" node -e '
    const c = require("/home/node/.openclaw/openclaw.json");
    console.log([
      c.session && c.session.dmScope,
      c.tools && c.tools.sessions && c.tools.sessions.visibility,
      c.mcp && c.mcp.servers && c.mcp.servers.asana && c.mcp.servers.asana.transport,
      ((c.gateway && c.gateway.trustedProxies) || []).join(",")
    ].join("|"));
  ')"

  [[ "${health}" == "healthy" ]]
  [[ "${restarts}" == "0" ]]
  [[ "${image}" == "${expected_image}" ]]
  [[ "${version}" == "2026.8.2" ]]
  [[ "${config}" == "per-channel-peer|tree|streamable-http|172.18.0.0/16" ]]

  printf '%s|%s|%s|%s|%s|%s\n' \
    "${agent}" "${health}" "${restarts}" "${image}" "${version}" "${config}"
done

audit_runtime() {
  local agent="$1" plugin_output status_file skills_file
  plugin_output="$(docker exec "${agent}" openclaw plugins update --all --dry-run 2>&1 || true)"
  if grep -q 'Would update' <<<"${plugin_output}"; then
    printf '%s|PENDING_PLUGIN_UPDATE\n%s\n' "${agent}" "${plugin_output}"
    return 1
  fi

  status_file="/tmp/${agent}-2026.8.2-final-status.txt"
  skills_file="/tmp/${agent}-2026.8.2-final-skills.json"
  docker exec "${agent}" openclaw status --deep --timeout 15000 >"${status_file}"
  grep -q '│ Gateway[[:space:]]*│ reachable' "${status_file}"
  grep -q '│ Event loop[[:space:]]*│ OK' "${status_file}"
  docker exec "${agent}" openclaw skills check --agent main --json >"${skills_file}"
  jq -e 'type == "object"' "${skills_file}" >/dev/null
  printf '%s|PLUGINS_CURRENT|GATEWAY_REACHABLE|EVENT_LOOP_OK|SKILLS_CHECK_OK\n' "${agent}"
}

export -f audit_runtime
printf '%s\n' "${agents[@]}" | xargs -n1 -P2 bash -c 'audit_runtime "$1"' _
