#!/usr/bin/env bash
set -euo pipefail

agents=(amanda marsha terry victor wilma inga gohzed grogar maggie vivian edith)
failures=0

for agent in "${agents[@]}"; do
  toolset="standard"
  expected_image="zedbiz/asana-http-mcp:2.0.0-standard"
  expected_tools=76
  if [[ "${agent}" == "amanda" || "${agent}" == "marsha" ]]; then
    toolset="advanced"
    expected_image="zedbiz/asana-http-mcp:2.0.0-advanced"
    expected_tools=126
  fi

  main_health="$(docker inspect -f '{{.State.Health.Status}}' "${agent}")"
  sidecar="${agent}-asana-mcp"
  sidecar_health="$(docker inspect -f '{{.State.Health.Status}}' "${sidecar}")"
  image="$(docker inspect -f '{{.Config.Image}}' "${sidecar}")"
  main_pids="$(docker exec "${agent}" sh -lc 'cat /sys/fs/cgroup/pids.current')"
  sidecar_pids="$(docker exec "${sidecar}" sh -lc 'cat /sys/fs/cgroup/pids.current')"

  [[ "${main_health}" == "healthy" ]] || failures=$((failures + 1))
  [[ "${sidecar_health}" == "healthy" ]] || failures=$((failures + 1))
  [[ "${image}" == "${expected_image}" ]] || failures=$((failures + 1))

  if docker exec "${agent}" sh -lc \
    'ps -e -o args 2>/dev/null | grep -E "mcp-server-asana|npm exec @roychri" | grep -v grep' \
    >/dev/null; then
    echo "FAIL|${agent}|stdio Asana child found"
    failures=$((failures + 1))
  fi

  docker exec "${agent}" sh -lc \
    'test -r /home/node/.openclaw/skills/zedbiz-asana-agent-control/SKILL.md' ||
    failures=$((failures + 1))
  if [[ "${toolset}" == "advanced" ]]; then
    docker exec "${agent}" sh -lc \
      'test -r /home/node/.openclaw/skills/zedbiz-advanced-asana-control/SKILL.md' ||
      failures=$((failures + 1))
  fi

  channels="/tmp/asana-v2-${agent}-channels.json"
  docker exec "${agent}" openclaw channels status --probe --json >"${channels}"
  channel_result="$(
    python3 - "${channels}" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    data = json.load(handle)
discord = data.get("channels", {}).get("discord", {})
probe = discord.get("probe", {})
ok = bool(discord.get("configured") and discord.get("running") and probe.get("ok"))
print("ok" if ok else "failed")
PY
  )"
  [[ "${channel_result}" == "ok" ]] || failures=$((failures + 1))

  echo "AUDIT|${agent}|${toolset}|tools=${expected_tools}|main=${main_health}|sidecar=${sidecar_health}|discord=${channel_result}|main_pids=${main_pids}|sidecar_pids=${sidecar_pids}"
done

if docker ps -a --format '{{.Names}}' | grep -q '^amanda-asana-team-mcp$'; then
  echo "FAIL|amanda|old team sidecar still exists"
  failures=$((failures + 1))
fi

if [[ "${failures}" -ne 0 ]]; then
  echo "FLEET_AUDIT_FAILED|failures=${failures}"
  exit 1
fi

echo "FLEET_AUDIT_PASS|agents=${#agents[@]}"
