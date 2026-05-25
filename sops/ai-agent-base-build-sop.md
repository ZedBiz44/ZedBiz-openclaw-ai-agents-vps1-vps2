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
- **VPS-2 agents:** spaced ports 4100+ (Harry = 4100, Suzy = 4200, Edith = 4300, etc.)
## Critical Lines in systemd Service
`OPENCLAW_STATE_DIR` and `OPENCLAW_CONFIG_PATH` are the critical lines. If either is missing or wrong, OpenClaw falls back to the global `~/.openclaw` directory and creates a split-state mess. `OPENCLAW_HOME` must NOT be used.
---
## Phase 1.1 Goal
By the end of Phase 1.1, the agent is:
- Running on its own isolated OpenClaw install
- All data (workspace, memory, skills) in one clean directory
- Accessible in browser at `http://[VPS_IP]:[port]` and `https://[agent-name].zbiz.ca`
- Token generated and saved
- 1Password secrets injected on startup via wrapper script
- OpenAI API key configured via 1Password, default model GPT-4o, fallback GPT-5.2
- Ready for Phase 2 (skills, Asana, Notion)
---
## Step 1: Set Variables
```bash
export AGENT_ID="[agent-name-lowercase]"     # e.g. harry, edith, victor
export AGENT_NAME="[Agent Display Name]"     # e.g. Harry, Edith, Victor
export VPS_IP="2.24.104.80"

# Use fixed VPS-2 port assignments:
# Harry = 4100
# Suzy  = 4200
# Edith = 4300
# (next agent = 4400, etc.)
export AGENT_PORT=[assigned-fixed-port]      # e.g. 4100 for Harry

echo "Building $AGENT_NAME ($AGENT_ID) on port $AGENT_PORT at http://$VPS_IP:$AGENT_PORT"
```
---
## Step 2: Install Base Packages
```bash
apt update
apt install -y curl ca-certificates gnupg git build-essential openssl fail2ban
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
# Clean up any stale processes before install
systemctl stop openclaw-${AGENT_ID} 2>/dev/null || true
fuser -k ${AGENT_PORT}/tcp 2>/dev/null || true
ss -ltnp | grep ":${AGENT_PORT} " && echo "FAIL: port in use" && exit 1

cd /opt/openclaw-${AGENT_ID}
npm init -y
npm install openclaw@latest

# Assert
[ -f /opt/openclaw-${AGENT_ID}/node_modules/.bin/openclaw ] && echo "OK: binary exists" || echo "FAIL"
/opt/openclaw-${AGENT_ID}/node_modules/.bin/openclaw --version
```
---
## Step 6: Generate Token and Write Config
Note: `gateway.mode` is required. Omitting it will cause OpenClaw to refuse to start with a CONFIG error.
```bash
export NEW_TOKEN=$(openssl rand -hex 24)

cat > /root/.openclaw-${AGENT_ID}/openclaw.json << CONFIG_EOF
{
  "gateway": {
    "mode": "local",
    "port": ${AGENT_PORT},
    "bind": "lan",
    "auth": {
      "token": "${NEW_TOKEN}"
    },
    "controlUi": {
      "dangerouslyDisableDeviceAuth": true,
      "allowedOrigins": [
        "http://${VPS_IP}:${AGENT_PORT}",
        "http://localhost:${AGENT_PORT}",
        "https://${AGENT_ID}.zbiz.ca"
      ]
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/gpt-4o"
    }
  },
  "meta": {
    "lastTouchedVersion": "2026.5.19"
  }
}
CONFIG_EOF

echo $NEW_TOKEN > /root/.openclaw-${AGENT_ID}/token.txt
chmod 600 /root/.openclaw-${AGENT_ID}/token.txt
echo "Token: $NEW_TOKEN"

# Assert
[ -f /root/.openclaw-${AGENT_ID}/openclaw.json ] && echo "OK: config exists" || echo "FAIL"
grep '"mode": "local"' /root/.openclaw-${AGENT_ID}/openclaw.json && echo "OK: gateway.mode present" || echo "FAIL: gateway.mode missing"
grep '"model": "openai/gpt-4o"' /root/.openclaw-${AGENT_ID}/openclaw.json && echo "OK: default model set" || echo "FAIL: default model missing"
```
---
## Step 7: 1Password CLI Install
```bash
curl -sS https://downloads.1password.com/linux/keys/1password.asc | gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/$(dpkg --print-architecture) stable main" | tee /etc/apt/sources.list.d/1password.list
mkdir -p /etc/debsig/policies/AC2D62742012EA22/
curl -sS https://downloads.1password.com/linux/debian/debsig/1password.pol | tee /etc/debsig/policies/AC2D62742012EA22/1password.pol
mkdir -p /usr/share/debsig/keyrings/AC2D62742012EA22
curl -sS https://downloads.1password.com/linux/keys/1password.asc | gpg --dearmor --output /usr/share/debsig/keyrings/AC2D62742012EA22/debsig.gpg
apt update -qq && apt install -y 1password-cli

# Assert
op --version && echo "PASS: op CLI installed" || echo "FAIL"
```
For full 1Password CLI vault setup, see **Phase 1.2 1Password SOP**.
---
## Step 8: 1Password Secret Injection Wrapper
**PAUSE — human action required.** Jack must provide the 1Password Service Account token for this agent before continuing.

