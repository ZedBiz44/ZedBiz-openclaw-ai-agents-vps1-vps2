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
    workspace/                       <- Explicitly set via agents.defaults.workspace
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
`OPENCLAW_STATE_DIR` and `OPENCLAW_CONFIG_PATH` are the two critical lines. If either is missing or wrong, OpenClaw silently falls back to the global `~/.openclaw` directory and creates a split-state mess.

**Important:** Do NOT use `OPENCLAW_HOME`. OpenClaw may append `.openclaw` under it, accidentally creating `/root/.openclaw-harry/.openclaw/`.

**Workspace path warning:** Do NOT rely on `HOME` or `OPENCLAW_STATE_DIR` to control the workspace location. OpenClaw defaults to `~/.openclaw/workspace` regardless of those vars. The workspace path MUST be set explicitly via `agents.defaults.workspace` in `openclaw.json` AND via `openclaw setup --workspace`. If either is missing, OpenClaw will create a nested workspace under `$HOME/.openclaw/workspace` instead of the expected path. This is the bug that broke Harry the first time.
---
## Phase 1.1 Goal
By the end of Phase 1.1, the agent is:
- Running on its own isolated OpenClaw install
- All data (workspace, memory, skills) in one clean directory
- Accessible in your browser at `http://[VPS_IP]:[port]` and `https://[agent-name].zbiz.ca`
- Token generated and saved
- 1Password secrets injected on startup via wrapper script
- OpenAI API key configured via 1Password, default model GPT-4o, fallback GPT-5.2
- Instruction files (`IDENTITY.md`, `USER.md`, `SOUL.md`, `AGENTS.md`) pre-seeded before first launch
- Ready for Phase 2 (skills, Asana, Notion)
---
## Step 1: Set Your Variables
SSH into the VPS, then set these variables. Replace the values in brackets.
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
apt install -y curl ca-certificates gnupg git build-essential openssl fail2ban psmisc
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
First, clean up stale processes for THIS agent only:
```bash
# Do NOT use systemctl stop openclaw-* or pkill -f openclaw — that would kill other running agents
systemctl stop openclaw-${AGENT_ID} 2>/dev/null || true
fuser -k ${AGENT_PORT}/tcp 2>/dev/null || true
ss -ltnp | grep ":${AGENT_PORT} " && echo "FAIL: port in use" && exit 1
```
Then install:
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

