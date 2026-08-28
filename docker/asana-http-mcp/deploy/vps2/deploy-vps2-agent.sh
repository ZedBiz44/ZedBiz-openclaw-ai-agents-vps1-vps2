#!/usr/bin/env bash
set -euo pipefail

agent="${1:?Usage: deploy-vps2-agent.sh <harry|suzy|frank> <port>}"
port="${2:?Usage: deploy-vps2-agent.sh <harry|suzy|frank> <port>}"

case "$agent" in
  harry|suzy|frank) ;;
  *) echo "Unsupported VPS2 agent: $agent" >&2; exit 2 ;;
esac
case "$port" in
  4110|4210|4310) ;;
  *) echo "Use the approved loopback port for this deployment" >&2; exit 2 ;;
esac

workspace_gid="11298561585567"
state_dir="/root/.openclaw-${agent}"
openclaw_dir="/opt/openclaw-${agent}"
openclaw_bin="${openclaw_dir}/node_modules/.bin/openclaw"
openclaw_config="${state_dir}/openclaw.json"
openclaw_env="${state_dir}/.env"
workspace_skills="${state_dir}/workspace/skills"
service_name="zedbiz-asana-mcp@${agent}.service"
source_root="/opt/zedbiz-asana-http-mcp"
verify_script="${source_root}/verify-vps2-agent.mjs"
package_name="z-asana-agent-control"
legacy_name="zedbiz-asana-agent-control"
package_source="/tmp/${package_name}.tar.gz"
expected_skill_hash="${EXPECTED_SKILL_HASH:?EXPECTED_SKILL_HASH is required}"
backup_dir="/root/zedbiz-asana-mcp-backups/${agent}-$(date -u +%Y%m%dT%H%M%SZ)"
agent_vault="agent-${agent}"
asana_item="asana-api-key-${agent}"
email_item="email-address-${agent}"

for path in "$state_dir" "$openclaw_dir" "$openclaw_bin" "$openclaw_config" "$openclaw_env" "$workspace_skills" "$package_source" "$source_root/dist/index.js" "$verify_script"; do
  test -e "$path"
done
test -s "${state_dir}/.op.token"
systemctl is-active --quiet "openclaw-${agent}.service"
if ss -ltn "sport = :${port}" | tail -n +2 | grep -q .; then
  echo "Approved port ${port} is already in use" >&2
  exit 1
fi

install -d -m 0700 "$backup_dir"
cp "$openclaw_config" "$backup_dir/openclaw.json"
cp "$openclaw_env" "$backup_dir/.env"
if [ -d "${workspace_skills}/${package_name}" ]; then
  cp -a "${workspace_skills}/${package_name}" "$backup_dir/${package_name}"
fi

rollback() {
  result=$?
  set +e
  systemctl disable --now "$service_name" >/dev/null 2>&1 || true
  rm -f /etc/systemd/system/zedbiz-asana-mcp@.service
  rm -rf "${workspace_skills}/${package_name}"
  if [ -d "$backup_dir/${package_name}" ]; then
    cp -a "$backup_dir/${package_name}" "${workspace_skills}/${package_name}"
  fi
  cp "$backup_dir/openclaw.json" "$openclaw_config"
  cp "$backup_dir/.env" "$openclaw_env"
  systemctl daemon-reload
  systemctl restart "openclaw-${agent}.service" >/dev/null 2>&1 || true
  printf "Deployment rolled back for %s after failure.\n" "$agent" >&2
  exit "$result"
}
trap rollback ERR

export OP_SERVICE_ACCOUNT_TOKEN="$(tr -d '\r\n' < "${state_dir}/.op.token")"
op item get "$asana_item" --vault "$agent_vault" --format json >/dev/null
op item get "$email_item" --vault "$agent_vault" --format json >/dev/null
expected_email="$(op read "op://${agent_vault}/${email_item}/username")"
test -n "$expected_email"

# Keep credential references in the existing agent environment. The agent and
# its local sidecar both resolve them only at process startup via `op run`.
grep -v -E '^(ASANA_ACCESS_TOKEN|MCP_AUTH_TOKEN|MCP_ALLOWED_HOSTS|MCP_BIND_HOST|PORT|MCP_SESSION_TTL_MS|MCP_MAX_SESSIONS)=' "$openclaw_env" > "${openclaw_env}.new"
cat >> "${openclaw_env}.new" <<EOF
ASANA_ACCESS_TOKEN=op://${agent_vault}/${asana_item}/credential
MCP_AUTH_TOKEN=op://${agent_vault}/${asana_item}/credential
MCP_ALLOWED_HOSTS=localhost,127.0.0.1
MCP_BIND_HOST=127.0.0.1
PORT=${port}
MCP_SESSION_TTL_MS=900000
MCP_MAX_SESSIONS=16
EOF
chmod 0600 "${openclaw_env}.new"
mv "${openclaw_env}.new" "$openclaw_env"

