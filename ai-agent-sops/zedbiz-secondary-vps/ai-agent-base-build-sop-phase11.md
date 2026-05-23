# AI Agent Base Build SOP — VPS-2 Native Install (Phase 1.1)
## Overview
This SOP is the **agent-executable version** of the VPS-2 OpenClaw setup process. It is designed to be run by Manus or another AI agent via SSH on VPS-2.
## Method: Per-Agent npm Install + systemd (No Docker, No Global Install)
Each agent on VPS-2 gets its own isolated OpenClaw program install under `/opt/openclaw-[agent-name]/` and its own data directory under `/root/.openclaw-[agent-name]/`. The systemd service sets `OPENCLAW_STATE_DIR` and `OPENCLAW_CONFIG_PATH` to point to the correct data directory.
## Directory Structure (Per Agent)
```javascript
/opt/openclaw-[agent-name]/          <- Agent's own OpenClaw program install
/root/.openclaw-[agent-name]/        <- ALL agent data
    agents/
    canvas/
    flows/
    identity/
    logs/
    memory/
    plugin-runtime-deps/
    plugin-skills/
    tasks/
    workspace/
    openclaw.json
```
## Why This Method
- **True isolation** — each agent has its own program binary and data directory
- **No cross-contamination** — memory, workspace, and skills never bleed between agents
- **Per-agent updates** — update one agent at a time, test before rolling to others
- **Predictable paths** — every tool, skill, and MCP knows exactly where to find agent files
- **Scales cleanly** — adding agent 3 is identical to adding agent 1
## Port Convention
- **VPS-1 agents:** ports 3000+
- **VPS-2 agents:** ports 4000+ (Harry = 4000, Edith = 4001, next = 4002, etc.)
## Critical Lines in systemd Service
`OPENCLAW_STATE_DIR` and `OPENCLAW_CONFIG_PATH` are the critical lines. If either is missing or wrong, OpenClaw falls back to the global `~/.openclaw` directory and creates a split-state mess. `OPENCLAW_HOME` must NOT be used — OpenClaw may append `.openclaw` under it, creating `/root/.openclaw-harry/.openclaw/`.
---
## Phase 1.1 Goal
By the end of Phase 1.1, the agent is:
- Running on its own isolated OpenClaw install
- All data (workspace, memory, skills) in one clean directory
- Accessible in browser at `http://[VPS_IP]:[port]`
- Token generated and saved
- Caddy routing active at `https://[agent-name].zbiz.ca`
- 1Password secrets injected on startup
- OpenAI API key configured, default model GPT-4o, fallback GPT-4.5
- Ready for Phase 2 (skills, Asana, Notion)
---
## Step 1: Set Variables
```bash
export AGENT_ID="[agent-name-lowercase]"     # e.g. harry, edith, victor
export AGENT_NAME="[Agent Display Name]"     # e.g. Harry, Edith, Victor
export VPS_IP="2.24.104.80"

# Find the next available port (VPS-2 uses 4000+)
ss -tlnp | grep 40

# Set the port manually based on what is free
export AGENT_PORT=[next-available-port]      # e.g. 4002 for the third agent

echo "Building $AGENT_NAME ($AGENT_ID) on port $AGENT_PORT at http://$VPS_IP:$AGENT_PORT"
```
---
## Step 2: Install Base Packages
```bash
apt update
apt install -y curl ca-certificates gnupg git build-essential openssl ufw
```
---
## Step 3: Verify Node.js 24
```bash
node --version
```
Must return `v24.x.x`. If not:
```bash
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
apt-get install -y nodejs
node --version
```
Assert: version starts with `v24`.
---
## Step 4: Create Directories
```bash
mkdir -p /opt/openclaw-${AGENT_ID}
mkdir -p /root/.openclaw-${AGENT_ID}

# Assert
[ -d /opt/openclaw-${AGENT_ID} ] && echo "OK: /opt/openclaw-${AGENT_ID} exists" || echo "FAIL"
[ -d /root/.openclaw-${AGENT_ID} ] && echo "OK: /root/.openclaw-${AGENT_ID} exists" || echo "FAIL"
```
---
## Step 5: Install OpenClaw Into Agent's Own Directory
```bash
cd /opt/openclaw-${AGENT_ID}
npm init -y
npm install openclaw@latest

# Assert
[ -f /opt/openclaw-${AGENT_ID}/node_modules/.bin/openclaw ] && echo "OK: binary exists" || echo "FAIL"
/opt/openclaw-${AGENT_ID}/node_modules/.bin/openclaw --version
```
---
## Step 6: Generate Token and Write Config
```bash
export NEW_TOKEN=$(openssl rand -hex 24)

cat > /root/.openclaw-${AGENT_ID}/openclaw.json << CONFIG_EOF
{
  "gateway": {
    "port": ${AGENT_PORT},
    "bind": "lan",
    "auth": {
      "token": "${NEW_TOKEN}"
    },
    "controlUi": {
      "dangerouslyDisableDeviceAuth": true,
      "allowedOrigins": [
        "http://${VPS_IP}:${AGENT_PORT}",
        "http://localhost:${AGENT_PORT}"
      ]
    }
  },
  "meta": {
    "lastTouchedVersion": "2026.5.19"
  }
}
CONFIG_EOF

echo $NEW_TOKEN > /root/.openclaw-${AGENT_ID}/token.txt
echo "Token: $NEW_TOKEN"

# Assert
[ -f /root/.openclaw-${AGENT_ID}/openclaw.json ] && echo "OK: config exists" || echo "FAIL"
```
---
## Step 7: Create systemd Service File
```bash
cat > /etc/systemd/system/openclaw-${AGENT_ID}.service << SERVICE_EOF
[Unit]
Description=OpenClaw Gateway (${AGENT_NAME})
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/openclaw-${AGENT_ID}
Environment=HOME=/root
Environment=OPENCLAW_STATE_DIR=/root/.openclaw-${AGENT_ID}
Environment=OPENCLAW_CONFIG_PATH=/root/.openclaw-${AGENT_ID}/openclaw.json
Environment=OPENCLAW_GATEWAY_PORT=${AGENT_PORT}
ExecStart=/opt/openclaw-${AGENT_ID}/node_modules/.bin/openclaw gateway run --bind lan --port ${AGENT_PORT}
Restart=always
RestartSec=5
MemoryMax=1.5G

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Assert OPENCLAW_STATE_DIR is present
grep OPENCLAW_STATE_DIR /etc/systemd/system/openclaw-${AGENT_ID}.service && echo "OK: OPENCLAW_STATE_DIR present" || echo "FAIL: missing critical env var"
grep OPENCLAW_CONFIG_PATH /etc/systemd/system/openclaw-${AGENT_ID}.service && echo "OK: OPENCLAW_CONFIG_PATH present" || echo "FAIL: missing critical env var"
```
---
## Step 8: Add Caddy Route
Ensure the DNS A record for `${AGENT_ID}.zbiz.ca` is already pointing to `2.24.104.80` before this step. Then append the new agent route to the Caddyfile and reload Caddy.
```bash
cat >> /opt/caddy/Caddyfile << EOF

${AGENT_ID}.zbiz.ca {
    reverse_proxy localhost:${AGENT_PORT}
}
EOF

systemctl reload caddy

# Wait for Caddy to provision SSL
sleep 10

# Assert
if curl -sI https://${AGENT_ID}.zbiz.ca | grep -q "HTTP/2 200\|200 OK"; then echo "PASS: HTTPS routing active"; else echo "FAIL: HTTPS routing failed — check DNS propagation and Caddy logs"; fi
```
For full Caddy install and configuration, see **Phase 1.3 Caddy Routing SOP**.
---
## Step 9: 1Password Secret Injection
**PAUSE — human action required.** Jack must provide the 1Password Service Account token for this agent before continuing. Do not proceed until the token is received.