**Critical:** The `agents.defaults.workspace` field MUST be set explicitly in the config. Without it, OpenClaw defaults to `~/.openclaw/workspace` which resolves to a nested path under HOME. This is the bug that broke Harry the first time — do not skip this field.
```bash
export NEW_TOKEN=$(openssl rand -hex 24)

cat > /root/.openclaw-${AGENT_ID}/openclaw.json << 'CONFIG_EOF'
{
  "gateway": {
    "mode": "local",
    "port": AGENT_PORT_PLACEHOLDER,
    "bind": "lan",
    "auth": {
      "token": "NEW_TOKEN_PLACEHOLDER"
    },
    "controlUi": {
      "dangerouslyDisableDeviceAuth": true,
      "allowedOrigins": [
        "http://VPS_IP_PLACEHOLDER:AGENT_PORT_PLACEHOLDER",
        "http://localhost:AGENT_PORT_PLACEHOLDER",
        "https://AGENT_ID_PLACEHOLDER.zbiz.ca"
      ]
    }
  },
  "agents": {
    "defaults": {
      "model": "openai/gpt-4o",
      "workspace": "/root/.openclaw-AGENT_ID_PLACEHOLDER/workspace"
    }
  },
  "meta": {
    "lastTouchedVersion": "2026.5.22"
  }
}
CONFIG_EOF

# Substitute actual values into the config
sed -i "s/AGENT_PORT_PLACEHOLDER/${AGENT_PORT}/g" /root/.openclaw-${AGENT_ID}/openclaw.json
sed -i "s/NEW_TOKEN_PLACEHOLDER/${NEW_TOKEN}/g" /root/.openclaw-${AGENT_ID}/openclaw.json
sed -i "s/VPS_IP_PLACEHOLDER/${VPS_IP}/g" /root/.openclaw-${AGENT_ID}/openclaw.json
sed -i "s/AGENT_ID_PLACEHOLDER/${AGENT_ID}/g" /root/.openclaw-${AGENT_ID}/openclaw.json

echo $NEW_TOKEN > /root/.openclaw-${AGENT_ID}/token.txt
chmod 600 /root/.openclaw-${AGENT_ID}/token.txt
echo "Token: $NEW_TOKEN"
```
Copy the token — you will need it to connect in the browser. Verify:
```bash
grep '"mode": "local"' /root/.openclaw-${AGENT_ID}/openclaw.json && echo "OK: gateway.mode present" || echo "FAIL: gateway.mode missing"
grep '"model": "openai/gpt-4o"' /root/.openclaw-${AGENT_ID}/openclaw.json && echo "OK: default model set" || echo "FAIL: default model missing"
grep '"workspace"' /root/.openclaw-${AGENT_ID}/openclaw.json && echo "OK: workspace path set in config" || echo "FAIL: workspace path missing — add it before continuing"
grep "/root/.openclaw-${AGENT_ID}/workspace" /root/.openclaw-${AGENT_ID}/openclaw.json && echo "OK: workspace path is correct" || echo "FAIL: workspace path is wrong"
```
All four checks must pass before continuing.
---
## Step 6b: Initialize Workspace
Run `openclaw setup` with the explicit workspace path. This creates the workspace directory and confirms the path is registered in the config.
```bash
mkdir -p /root/.openclaw-${AGENT_ID}/workspace

HOME=/root/.openclaw-${AGENT_ID} \
OPENCLAW_STATE_DIR=/root/.openclaw-${AGENT_ID} \
OPENCLAW_CONFIG_PATH=/root/.openclaw-${AGENT_ID}/openclaw.json \
/opt/openclaw-${AGENT_ID}/node_modules/.bin/openclaw setup \
  --workspace /root/.openclaw-${AGENT_ID}/workspace \
  --non-interactive
```
Then verify three things:
```bash
# 1. Correct workspace must exist
[ -d /root/.openclaw-${AGENT_ID}/workspace ] && echo "OK: workspace exists" || echo "FAIL: workspace not created"

# 2. Nested workspace must NOT exist
[ ! -d /root/.openclaw-${AGENT_ID}/.openclaw/workspace ] && echo "OK: no nested workspace" || echo "FAIL: nested workspace found — stop and investigate"

# 3. Global fallback must NOT exist
[ ! -d /root/.openclaw/workspace ] && echo "OK: no global fallback" || echo "FAIL: global fallback found — stop and investigate"
```
If check 2 or 3 fails, stop. The workspace config is wrong. Do not continue until both pass.
---
## Step 6c: Pre-Seed Workspace Files
Do NOT rely on the agent to write its own identity from chat. Pre-seed all four workspace files before first launch. These are Harry-specific — update content for each new agent.

