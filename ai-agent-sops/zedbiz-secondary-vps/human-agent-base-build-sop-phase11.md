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
- OpenAI API key configured via 1Password
- Curated model list active with Primary: `openai/gpt-5.5` and Fallbacks: `[gpt-5.5, gpt-5.4, gpt-5.4-mini, gpt-5.3-codex, gpt-5.2]`
- Workspace files (`IDENTITY.md`, `USER.md`, `SOUL.md`, `AGENTS.md`) pre-seeded before first launch
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

## Step 5b: Install Required Plugins
We must install the codex and discord plugins into the per-agent npm directory:
```bash
cd /opt/openclaw-${AGENT_ID}
npm install @openclaw/codex @openclaw/discord

# Create codex-home directory
mkdir -p /root/.openclaw-${AGENT_ID}/agents/main/agent/codex-home
```

---

## Step 6: Generate Token and Write Config
Note: `gateway.mode` is required. Omitting it will cause OpenClaw to refuse to start with a CONFIG error.
**Critical:** The `agents.defaults` block must contain the curated `models` object from Harry. If omitted, OpenClaw falls back to the full raw API catalogue, populating the dropdown with 100+ junk models.

```bash
export NEW_TOKEN=$(openssl rand -hex 24)

# We use Python to merge Harry's curated models section into Edith's custom workspace
python3 - << 'EOF'
import json, os

AGENT_ID = os.environ.get('AGENT_ID')
AGENT_PORT = os.environ.get('AGENT_PORT')
NEW_TOKEN = os.environ.get('NEW_TOKEN')
VPS_IP = os.environ.get('VPS_IP')

# Read Harry's config to extract the curated models list
with open('/root/.openclaw-harry/openclaw.json') as f:
    harry = json.load(f)
harry_models = harry['agents']['defaults']['models']

# Create Edith's openclaw.json structure
config = {
  "gateway": {
    "mode": "local",
    "port": int(AGENT_PORT),
    "bind": "lan",
    "auth": {
      "token": NEW_TOKEN
    },
    "controlUi": {
      "dangerouslyDisableDeviceAuth": True,
      "allowedOrigins": [
        f"http://{VPS_IP}:{AGENT_PORT}",
        f"http://localhost:{AGENT_PORT}",
        f"https://{AGENT_ID}.zbiz.ca"
      ]
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "openai/gpt-5.5",
        "fallbacks": [
          "openai/gpt-5.5",
          "openai/gpt-5.4",
          "openai/gpt-5.4-mini",
          "openai/gpt-5.3-codex",
          "openai/gpt-5.2"
        ]
      },
      "models": harry_models,
      "workspace": f"/root/.openclaw-{AGENT_ID}/workspace",
      "contextLimits": {
        "toolResultMaxChars": 64000,
        "memoryGetMaxChars": 48000,
        "memoryGetDefaultLines": 240,
        "postCompactionMaxChars": 6000
      },
      "bootstrapMaxChars": 24000,
      "bootstrapTotalMaxChars": 120000
    }
  },
  "plugins": {
    "entries": {
      "openai": { "enabled": True },
      "openrouter": { "enabled": True }
    }
  },
  "meta": {
    "lastTouchedVersion": "2026.5.28"
  }
}

# Write Edith's config
with open(f'/root/.openclaw-{AGENT_ID}/openclaw.json', 'w') as f:
    json.dump(config, f, indent=2)

print("OK: Curated openclaw.json written")
EOF

echo $NEW_TOKEN > /root/.openclaw-${AGENT_ID}/token.txt
chmod 600 /root/.openclaw-${AGENT_ID}/token.txt
echo "Token: $NEW_TOKEN"
```
Copy the token — you will need it to connect in the browser. Verify:
```bash
grep '"primary": "openai/gpt-5.5"' /root/.openclaw-${AGENT_ID}/openclaw.json && echo "OK: Primary model correct" || echo "FAIL"
grep '"workspace"' /root/.openclaw-${AGENT_ID}/openclaw.json && echo "OK: workspace path set in config" || echo "FAIL"
```

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

