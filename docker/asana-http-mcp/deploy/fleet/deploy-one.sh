#!/usr/bin/env bash
set -euo pipefail

agent="${1:?agent is required}"
agent_name="${2:?agent name is required}"
email="${3:?email is required}"
user_gid="${4:?user gid is required}"
stamp="${5:?backup suffix is required}"

base="/opt/openclaw/agents/${agent}"
sidecar="${agent}-asana-mcp"
deploy_dir="/tmp/cody-fleet-deploy"
work="${deploy_dir}/live-${agent}"

if docker logs --since 90s "${agent}" 2>&1 |
  grep -Eq 'run started|turn started|dispatching agent|embedded run start'; then
  echo "SKIP|${agent}|recent active-turn signal"
  exit 42
fi

mkdir -p "${work}"
docker run --rm \
  -v "${base}":/agent \
  -v "${work}":/work \
  -v "${deploy_dir}":/in:ro \
  alpine sh -lc "
    set -eu
    cp /agent/docker-compose.yml /work/docker-compose.yml
    chown 1001:1001 /work/docker-compose.yml
    if [ ! -f /agent/docker-compose.yml.${stamp} ]; then
      cp /agent/docker-compose.yml /agent/docker-compose.yml.${stamp}
    fi
    if [ ! -f /agent/config/openclaw.json.${stamp} ]; then
      cp /agent/config/openclaw.json /agent/config/openclaw.json.${stamp}
    fi
    mkdir -p /agent/asana-http-mcp
    tar -xzf /in/asana-http-mcp-src.tar.gz -C /agent/asana-http-mcp
    chown -R 1001:1001 /agent/asana-http-mcp
  "

python3 "${deploy_dir}/patch-compose.py" \
  "${work}/docker-compose.yml" "${agent}" --backup-suffix "${stamp}"
docker compose \
  --env-file "${base}/.env" \
  -f "${work}/docker-compose.yml" \
  config --quiet
docker run --rm \
  -v "${base}":/agent \
  -v "${work}":/work \
  alpine cp /work/docker-compose.yml /agent/docker-compose.yml

docker run --rm \
  -v "${base}":/agent \
  -v "${deploy_dir}":/scripts:ro \
  node:24-alpine \
  node /scripts/switch-openclaw-mcp.mjs \
  /agent/config/openclaw.json "${agent}"

docker run --rm \
  -v "${base}":/agent \
  -v "${deploy_dir}":/scripts:ro \
  node:24-alpine \
  node /scripts/patch-agent-asana-guidance.mjs \
  /agent/workspace "${agent_name}" "${email}" "${user_gid}" "${stamp}"

docker run --rm \
  -v "${base}":/agent \
  -v "${deploy_dir}":/in:ro \
  alpine sh -lc "
    set -eu
    if [ -d /agent/skills/zedbiz-asana-agent-control ] &&
       [ ! -d /agent/skills/zedbiz-asana-agent-control.${stamp} ]; then
      cp -a /agent/skills/zedbiz-asana-agent-control \
        /agent/skills/zedbiz-asana-agent-control.${stamp}
    fi
    tar -xzf /in/zedbiz-asana-agent-control.tar.gz -C /agent/skills
    chown -R 1000:1000 \
      /agent/skills/zedbiz-asana-agent-control \
      /agent/workspace/TOOLS.md \
      /agent/config/openclaw.json
  "

"${base}/op-start-${agent}.sh" restart

for container in "${sidecar}" "${agent}"; do
  health=""
  for _ in $(seq 1 60); do
    health="$(
      docker inspect -f \
        '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' \
        "${container}" 2>/dev/null || true
    )"
    [[ "${health}" == "healthy" ]] && break
    sleep 2
  done
  if [[ "${health}" != "healthy" ]]; then
    docker logs --tail 100 "${container}" || true
    echo "FAIL|${agent}|${container} health=${health}"
    exit 1
  fi
done

docker cp "${deploy_dir}/provision-portfolio-viewer.mjs" \
  amanda:/home/node/provision-portfolio-viewer.mjs
docker exec amanda node /home/node/provision-portfolio-viewer.mjs \
  "${user_gid}" "${email}"

docker cp "${deploy_dir}/verify-standard-sidecar.mjs" \
  "${sidecar}":/app/verify-standard-sidecar.mjs
docker exec "${sidecar}" node /app/verify-standard-sidecar.mjs \
  "${user_gid}" "${email}" 5

docker exec "${agent}" openclaw channels status --probe --json \
  >"${work}/channels.json"
python3 - "${work}/channels.json" "${agent}" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    data = json.load(handle)
discord = data.get("channels", {}).get("discord", {})
probe = discord.get("probe", {})
if not (discord.get("configured") and discord.get("running") and probe.get("ok")):
    raise SystemExit(f"{sys.argv[2]} Discord probe failed: {discord}")
print(f"discord=ok bot={probe.get('bot', {}).get('username')}")
PY

if docker exec "${agent}" sh -lc \
  'ps -e -o args 2>/dev/null | grep -E "mcp-server-asana|npm exec @roychri" | grep -v grep'
then
  echo "FAIL|${agent}|stdio Asana process remains"
  exit 1
fi

if [[ "${agent}" == "wilma" ]]; then
  docker exec wilma node -e '
    const fs = require("fs");
    const config = JSON.parse(
      fs.readFileSync("/home/node/.openclaw/openclaw.json", "utf8"),
    );
    const route = config.mcp?.servers?.["wordpress-allzed"];
    if (route?.url !== "https://allzed.com/wp-json/mcp/v1/http") {
      throw new Error("Wilma WordPress MCP route changed");
    }
    console.log("wordpress-allzed=preserved");
  '
fi

main_pids="$(
  docker exec "${agent}" sh -lc 'cat /sys/fs/cgroup/pids.current'
)"
sidecar_pids="$(
  docker exec "${sidecar}" sh -lc 'cat /sys/fs/cgroup/pids.current'
)"
echo "PASS|${agent}|main_pids=${main_pids}|sidecar_pids=${sidecar_pids}"