cat > /etc/systemd/system/zedbiz-asana-mcp@.service <<'EOF'
[Unit]
Description=ZedBiz agent-specific Asana Streamable HTTP MCP (%i)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/zedbiz-asana-http-mcp
ExecStart=/bin/bash -lc 'export OP_SERVICE_ACCOUNT_TOKEN="$(tr -d "\r\n" < /root/.openclaw-%i/.op.token)"; exec /usr/bin/op run --env-file=/root/.openclaw-%i/.env -- /usr/bin/node /opt/zedbiz-asana-http-mcp/dist/index.js'
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=read-only
ReadWritePaths=/tmp

[Install]
WantedBy=multi-user.target
EOF
chmod 0644 /etc/systemd/system/zedbiz-asana-mcp@.service

jq \
  --arg url "http://127.0.0.1:${port}/mcp" \
  '.mcp = (.mcp // {})
   | .mcp.servers = (.mcp.servers // {})
   | .mcp.servers.asana = {
       url: $url,
       headers: {Authorization: "Bearer ${ASANA_ACCESS_TOKEN}"}
     }' \
  "$openclaw_config" > "${openclaw_config}.new"
chmod 0600 "${openclaw_config}.new"
mv "${openclaw_config}.new" "$openclaw_config"

rm -rf "${workspace_skills}/${legacy_name}" "${workspace_skills}/${legacy_name}".*
tar -xzf "$package_source" -C "$workspace_skills"
test -f "${workspace_skills}/${package_name}/SKILL.md"
test "$(sha256sum "${workspace_skills}/${package_name}/SKILL.md" | awk '{print $1}')" = "$expected_skill_hash"
if find "$workspace_skills" -mindepth 1 -maxdepth 1 -iname "${legacy_name}*" -print -quit | grep -q .; then
  echo "Retired Asana Skill directory remains in ${agent} workspace" >&2
  exit 1
fi

systemctl daemon-reload
systemctl enable --now "$service_name"
for _ in $(seq 1 30); do
  systemctl is-active --quiet "$service_name" && curl -fsS "http://127.0.0.1:${port}/healthz" >/dev/null && break
  sleep 2
done
systemctl is-active --quiet "$service_name"
curl -fsS "http://127.0.0.1:${port}/healthz" | jq -e '.ok == true' >/dev/null

# Resolve only for this short-lived, local read-only verification process.
export MCP_AUTH_TOKEN="$(op read "op://${agent_vault}/${asana_item}/credential")"
node "$verify_script" "$agent" "http://127.0.0.1:${port}/mcp" "$expected_email" "$workspace_gid" > "/tmp/zedbiz-asana-${agent}-preflight.json"
chmod 0600 "/tmp/zedbiz-asana-${agent}-preflight.json"

systemctl restart "openclaw-${agent}.service"
for _ in $(seq 1 30); do
  systemctl is-active --quiet "openclaw-${agent}.service" && break
  sleep 2
done
systemctl is-active --quiet "openclaw-${agent}.service"

HOME="$state_dir" OPENCLAW_STATE_DIR="$state_dir" OPENCLAW_CONFIG_PATH="$openclaw_config" "$openclaw_bin" mcp list 2>/dev/null | grep -q 'asana'
HOME="$state_dir" OPENCLAW_STATE_DIR="$state_dir" OPENCLAW_CONFIG_PATH="$openclaw_config" "$openclaw_bin" skills list 2>/dev/null | grep -q "$package_name"
! HOME="$state_dir" OPENCLAW_STATE_DIR="$state_dir" OPENCLAW_CONFIG_PATH="$openclaw_config" "$openclaw_bin" skills list 2>/dev/null | grep -q "$legacy_name"

jq --arg agent "$agent" --arg port "$port" --arg service "$service_name" \
  '. + {agent:$agent,port:($port|tonumber),service:$service,service_health:"active",openclaw_health:"active",skill:"z-asana-agent-control",legacy_skill:"absent"}' \
  "/tmp/zedbiz-asana-${agent}-preflight.json"
rm -f "$package_source" "/tmp/zedbiz-asana-${agent}-preflight.json"
rm -rf "$backup_dir"
trap - ERR
unset OP_SERVICE_ACCOUNT_TOKEN MCP_AUTH_TOKEN