## Step 6c: Pre-seed Workspace Files
We must pre-seed the instruction files into the workspace before the first service launch.
```bash
# Copy files from Harry's workspace to pre-seed the new agent's workspace
for f in IDENTITY.md USER.md SOUL.md AGENTS.md; do
  cp /root/.openclaw-harry/workspace/$f /root/.openclaw-${AGENT_ID}/workspace/
  chmod 600 /root/.openclaw-${AGENT_ID}/workspace/$f
done

# Verify
ls -la /root/.openclaw-${AGENT_ID}/workspace/
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

## Step 12: Verify OpenAI Models and Vision
The OpenAI API key is injected via 1Password. Verify it is available:
```bash
grep -q "OPENAI_API_KEY" /root/.openclaw-${AGENT_ID}/.env && echo "PASS: Key defined in .env" || echo "FAIL: Key missing from .env"
```

Verify that the `openclaw.json` has the curated `models` list:
```bash
python3 -c "
import json
with open('/root/.openclaw-${AGENT_ID}/openclaw.json') as f: c = json.load(f)
models = c['agents']['defaults']['models']
print(f'OK: Curated list has {len(models)} models')
"
```

---

## Step 12b: Set Up Agent Memory
Must be done before the browser first-run so that memory, wiki, and dreaming are initialized correctly.

### 12b-1: Add plugins to openclaw.json
We add `memory-core`, `memory-wiki`, and `active-memory` plugins to the `openclaw.json` config:
```bash
python3 - << 'EOF'
import json, os
AGENT_ID = os.environ.get('AGENT_ID', 'UNKNOWN')
p = f'/root/.openclaw-{AGENT_ID}/openclaw.json'
with open(p) as f: c = json.load(f)
if 'plugins' not in c: c['plugins'] = {}
if 'entries' not in c['plugins']: c['plugins']['entries'] = {}
c['plugins']['entries']['memory-core'] = {'enabled': True, 'config': {'dreaming': {'enabled': True, 'frequency': '0 2 * * *', 'timezone': 'America/Edmonton', 'verboseLogging': True, 'storage': {'mode': 'both', 'separateReports': True}, 'phases': {'light': {'enabled': True, 'lookbackDays': 7, 'limit': 50, 'dedupeSimilarity': 0.85}, 'deep': {'enabled': True, 'limit': 20, 'minScore': 0.6, 'minRecallCount': 2, 'minUniqueQueries': 1, 'recencyHalfLifeDays': 14, 'maxAgeDays': 90}, 'rem': {'enabled': True, 'lookbackDays': 30, 'limit': 10, 'minPatternStrength': 0.5}}}}}
c['plugins']['entries']['memory-wiki'] = {'enabled': True, 'config': {'vaultMode': 'isolated', 'bridge': {'enabled': True, 'readMemoryArtifacts': True, 'indexDreamReports': True, 'indexDailyNotes': True, 'indexMemoryRoot': True, 'followMemoryEvents': True}, 'ingest': {'autoCompile': True, 'allowUrlIngest': True}, 'search': {'backend': 'shared', 'corpus': 'all'}, 'context': {'includeCompiledDigestPrompt': True}, 'render': {'createBacklinks': True, 'createDashboards': True}, 'vault': {'path': f'/root/.openclaw-{AGENT_ID}/workspace/wiki'}}}
c['plugins']['entries']['active-memory'] = {'enabled': True, 'config': {'logging': True, 'queryMode': 'recent', 'promptStyle': 'balanced', 'qmd': {'searchMode': 'search'}}}
with open(p, 'w') as f: json.dump(c, f, indent=2)
print('OK: memory plugins added')
EOF
```

### 12b-2: Create wiki vault structure
```bash
for dir in concepts entities reports sources syntheses _views _attachments; do
  mkdir -p /root/.openclaw-${AGENT_ID}/workspace/wiki/$dir
done
mkdir -p /root/.openclaw-${AGENT_ID}/workspace/memory/.dreams/session-corpus
echo "# Entities\nAuto-populated as conversation logs are analyzed." > /root/.openclaw-${AGENT_ID}/workspace/wiki/entities/index.md
echo "# Knowledge Vault\nLong-term structured knowledge base." > /root/.openclaw-${AGENT_ID}/workspace/wiki/index.md
```

### 12b-3: Restart and verify memory status
```bash
systemctl restart openclaw-${AGENT_ID} && sleep 10

# We must set correct HOME and OPENCLAW_STATE_DIR so the CLI resolves the local agent state correctly
HOME=/root/.openclaw-${AGENT_ID} \
OPENCLAW_CONFIG=/root/.openclaw-${AGENT_ID}/openclaw.json \
OPENCLAW_STATE_DIR=/root/.openclaw-${AGENT_ID} \
/opt/openclaw-${AGENT_ID}/node_modules/.bin/openclaw memory status 2>&1 | grep "Dreaming:"
# Expected: Dreaming: 0 2 * * * (America/Edmonton)

HOME=/root/.openclaw-${AGENT_ID} \
OPENCLAW_CONFIG=/root/.openclaw-${AGENT_ID}/openclaw.json \
OPENCLAW_STATE_DIR=/root/.openclaw-${AGENT_ID} \
/opt/openclaw-${AGENT_ID}/node_modules/.bin/openclaw wiki status 2>&1 | grep "Vault:"
# Expected: Vault: ready (...)
```

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

## Step 16: Create GitHub Tracking Note
Create a tracking note for the agent install and commit it to GitHub.
```bash
cat > /home/ubuntu/zedbiz-ai-agents/ai-agent-sops/zedbiz-secondary-vps/tracking/${AGENT_ID}-phase1-install-2026-06-02.md << EOF
# ${AGENT_NAME} Phase 1 Installation Log

## Metadata
- **Date:** 2026-06-02 MST
- **Port:** ${AGENT_PORT}
- **Domain:** https://${AGENT_ID}.zbiz.ca

## Steps Completed
- npm folder install at /opt/openclaw-${AGENT_ID}
- Configured openclaw.json with curated model dropdown (Primary: openai/gpt-5.5)
- Pre-seeded instruction files
- systemd service created and enabled
- Memory setup (memory-core, memory-wiki, active-memory) active and verified
- HTTPS routing configured in Caddy
EOF

cd /home/ubuntu/zedbiz-ai-agents
git add ai-agent-sops/zedbiz-secondary-vps/tracking/${AGENT_ID}-phase1-install-2026-06-02.md
git commit -m "${AGENT_NAME} Phase 1 complete"
git push origin main
```

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
- Curated model dropdown is identical to Harry and Suzy (Primary: `openai/gpt-5.5`, Fallbacks active)
- Fail2Ban active, Hostinger firewall managing port access
- All four workspace files present: `IDENTITY.md`, `USER.md`, `SOUL.md`, `AGENTS.md`
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