Once the token is received, save it and create the `.env` file:
```bash
# Replace [RECEIVED_TOKEN] with the actual token provided by Jack
echo "[RECEIVED_TOKEN]" > /root/.openclaw-${AGENT_ID}/.op.token
chmod 600 /root/.openclaw-${AGENT_ID}/.op.token

# Create the .env file with 1Password secret references
# All items live in the openclaw-agents-shared vault
# Field name is: credential
cat > /root/.openclaw-${AGENT_ID}/.env << ENV_EOF
OPENAI_API_KEY=op://openclaw-agents-shared/openai-api-key/credential
OPENROUTER_API_KEY=op://openclaw-agents-shared/openrouter-api-key/credential
NOTION_API_KEY=op://openclaw-agents-shared/notion-api-key/credential
ENV_EOF
chmod 600 /root/.openclaw-${AGENT_ID}/.env

# Assert
[ -s "/root/.openclaw-${AGENT_ID}/.op.token" ] || exit 1
[ -f "/root/.openclaw-${AGENT_ID}/.env" ] || exit 1
op run --env-file=/root/.openclaw-${AGENT_ID}/.env -- printenv OPENAI_API_KEY >/dev/null || exit 1
echo "PASS: 1Password secrets resolving correctly"
```

Create the 1Password wrapper script:
```bash
cat > /opt/openclaw-${AGENT_ID}/start-${AGENT_ID}.sh << SCRIPT_EOF
#!/usr/bin/env bash
set -euo pipefail

export OP_SERVICE_ACCOUNT_TOKEN="$(cat /root/.openclaw-${AGENT_ID}/.op.token)"
export HOME="/root/.openclaw-${AGENT_ID}"
export OPENCLAW_STATE_DIR="/root/.openclaw-${AGENT_ID}"
export OPENCLAW_CONFIG_PATH="/root/.openclaw-${AGENT_ID}/openclaw.json"

exec op run \
  --env-file=/root/.openclaw-${AGENT_ID}/.env \
  -- /opt/openclaw-${AGENT_ID}/node_modules/.bin/openclaw gateway run \
    --bind lan \
    --port ${AGENT_PORT}
SCRIPT_EOF

chmod 700 /opt/openclaw-${AGENT_ID}/start-${AGENT_ID}.sh

# Assert
[ -x "/opt/openclaw-${AGENT_ID}/start-${AGENT_ID}.sh" ] && echo "PASS: wrapper executable" || echo "FAIL"
```
---
## Step 9: Create systemd Service File
```bash
cat > /etc/systemd/system/openclaw-${AGENT_ID}.service << SERVICE_EOF
[Unit]
Description=OpenClaw Gateway (${AGENT_NAME})
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/openclaw-${AGENT_ID}
Environment=HOME=/root/.openclaw-${AGENT_ID}
Environment=OPENCLAW_STATE_DIR=/root/.openclaw-${AGENT_ID}
Environment=OPENCLAW_CONFIG_PATH=/root/.openclaw-${AGENT_ID}/openclaw.json
Environment=OPENCLAW_GATEWAY_PORT=${AGENT_PORT}
ExecStart=/opt/openclaw-${AGENT_ID}/start-${AGENT_ID}.sh
Restart=always
RestartSec=5
MemoryMax=1.5G

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Assert critical env vars present
grep OPENCLAW_STATE_DIR /etc/systemd/system/openclaw-${AGENT_ID}.service && echo "OK: OPENCLAW_STATE_DIR present" || echo "FAIL"
grep OPENCLAW_CONFIG_PATH /etc/systemd/system/openclaw-${AGENT_ID}.service && echo "OK: OPENCLAW_CONFIG_PATH present" || echo "FAIL"
```
---
## Step 10: Enable and Start Service
```bash
systemctl daemon-reload
systemctl enable openclaw-${AGENT_ID}
systemctl start openclaw-${AGENT_ID}
sleep 10
systemctl status openclaw-${AGENT_ID} --no-pager | head -10

# Assert
systemctl is-active openclaw-${AGENT_ID} && echo "OK: service active" || echo "FAIL: service not active"
```
If the service fails, check logs:
```bash
journalctl -u openclaw-${AGENT_ID} -n 20 --no-pager
```
---
## Step 11: Verify State Directory Layout
```bash
ls /root/.openclaw-${AGENT_ID}/

# Verify workspace is NOT in the wrong place
[ -d /root/.openclaw-${AGENT_ID}/workspace ] || echo "FAIL: workspace missing"
[ ! -d /root/.openclaw/workspace ] || echo "FAIL: using global workspace"
```
---
## Step 12: Configure OpenAI Models
The OpenAI API key is injected via 1Password. Verify it is available:
```bash
grep -q "OPENAI_API_KEY" /root/.openclaw-${AGENT_ID}/.env && echo "PASS: Key defined in .env" || echo "FAIL: Key missing from .env"
```
In the OpenClaw browser UI (`http://[VPS_IP]:[port]`):
- Go to **Settings > Models**
- Add OpenAI as a provider (key auto-detected from environment)
- Set **default model** to `gpt-4o`
- Set **fallback model** to `gpt-5.2`
- Test that both models respond