Once the token is received, save it and restart the service with secrets injected:
```bash
# Replace [RECEIVED_TOKEN] with the actual token provided by Jack
echo "[RECEIVED_TOKEN]" > /root/.openclaw-${AGENT_ID}/.op.token
chmod 600 /root/.openclaw-${AGENT_ID}/.op.token

# Assert
[ -f "/root/.openclaw-${AGENT_ID}/.op.token" ] && echo "PASS: Token saved" || echo "FAIL: Token missing"
```
Restart the service with 1Password secret injection:
```bash
systemctl stop openclaw-${AGENT_ID}

OP_SERVICE_ACCOUNT_TOKEN=$(cat /root/.openclaw-${AGENT_ID}/.op.token) \
  op run --env-file=/root/.openclaw-${AGENT_ID}/.env -- \
  systemctl start openclaw-${AGENT_ID}

sleep 10

# Assert secrets injected
systemctl is-active openclaw-${AGENT_ID} && echo "OK: service active with secrets" || echo "FAIL: service not active"
```
For full 1Password CLI install and vault setup, see **Phase 1.2 1Password SOP**.
---
## Step 10: Configure OpenAI API Key and Models
The OpenAI API key is injected via the `.env` file used by 1Password in Step 9. Verify it is present in the running service environment:
```bash
# Assert API key is available to the service
systemctl show openclaw-${AGENT_ID} --property=Environment | grep -q "OPENAI_API_KEY" && echo "PASS: API key present" || echo "NOTE: Key may be injected at runtime via op run — verify in browser"
```
In the OpenClaw browser UI:
- Go to **Settings > Models**
- Add OpenAI as a provider
- Set **default model** to `gpt-4o`
- Set **fallback model** to `gpt-4.5-preview`
- Test that both models respond

