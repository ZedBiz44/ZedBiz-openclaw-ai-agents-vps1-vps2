#!/usr/bin/env bash
set -euo pipefail

agent="${1:?agent is required}"
toolset="${2:?standard or advanced is required}"
agent_name="${3:?agent name is required}"
email="${4:?email is required}"
user_gid="${5:?user gid is required}"
team_gid="${6:-1216007690588299}"
team_name="${7:-Z1AM-ZedBiz-Main}"
stamp="${8:?backup suffix is required}"

if [[ "${toolset}" != "standard" && "${toolset}" != "advanced" ]]; then
  echo "toolset must be standard or advanced" >&2
  exit 2
fi

base="/opt/openclaw/agents/${agent}"
sidecar="${agent}-asana-mcp"
old_team_sidecar="${agent}-asana-team-mcp"
deploy_dir="/tmp/cody-asana-v2-20260730"
work="${deploy_dir}/live-${agent}"

if docker logs --since 120s "${agent}" 2>&1 |
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
    [ -f /agent/docker-compose.yml.${stamp} ] ||
      cp /agent/docker-compose.yml /agent/docker-compose.yml.${stamp}
    [ -f /agent/config/openclaw.json.${stamp} ] ||
      cp /agent/config/openclaw.json /agent/config/openclaw.json.${stamp}
    [ -f /agent/workspace/TOOLS.md.${stamp} ] ||
      cp /agent/workspace/TOOLS.md /agent/workspace/TOOLS.md.${stamp}
    mkdir -p /agent/asana-http-mcp
    find /agent/asana-http-mcp -mindepth 1 -maxdepth 1 -exec rm -rf {} +
    tar -xzf /in/asana-http-mcp-src.tar.gz -C /agent/asana-http-mcp
    chown -R 1001:1001 /agent/asana-http-mcp
  "

python3 "${deploy_dir}/patch-compose-v2.py" \
  "${work}/docker-compose.yml" "${agent}" \
  --toolset "${toolset}" --backup-suffix "${stamp}"
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
  /agent/config/openclaw.json "${agent}" "${toolset}"

docker run --rm \
  -v "${base}":/agent \
  -v "${deploy_dir}":/scripts:ro \
  node:24-alpine \
  node /scripts/patch-agent-asana-guidance-v2.mjs \
  /agent/workspace "${toolset}" "${agent_name}" "${email}" "${user_gid}" "${stamp}"

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
    if [ '${toolset}' = advanced ]; then
      if [ -d /agent/skills/zedbiz-advanced-asana-control ] &&
         [ ! -d /agent/skills/zedbiz-advanced-asana-control.${stamp} ]; then
        cp -a /agent/skills/zedbiz-advanced-asana-control \
          /agent/skills/zedbiz-advanced-asana-control.${stamp}
      fi
      tar -xzf /in/zedbiz-advanced-asana-control.tar.gz -C /agent/skills
    fi
    chown -R 1000:1000 /agent/skills/zedbiz-asana-agent-control
    if [ '${toolset}' = advanced ]; then
      chown -R 1000:1000 /agent/skills/zedbiz-advanced-asana-control
    fi
    chown 1000:1000 /agent/workspace/TOOLS.md /agent/config/openclaw.json
  "

docker compose \
  --env-file "${base}/.env" \
  -f "${base}/docker-compose.yml" \
  build "${sidecar}"
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

docker cp "${deploy_dir}/verify-toolset.mjs" \
  "${sidecar}":/app/verify-toolset.mjs
docker exec "${sidecar}" node /app/verify-toolset.mjs \
  "${toolset}" "${user_gid}" "${email}" "${team_gid}" "${team_name}"

docker exec "${agent}" sh -lc \
  'test -r /home/node/.openclaw/skills/zedbiz-asana-agent-control/SKILL.md'
if [[ "${toolset}" == "advanced" ]]; then
  docker exec "${agent}" sh -lc \
    'test -r /home/node/.openclaw/skills/zedbiz-advanced-asana-control/SKILL.md'
fi

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

if [[ "${toolset}" == "advanced" ]] &&
   docker inspect "${old_team_sidecar}" >/dev/null 2>&1; then
  docker stop "${old_team_sidecar}"
  docker rm "${old_team_sidecar}"
fi

main_pids="$(docker exec "${agent}" sh -lc 'cat /sys/fs/cgroup/pids.current')"
sidecar_pids="$(docker exec "${sidecar}" sh -lc 'cat /sys/fs/cgroup/pids.current')"
echo "PASS|${agent}|${toolset}|main_pids=${main_pids}|sidecar_pids=${sidecar_pids}"
