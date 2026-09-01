#!/usr/bin/env bash
set -euo pipefail

agent="${1:?usage: update-vps1-openclaw-agent.sh AGENT IMAGE}"
image="${2:?usage: update-vps1-openclaw-agent.sh AGENT IMAGE}"
agent_root="/opt/openclaw/agents/${agent}"
start_wrapper="${agent_root}/op-start-${agent}.sh"
backup_root="/opt/openclaw/backups/2026-09-01-openclaw-2026.8.2"
backup_file="${backup_root}/${agent}-pre-update.tar.gz"
batch_file="/tmp/${agent}-openclaw-2026.8.2-config.json"

case "${agent}" in
  amanda|edith|gohzed|grogar|inga|maggie|marsha|terry|victor|vivian|wilma) ;;
  *) echo "unsupported VPS1 agent: ${agent}" >&2; exit 2 ;;
esac

[[ -x "${start_wrapper}" ]] || { echo "missing start wrapper: ${start_wrapper}" >&2; exit 1; }
docker image inspect "${image}" >/dev/null

echo "${agent}: stopping for offline backup"
"${start_wrapper}" down

docker run --rm \
  -v "${agent_root}:/source:ro" \
  -v "${backup_root}:/backup" \
  alpine:3.22 sh -c "tar -czf /backup/${agent}-pre-update.tar.gz -C /source ."
sha256sum "${backup_file}"

sed -i "s|^OPENCLAW_IMAGE=.*|OPENCLAW_IMAGE=${image}|" "${agent_root}/.env"
grep '^OPENCLAW_IMAGE=' "${agent_root}/.env"
if [[ "${agent}" == "victor" ]]; then
  sed -i -E "0,/^([[:space:]]*)image: zedbiz-openclaw-victor:/s||\\1image: ${image}|" "${agent_root}/docker-compose.yml"
  grep -q "^[[:space:]]*image: ${image}$" "${agent_root}/docker-compose.yml"
fi

echo "${agent}: creating the 2026.8.2 container for maintenance"
"${start_wrapper}" up
docker update --restart=no "${agent}" >/dev/null
docker stop -t 20 "${agent}" >/dev/null || true

docker run --rm \
  --network openclaw \
  --volumes-from "${agent}" \
  --user node \
  --entrypoint openclaw \
  "${image}" doctor --fix --non-interactive --yes

printf '%s\n' '[{"path":"session.dmScope","value":"per-channel-peer"},{"path":"tools.sessions.visibility","value":"tree"},{"path":"gateway.trustedProxies","value":["172.18.0.0/16"]},{"path":"mcp.servers.asana.transport","value":"streamable-http"}]' > "${batch_file}"
docker run --rm \
  --volumes-from "${agent}" \
  -v "${batch_file}:/tmp/config-set.json:ro" \
  --user node \
  --entrypoint openclaw \
  "${image}" config set --batch-file /tmp/config-set.json
rm -f "${batch_file}"

"${start_wrapper}" up
docker update --restart=unless-stopped "${agent}" >/dev/null

for _ in $(seq 1 60); do
  health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${agent}" 2>/dev/null || true)"
  [[ "${health}" == "healthy" ]] && break
  sleep 3
done
[[ "${health:-}" == "healthy" ]] || { docker logs --tail 150 "${agent}"; exit 1; }

echo "${agent}: updating tracked plugins"
docker exec "${agent}" openclaw plugins update --all || true
for plugin in qwen memory-lancedb slack; do
  if docker exec "${agent}" openclaw plugins inspect "${plugin}" --json >/dev/null 2>&1; then
    docker exec "${agent}" openclaw plugins update "${plugin}" --accept-capabilities || true
  fi
done
if docker exec "${agent}" openclaw plugins update --all --dry-run 2>&1 | grep -q 'Would update voice-call:'; then
  docker exec "${agent}" openclaw plugins update @openclaw/voice-call@latest --accept-capabilities
fi

"${start_wrapper}" restart
for _ in $(seq 1 60); do
  health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${agent}" 2>/dev/null || true)"
  [[ "${health}" == "healthy" ]] && break
  sleep 3
done
[[ "${health:-}" == "healthy" ]] || { docker logs --tail 150 "${agent}"; exit 1; }

docker exec "${agent}" openclaw memory status --index --agent main --json >/tmp/"${agent}"-memory-status.json
docker exec "${agent}" openclaw status --deep --timeout 15000 >/tmp/"${agent}"-status.txt

[[ "$(docker exec "${agent}" openclaw config get session.dmScope)" == "per-channel-peer" ]]
[[ "$(docker exec "${agent}" openclaw config get tools.sessions.visibility)" == "tree" ]]
[[ "$(docker exec "${agent}" openclaw config get mcp.servers.asana.transport)" == "streamable-http" ]]
docker exec "${agent}" openclaw config get gateway.trustedProxies --json | grep -q '172.18.0.0/16'
docker exec "${agent}" openclaw --version | grep -q '2026.8.2'
plugins_json="$(docker exec "${agent}" openclaw plugins list --json || true)"
grep -q '"version": "2026.8.2"' <<<"${plugins_json}"
docker exec "${agent}" openclaw skills check --agent main --json >/tmp/"${agent}"-skills.json

echo "${agent}: COMPLETE image=${image} health=${health}"