For detailed step-by-step model configuration, see **Phase 1.4 LLM Model Picker SOP**.
---
## Step 11: Enable and Start Service
```bash
systemctl daemon-reload
systemctl enable openclaw-${AGENT_ID}
systemctl start openclaw-${AGENT_ID}
sleep 10
systemctl status openclaw-${AGENT_ID} --no-pager | head -5

# Assert
systemctl is-active openclaw-${AGENT_ID} && echo "OK: service active" || echo "FAIL: service not active"
```
---
## Step 12: Open Firewall Port
```bash
ufw allow ${AGENT_PORT}/tcp
ufw reload
ufw status | grep ${AGENT_PORT}

# Assert HTTP response
curl -s -o /dev/null -w "%{http_code}" http://localhost:${AGENT_PORT}/ | grep -q "200\|301\|302" && echo "OK: port responding" || echo "FAIL: port not responding"
```
---
## Step 13: Verify State Directory Layout
After the service starts, verify all state writes are landing in the correct location:
```bash
# Check state dir exists and is populated
ls /root/.openclaw-${AGENT_ID}/

# Critical: verify workspace is NOT in the wrong place
ls /root/.openclaw/ 2>/dev/null | grep workspace-${AGENT_ID} && echo "FAIL: workspace in wrong location" || echo "OK: workspace not split"

# After first browser connect, check all folders are created
# Expected: agents/ canvas/ flows/ identity/ logs/ memory/ plugin-runtime-deps/ plugin-skills/ tasks/ workspace/
```
Note: Some folders (canvas, flows, memory, workspace) are created by OpenClaw during first browser initialization. The service environment must first prove all state writes land under `/root/.openclaw-[agent]/` before trusting the layout is correct.
---
## Phase 1.1 Done When
- Service is `Active: active (running)` in systemd
- Browser connects at `http://[VPS_IP]:[port]`
- HTTPS routing active at `https://[agent-name].zbiz.ca`
- All state directories exist under `/root/.openclaw-[agent-name]/` including `workspace/` and `memory/`
- No workspace or memory files exist under `/root/.openclaw/workspace-[agent-name]`
- Token is saved to `/root/.openclaw-[agent-name]/token.txt`
- Memory limit is 1.5G
- 1Password secrets injected on startup
- OpenAI API key configured in browser
- Default model: GPT-4o, Fallback: GPT-4.5
---
## Phase 1 — All Phases
Phase 1.1 (this page) is complete. Continue with:
- **Phase 1.2** — 1Password Secrets Setup
- **Phase 1.3** — Caddy Routing Setup (custom domain + HTTPS)
- **Phase 1.4** — OpenClaw LLM Model Picker Configuration
---
## Phase 2 — After All Phase 1 Steps Are Complete
- Install core skills + agent-specific skills
- Asana MCP setup
- Notion setup
