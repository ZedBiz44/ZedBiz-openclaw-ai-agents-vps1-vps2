#!/bin/bash
set -euo pipefail
umask 077
B=/root/cody-harry-maintenance-20261003
old="$B/asana-service-before"
test ! -e "$old"
cp -a "$B/asana-candidate" /opt/zedbiz-asana-http-mcp.next-20261003
cp /opt/zedbiz-asana-http-mcp/verify-vps2-agent.mjs /opt/zedbiz-asana-http-mcp.next-20261003/
mv /opt/zedbiz-asana-http-mcp "$old"
mv /opt/zedbiz-asana-http-mcp.next-20261003 /opt/zedbiz-asana-http-mcp
rollback() {
 trap - ERR
 mv /opt/zedbiz-asana-http-mcp "$B/asana-service-failed"
 mv "$old" /opt/zedbiz-asana-http-mcp
 systemctl restart zedbiz-asana-mcp@suzy zedbiz-asana-mcp@harry zedbiz-asana-mcp@frank
 exit 1
}
trap rollback ERR
for spec in suzy:4210 harry:4110 frank:4310; do
 agent="${spec%:*}"; port="${spec#*:}"
 systemctl restart "zedbiz-asana-mcp@$agent"
 for i in $(seq 1 20); do curl -sf "http://127.0.0.1:$port/healthz" >/dev/null && break; sleep 1; done
 export OP_SERVICE_ACCOUNT_TOKEN="$(cat /root/.openclaw-$agent/.op.token)"
 expected="$(op read op://agent-$agent/email-address-$agent/credential)"
 op run --env-file="/root/.openclaw-$agent/.env" -- node /opt/zedbiz-asana-http-mcp/verify-vps2-agent.mjs "$agent" "http://127.0.0.1:$port/mcp" "$expected"
done
printf 'ASANA_ALL_THREE_VERIFIED\n'