# Human Agent Base Build SOP — VPS-2 Native Install (Phase 1.1)
## Overview
This SOP is the **human-executable version** of the VPS-2 OpenClaw setup process. It walks you or Cody through setting up a new OpenClaw agent on VPS-2 step by step.
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
`OPENCLAW_STATE_DIR` and `OPENCLAW_CONFIG_PATH` are the two critical lines. If either is missing or wrong, OpenClaw silently falls back to the global `~/.openclaw` directory and creates a split-state mess.

**Important:** Do NOT use `OPENCLAW_HOME`. OpenClaw may append `.openclaw` under it, accidentally creating `/root/.openclaw-harry/.openclaw/`.
---
## Phase 1.1 Goal
By the end of Phase 1.1, the agent is:
- Running on its own isolated OpenClaw install
- All data (workspace, memory, skills) in one clean directory
- Accessible in your browser at `http://[VPS_IP]:[port]` and `https://[agent-name].zbiz.ca`
- Token generated and saved
- 1Password secrets injected on startup via wrapper script
- OpenAI API key configured via 1Password, default model GPT-4o, fallback GPT-5.2
- Ready for Phase 2 (skills, Asana, Notion)
---
## Step 1: Set Your Variables
SSH into the VPS, then set these variables. Replace the values in brackets.
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
apt install -y curl ca-certificates gnupg git build-essential openssl fail2ban
```
---
## Step 3: Verify Node.js 24
```bash
node --version
```
You should see `v24.x.x`. If you see anything lower, run:
```bash
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
apt-get install -y nodejs
node --version
```
Confirm it shows `v24.x.x` before continuing.
---
## Step 4: Create Directories
```bash
mkdir -p /opt/openclaw-${AGENT_ID}
mkdir -p /root/.openclaw-${AGENT_ID}
ls /opt/ | grep openclaw
ls /root/ | grep openclaw
```
You should see both new directories listed.
---
## Step 5: Install OpenClaw Into the Agent's Own Directory
```bash
cd /opt/openclaw-${AGENT_ID}
npm init -y
npm install openclaw@latest
```
This takes 1-2 minutes. When done, verify:
```bash
ls /opt/openclaw-${AGENT_ID}/node_modules/.bin/openclaw
/opt/openclaw-${AGENT_ID}/node_modules/.bin/openclaw --version
```
You should see the OpenClaw version number.
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
chmod 600 /root/.openclaw-${AGENT_ID}/token.txt
echo "Token: $NEW_TOKEN"
```
Copy the token — you will need it to connect in the browser. Verify:
```bash
grep '"mode": "local"' /root/.openclaw-${AGENT_ID}/openclaw.json && echo "OK: gateway.mode present" || echo "FAIL: gateway.mode missing"
```
---
## Step 7: Install 1Password CLI
```bash
curl -sS https://downloads.1password.com/linux/keys/1password.asc | gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/$(dpkg --print-architecture) stable main" | tee /etc/apt/sources.list.d/1password.list
mkdir -p /etc/debsig/policies/AC2D62742012EA22/
curl -sS https://downloads.1password.com/linux/debian/debsig/1password.pol | tee /etc/debsig/policies/AC2D62742012EA22/1password.pol
mkdir -p /usr/share/debsig/keyrings/AC2D62742012EA22
curl -sS https://downloads.1password.com/linux/keys/1password.asc | gpg --dearmor --output /usr/share/debsig/keyrings/AC2D62742012EA22/debsig.gpg
apt update -qq && apt install -y 1password-cli
op --version
```
You should see the op CLI version number.
---
## Step 8: 1Password Secret Injection Wrapper
**STOP — you need to provide the 1Password Service Account token for this agent before continuing.**

Once you have the token, save it to the VPS and create the `.env` file:
```bash
# Replace [RECEIVED_TOKEN] with the actual token
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
[ -f "/root/.openclaw-${AGENT_ID}/.op.token" ] && echo "PASS: Token saved" || echo "FAIL: Token missing"
[ -f "/root/.openclaw-${AGENT_ID}/.env" ] && echo "PASS: .env saved" || echo "FAIL: .env missing"
```