For detailed model configuration, see **Phase 1.4 LLM Model Picker SOP**.
---
## Step 13: Browser First-Run Setup
- Open `http://[VPS_IP]:[port]` in your browser
- Enter the Gateway Token saved in Step 6
- Click Connect
- Complete the first-run setup wizard

After connecting, wait 15-20 seconds then verify state directories were created:
```bash
ls /root/.openclaw-${AGENT_ID}/
# Expected: agents/ canvas/ flows/ identity/ logs/ memory/ plugin-runtime-deps/ plugin-skills/ tasks/ workspace/
```
---
## Step 14: Fail2Ban Security Setup
VPS-2 uses Fail2Ban + the Hostinger firewall panel instead of UFW. UFW is disabled.
```bash
# Verify Fail2Ban is running
systemctl status fail2ban --no-pager | head -5
systemctl is-active fail2ban && echo "PASS: fail2ban active" || echo "NOTE: fail2ban not active — start it"

# Start and enable if not running
systemctl enable fail2ban
systemctl start fail2ban

# Confirm SSH jail is active
fail2ban-client status sshd 2>/dev/null || fail2ban-client status
```
Port access for agents is managed via the Hostinger firewall panel (not UFW). Ensure port 80 and 443 are open in Hostinger for Caddy, and agent ports (4000+) are restricted to internal access only after Caddy is configured.
---
## Step 15: Add Caddy Route
Ensure the DNS A record for `${AGENT_ID}.zbiz.ca` is already pointing to `2.24.104.80` before this step.
```bash
cat >> /opt/caddy/Caddyfile << EOF

${AGENT_ID}.zbiz.ca {
    reverse_proxy localhost:${AGENT_PORT}
}
EOF

systemctl reload caddy
sleep 10

# Assert
if curl -sI https://${AGENT_ID}.zbiz.ca | grep -q "HTTP/2 200\|200 OK"; then echo "PASS: HTTPS routing active"; else echo "FAIL: check DNS propagation and Caddy logs"; fi
```
For full Caddy install and configuration, see **Phase 1.3 Caddy Routing SOP**.
---
## Phase 1.1 Done When
- Service is `Active: active (running)` in systemd
- HTTPS routing active at `https://[agent-name].zbiz.ca`
- All state directories exist under `/root/.openclaw-[agent-name]/` including `workspace/` and `memory/`
- No global fallback workspace exists at `/root/.openclaw/workspace`
- No agent memory or workspace data exists under `/root/.openclaw/` unless intentionally documented
- Token is saved to `/root/.openclaw-[agent-name]/token.txt`
- Memory limit is 1.5G
- 1Password secrets injected on startup via wrapper script
- OpenAI API key configured via 1Password
- Default model: GPT-4o, Fallback: GPT-5.2
- Fail2Ban active, Hostinger firewall managing port access
---
## Phase 1 — All Phases
- **Phase 1.2** — 1Password Secrets Setup
- **Phase 1.3** — Caddy Routing Setup (custom domain + HTTPS)
- **Phase 1.4** — OpenClaw LLM Model Picker Configuration
---
## Phase 2 — After All Phase 1 Steps Are Complete
- Install core skills + agent-specific skills
- Asana MCP setup
- Notion setup