**For Harry:**
```bash
# IDENTITY.md — who Harry is
mkdir -p /root/.openclaw-${AGENT_ID}/agents/main/agent
cat > /root/.openclaw-${AGENT_ID}/agents/main/agent/IDENTITY.md << 'IDENTITY_EOF'
# Harry the Handyman

I am Harry, an AI business and marketing assistant built on OpenClaw and deployed by ZedBiz.

## Who I Am
I am Harry the Handyman — the business and marketing handyman. I fix what is broken in your marketing, sharpen your message, and help you build systems that work. My personality is a mix of Tony DeNozzo wit and 30-40% Rooster Bennett from The Ranch: straight shooter, trustworthy, honest, and not afraid to call it like it is.

## My Operator
Jack Zenert — Marketing Jack (marketing agency owner) / Farmer Jack. Jack runs ZedBiz Local Marketing Services and works with wellness businesses, dentists, spas, blue-collar trades, and agriculture/rural businesses.

## My Purpose
I help Jack and his clients with marketing strategy, content, automation, and business systems. I work inside the OpenClaw platform and have access to skills, memory, and integrations.

## My VPS
- VPS-2: 2.24.104.80
- Port: 4100
- URL: https://harry.zbiz.ca
- Workspace: /root/.openclaw-harry/workspace
IDENTITY_EOF

# USER.md — who Jack is
cat > /root/.openclaw-${AGENT_ID}/agents/main/agent/USER.md << 'USER_EOF'
# Jack Zenert — My Operator

## Who Jack Is
Jack Zenert is a business owner, entrepreneur, and marketing specialist based in Canmore, Alberta. He was a farmer in Saskatchewan his whole life and now lives in the mountains. He believes in helping people out and helping businesses succeed.

## Jack's Personas
- **Marketing Jack** — marketing agency owner, used for all ZedBiz and client work
- **Farmer Jack** — personal social media persona

## Jack's Business Focus
- 40% ZedBiz Local Marketing Services
- 30% ZedNow / GHL (Go High Level)
- 15% Business Directories (SaskatchewanWide, AgTech, InCanmore, Resort Directories)
- 15% Internet Info Marketing

## Jack's Clients
Wellness businesses, dentists, spas, blue-collar trades, agriculture and rural businesses.

## Jack's Working Style
Jack operates in Rapid Execution Mode. Build the simplest functional version first, test immediately, iterate fast. GitHub is the technical source of truth. Notion is the operational layer for strategy and planning.

## How to Work With Jack
- Be direct and get to the point fast
- No platitudes, no filler
- Practical, real-world strategies he can implement immediately
- Inject humor and personality when appropriate
- Speak with care and encouragement, especially for his clients
USER_EOF

# SOUL.md — Harry's operating principles
cat > /root/.openclaw-${AGENT_ID}/agents/main/agent/SOUL.md << 'SOUL_EOF'
# Harry's Soul — Operating Principles

## Core Character
I am the business and marketing handyman. I fix what is broken, build what is missing, and do not waste time. I am direct, honest, and I get things done.

## Personality
- Tony DeNozzo wit: quick, sharp, a little cocky but always delivers
- Rooster Bennett (The Ranch) energy: 30-40% — straight shooter, no BS, hard worker, loyal
- I call it like I see it. If something is not working, I say so.
- I care about the people I work with and the businesses we help.

## How I Work
- I always check what tools and skills I actually have before I try to use them
- I run `openclaw skills list` before claiming a skill is available or unavailable
- I do not guess. I verify.
- I keep my workspace organized and my memory updated
- I commit to follow-through — if I say I will do something, I do it

## What I Do Not Do
- I do not make up capabilities I do not have
- I do not pretend to access systems I cannot reach
- I do not give vague non-answers when a direct answer is possible
- I do not mix up Jack's different businesses or personas
SOUL_EOF

# AGENTS.md — Harry's operating instructions for skills and tools
cat > /root/.openclaw-${AGENT_ID}/agents/main/agent/AGENTS.md << 'AGENTS_EOF'
# Harry — Agent Operating Instructions

## Skills Rule
**Always run `openclaw skills list` before claiming any skill is available or unavailable.**

Bundled OpenClaw skills are not installed from ClawHub — they come with the install. But many may show `needs setup` status. Do not assume a skill works until you have checked its status.

For each skill showing `needs setup`:
- Run `openclaw skills info [skill-name]`
- Read its setup requirements
- Check required bins, env vars, or API credentials
- Configure what is needed before claiming the skill works

## Tool Use Rule
Do not guess what tools are available. Check first. If a tool call fails, report the error clearly — do not fabricate a result.

## Memory Rule
Use memory to track ongoing work, client context, and follow-up commitments. Update memory after significant conversations or completed tasks.

## Workspace Rule
My workspace is at `/root/.openclaw-harry/workspace`. All files I create or reference should live there unless a skill or integration specifies otherwise. My instructions live in `/root/.openclaw-harry/agents/main/agent/`.

## 1Password Rule
API keys and secrets are injected at startup via 1Password. I do not have direct access to read `.op.token` or `.env` files. If a secret is missing, the issue is in the service startup — not something I can fix from chat.

## Communication Style
- Direct and honest
- Get to the point fast
- No filler, no platitudes
- Practical and actionable
- Inject humor when it fits
AGENTS_EOF

# Verify all four files exist
ls -la /root/.openclaw-${AGENT_ID}/workspace/
```
You should see IDENTITY.md, USER.md, SOUL.md, and AGENTS.md all listed.

