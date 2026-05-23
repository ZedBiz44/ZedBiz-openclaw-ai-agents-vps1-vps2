# SOP Update: Cody Fixes — Environment Variables + OpenAI Models

**Date:** 2026-05-23
**Agent:** Manus

## Changes Applied to Both SOPs

### Critical Fix: OPENCLAW_HOME replaced with OPENCLAW_STATE_DIR + OPENCLAW_CONFIG_PATH

Previous (wrong):
```
Environment=OPENCLAW_HOME=/root/.openclaw-${AGENT_ID}
```

Correct:
```
Environment=HOME=/root
Environment=OPENCLAW_STATE_DIR=/root/.openclaw-${AGENT_ID}
Environment=OPENCLAW_CONFIG_PATH=/root/.openclaw-${AGENT_ID}/openclaw.json
Environment=OPENCLAW_GATEWAY_PORT=${AGENT_PORT}
```

Reason: OPENCLAW_HOME is treated like a user home folder — OpenClaw may append .openclaw under it, creating /root/.openclaw-harry/.openclaw/ which defeats the purpose.

### Memory Limit Updated
- Old: MemoryMax=512M
- New: MemoryMax=1.5G
- Reason: 512M is too tight for OpenClaw with plugins and skills loaded

### npm install fixes
- Added: npm init -y before npm install
- Changed: npm install openclaw -> npm install openclaw@latest

### Base packages step added (Step 0.5)
- curl, ca-certificates, gnupg, git, build-essential, openssl, ufw

### OpenAI API Key + Models added to Phase 1.1 (Step 9)
- Default model: GPT-4o
- Fallback model: GPT-4.5
- Note added: OpenAI OAuth requires human browser authorization

### Step 7 verification improved
- Now checks state dir BEFORE browser connect
- Checks workspace is NOT in /root/.openclaw/workspace-[agent]
- Checks workspace IS in /root/.openclaw-[agent]/workspace after browser connect

### Critical line note updated
- Old: "OPENCLAW_HOME is the single most important line"
- New: "OPENCLAW_STATE_DIR and OPENCLAW_CONFIG_PATH are the critical lines"