Create the 1Password wrapper script:
```bash
cat > /opt/openclaw-${AGENT_ID}/start-${AGENT_ID}.sh << SCRIPT_EOF
#!/usr/bin/env bash
set -euo pipefail

export OP_SERVICE_ACCOUNT_TOKEN="$(cat /root/.openclaw-${AGENT_ID}/.op.token)"

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
For full 1Password vault setup, see **Phase 1.2 1Password SOP**.
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
Environment=HOME=/root
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
```
Verify the critical lines are present:
```bash
grep OPENCLAW_STATE_DIR /etc/systemd/system/openclaw-${AGENT_ID}.service
grep OPENCLAW_CONFIG_PATH /etc/systemd/system/openclaw-${AGENT_ID}.service
```
Both lines must appear. If either is missing, edit the file and add them before continuing.
---
## Step 10: Enable and Start the Service
```bash
systemctl daemon-reload
systemctl enable openclaw-${AGENT_ID}
systemctl start openclaw-${AGENT_ID}
sleep 10
systemctl status openclaw-${AGENT_ID}
```
You should see `Active: active (running)`. If it shows failed, check logs:
```bash
journalctl -u openclaw-${AGENT_ID} -n 30
```
---
## Step 11: Verify State Directory Layout
```bash
ls /root/.openclaw-${AGENT_ID}/
```
You should see `openclaw.json` and `token.txt` at minimum.

Also verify workspace is NOT in the wrong place:
```bash
ls /root/.openclaw/ 2>/dev/null | grep workspace-${AGENT_ID}
```
This must return nothing. If it returns `workspace-[agent-name]`, the `OPENCLAW_STATE_DIR` env var is not working — stop and fix the service file before continuing.
---
## Step 12: Configure OpenAI Models
Do this before the browser first-run so the model is set correctly when you connect.

Verify the API key is defined in `.env`:
```bash
grep -q "OPENAI_API_KEY" /root/.openclaw-${AGENT_ID}/.env && echo "PASS: Key defined in .env" || echo "FAIL: Key missing from .env"
```
In the OpenClaw browser UI (`http://[VPS_IP]:[port]`):
- Go to **Settings > Models**
- Add OpenAI as a provider (key auto-detected from environment)
- Set **default model** to `gpt-4o`
- Set **fallback model** to `gpt-5.2`
- Test that both models respond

For detailed step-by-step model configuration, see **Phase 1.4 LLM Model Picker SOP**.
---
## Step 13: Connect in Browser and Complete First-Run Setup
- Open `http://[VPS_IP]:[port]` in your browser
- Enter the Gateway Token you saved in Step 6
- Click Connect
- Complete the first-run setup wizard

This step generates the remaining state directories (workspace, memory, canvas, flows, etc.). After connecting, wait 15-20 seconds then run the Step 11 verification again to confirm all folders landed in the right place.
---
## Step 14: Fail2Ban Security Setup
VPS-2 uses Fail2Ban + the Hostinger firewall panel instead of UFW. UFW is disabled.
```bash
# Verify Fail2Ban is running
systemctl status fail2ban --no-pager | head -5
systemctl is-active fail2ban && echo "PASS: fail2ban active" || echo "NOTE: fail2ban not active"

# Start and enable if not running
systemctl enable fail2ban
systemctl start fail2ban

# Confirm SSH jail is active
fail2ban-client status sshd 2>/dev/null || fail2ban-client status
```
Port access for agents is managed via the Hostinger firewall panel. Ensure ports 80 and 443 are open for Caddy. Agent ports (4000+) should be restricted to internal access only once Caddy is configured.
---
## Step 15: Add Caddy Route
Before running this step, confirm the DNS A record for `${AGENT_ID}.zbiz.ca` is already pointing to `2.24.104.80`. If DNS is not set up yet, do that first and wait for propagation.
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
- Agent service is `Active: active (running)` in systemd
- HTTPS routing active at `https://[agent-name].zbiz.ca`
- All state directories exist under `/root/.openclaw-[agent-name]/` including `workspace/` and `memory/`
- No workspace or memory files exist under `/root/.openclaw/workspace-[agent-name]`
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