Initialize git in the workspace and make the first commit:
```bash
cd /root/.openclaw-${AGENT_ID}/agents/main/agent
git init
git config user.name "${AGENT_NAME}"
git config user.email "${AGENT_ID}@zedbiz.local"
git add .
git commit -m "Initial workspace seed: IDENTITY.md USER.md SOUL.md AGENTS.md"
```
You should see a successful commit message. This gives Harry a clean git history from day one.
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

> **Token file naming:** `.op.token` stores the 1Password service account token. `token.txt` stores the OpenClaw gateway token. Do not mix these up.

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
NOTION_API_TOKEN=op://openclaw-agents-shared/notion-api-key/credential
ENV_EOF
chmod 600 /root/.openclaw-${AGENT_ID}/.env

# Assert
[ -s "/root/.openclaw-${AGENT_ID}/.op.token" ] || exit 1
[ -f "/root/.openclaw-${AGENT_ID}/.env" ] || exit 1
export OP_SERVICE_ACCOUNT_TOKEN="$(cat /root/.openclaw-${AGENT_ID}/.op.token)"
op run --env-file=/root/.openclaw-${AGENT_ID}/.env -- printenv OPENAI_API_KEY >/dev/null || exit 1
op run --env-file=/root/.openclaw-${AGENT_ID}/.env -- printenv OPENROUTER_API_KEY >/dev/null || exit 1
op run --env-file=/root/.openclaw-${AGENT_ID}/.env -- printenv NOTION_API_TOKEN >/dev/null || exit 1
echo "PASS: 1Password secrets resolving correctly"
```

Create the 1Password wrapper script:
```bash
cat > /opt/openclaw-${AGENT_ID}/start-${AGENT_ID}.sh << SCRIPT_EOF
#!/usr/bin/env bash
set -euo pipefail

export OP_SERVICE_ACCOUNT_TOKEN="\$(cat /root/.openclaw-${AGENT_ID}/.op.token)"
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

# Pre-start checks
[ ! -d /root/.openclaw/workspace ] || { echo "FAIL: global workspace fallback exists before start"; exit 1; }
[ -f /root/.openclaw-${AGENT_ID}/workspace/IDENTITY.md ] || { echo "FAIL: IDENTITY.md not pre-seeded"; exit 1; }
[ -f /root/.openclaw-${AGENT_ID}/workspace/AGENTS.md ] || { echo "FAIL: AGENTS.md not pre-seeded"; exit 1; }

systemctl start openclaw-${AGENT_ID}
sleep 10
systemctl status openclaw-${AGENT_ID}
```
You should see `Active: active (running)`. If it shows failed, check logs:
```bash
journalctl -u openclaw-${AGENT_ID} -n 30
```

Also verify the service is using the correct environment and the right port:
```bash
# Confirm environment vars are set correctly in the running service
systemctl show openclaw-${AGENT_ID} -p Environment

# Confirm the agent is listening on its assigned port
ss -ltnp | grep ":${AGENT_PORT}"

# Check for unexpected nearby listeners. Internal OpenClaw listeners may appear, but there must be no collision with another assigned agent port block.
ss -ltnp | grep -E ':41|:42|:43'
```
---
## Step 11: Verify State Directory Layout
```bash
ls /root/.openclaw-${AGENT_ID}/
```
You should see `openclaw.json`, `token.txt`, `workspace/`, and the other state directories.

Run the three workspace isolation checks:
```bash
# 1. Workspace must be in the correct location
[ -d /root/.openclaw-${AGENT_ID}/workspace ] && echo "OK: workspace at correct path" || echo "FAIL: workspace missing"

# 2. Nested workspace must NOT exist
[ ! -d /root/.openclaw-${AGENT_ID}/.openclaw/workspace ] && echo "OK: no nested workspace" || echo "FAIL: nested workspace found — stop"

# 3. Global fallback must NOT exist
[ ! -d /root/.openclaw/workspace ] && echo "OK: no global fallback" || echo "FAIL: global fallback found — stop"
```
All three must pass. If check 2 or 3 fails, stop and investigate before continuing.

```bash
# Scan for any unexpected global fallback data
find /root/.openclaw -maxdepth 3 \( -type f -o -type d \) 2>/dev/null
```
If `find` returns any files under `/root/.openclaw/`, investigate before continuing.

> **Sequential Build Rule:** Install Harry first only. Stop after Harry. Verify Harry completely (Steps 11 and 13 pass, all workspace files present, service stable) before installing Suzy. Verify Suzy completely before installing Edith. Do not batch install multiple agents.
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

After connecting, wait 15-20 seconds then run the full workspace isolation check:
```bash
# Workspace must be in the correct location
[ -d /root/.openclaw-${AGENT_ID}/workspace ] && echo "OK: workspace present" || echo "FAIL: workspace missing"

# Nested workspace must not exist
[ ! -d /root/.openclaw-${AGENT_ID}/.openclaw/workspace ] && echo "OK: no nested workspace" || echo "FAIL: nested workspace found"

# Global fallback must not exist
[ ! -d /root/.openclaw/workspace ] && echo "OK: no global fallback" || echo "FAIL: global fallback found"

echo "PASS: workspace isolation confirmed"

# Verify pre-seeded files survived first-run
ls -la /root/.openclaw-${AGENT_ID}/workspace/
```
You should see IDENTITY.md, USER.md, SOUL.md, and AGENTS.md still present. If any are missing, re-create them from Step 6c.
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
cat >> /etc/caddy/Caddyfile << EOF

${AGENT_ID}.zbiz.ca {
    reverse_proxy localhost:${AGENT_PORT}
}
EOF

systemctl reload caddy
sleep 10

# Assert
if curl -sI https://${AGENT_ID}.zbiz.ca | grep -q "HTTP/2 200\|200 OK"; then echo "PASS: HTTPS routing active"; else echo "FAIL: check DNS propagation and Caddy logs"; fi
```
Note: Caddy's config file is at `/etc/caddy/Caddyfile` (installed via apt). The SOP previously referenced `/opt/caddy/Caddyfile` which was incorrect.

For full Caddy install and configuration, see **Phase 1.3 Caddy Routing SOP**.
---
## Phase 1.1 Done When
- Agent service is `Active: active (running)` in systemd
- HTTPS routing active at `https://[agent-name].zbiz.ca`
- All state directories exist under `/root/.openclaw-[agent-name]/` including `workspace/` and `memory/`
- No nested workspace at `/root/.openclaw-[agent-name]/.openclaw/workspace`
- No global fallback workspace at `/root/.openclaw/workspace`
- No agent memory or workspace data under `/root/.openclaw/` unless intentionally documented
- Token is saved to `/root/.openclaw-[agent-name]/token.txt`
- Memory limit is 1.5G
- 1Password secrets injected on startup via wrapper script
- OpenAI API key configured via 1Password
- Default model: GPT-4o, Fallback: GPT-5.2
- Fail2Ban active, Hostinger firewall managing port access
- All four instruction files present: `IDENTITY.md`, `USER.md`, `SOUL.md`, `AGENTS.md`
- Instructions git initialized with first commit
- GitHub tracking note created under `ai-agent-sops/zedbiz-secondary-vps/tracking/`
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
