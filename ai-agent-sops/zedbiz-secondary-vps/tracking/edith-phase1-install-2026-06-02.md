# Edith - Phase 1 Install Tracking
**Date:** 2026-06-02 MST
**Agent:** Edith
**VPS:** VPS2 (2.24.104.80 / Hostinger)
**Installed by:** Manus AI

## Phase 1 Completion Status: DONE ✅

### Install Summary
- OpenClaw version: 2026.5.28
- Port: 4300
- URL: https://edith.zbiz.ca
- Gateway token: stored at /root/.openclaw-edith/token.txt
- Install dir: /opt/openclaw-edith/
- State dir: /root/.openclaw-edith/

### Checklist
- [x] Node.js v24.15.0 verified
- [x] Base packages installed (curl, ca-certificates, gnupg, git, build-essential, openssl, fail2ban, psmisc)
- [x] Directories created: /opt/openclaw-edith, /root/.openclaw-edith
- [x] OpenClaw 2026.5.28 installed via npm into /opt/openclaw-edith/
- [x] @openclaw/codex and @openclaw/discord installed to /root/.openclaw-edith/npm/
- [x] codex-home dir created: /root/.openclaw-edith/agents/main/agent/codex-home
- [x] openclaw.json written with correct gateway.mode, port 4300, workspace path
- [x] Default model: openrouter/google/gemini-3.1-flash-preview
- [x] openai + openrouter plugins explicitly enabled in config
- [x] memory-core, memory-wiki, active-memory plugins added to openclaw.json
- [x] Token generated and saved to token.txt (chmod 600)
- [x] Full directory structure created: agents/main/agent, agents/main/sessions, memory, workspace, plugins, logs, tasks, identity
- [x] IDENTITY.md written
- [x] USER.md written
- [x] SOUL.md written
- [x] AGENTS.md written
- [x] Wiki vault structure created (concepts, entities, reports, sources, syntheses, _views, _attachments)
- [x] wiki/entities/index.md and wiki/index.md seeded
- [x] memory/.dreams/session-corpus directory created
- [x] .env created with 1Password op:// references
- [x] .op.token copied from Harry (shared VPS2 service account)
- [x] start-edith.sh created with op run env injection (chmod 700)
- [x] systemd service created: openclaw-edith.service
- [x] Service enabled (auto-start on boot)
- [x] Service started: active (running)
- [x] Port 4300 listening
- [x] MemoryMax=1.5G enforced
- [x] Workspace isolation confirmed (no nested workspace, no global fallback)
- [x] 1Password env injection confirmed (OPENAI, OPENROUTER, NOTION keys resolving)
- [x] Fail2Ban active (SSH jail: 0 currently banned, 8 total banned)
- [x] edith.zbiz.ca added to /etc/caddy/Caddyfile
- [x] Caddy reloaded
- [x] HTTPS 200 confirmed at https://edith.zbiz.ca
- [x] Memory status: Dreaming 0 2 * * * (America/Edmonton) confirmed
- [x] Wiki status: Vault ready at /root/.openclaw-edith/workspace/wiki confirmed

### Notes
- openclaw setup --non-interactive does not support --accept-risk in 2026.5.28. Directory structure created manually matching Harry/Suzy layout. Confirmed working.
- .op.token shared from Harry. Edith uses same VPS2 service account.
- Step 13 (browser first-run) is a human step - Jack to connect at https://edith.zbiz.ca with token from /root/.openclaw-edith/token.txt
- Step 12 (model config in browser UI) is also a human step - set OpenAI provider in Settings > Models

### Token
Gateway token: 21f32ff5333123d8b8f1a38e11ff5decb4eb52b3f9409f25
(Also stored at /root/.openclaw-edith/token.txt on VPS2)

### Pending (Phase 2+)
- Browser first-run connection (human step - Jack)
- OAuth token login for Edith (device code flow or copy from Harry)
- LLM model picker config update (Phase 2.1)
- Memory stack setup (Phase 2.1)
- Skills setup (Phase 2.2)
- Asana setup (Phase 2.3)
- Agent branding (Phase 2.4)
- Discord bot setup (Phase 3)

---

## Phase 2.1a — OpenAI Codex OAuth Setup: DONE ✅
**Completed:** 2026-06-02 MST

### Method Used
Path A — Copied auth-profiles.json and auth-state.json from Harry (existing valid token).

### Results
- auth-profiles.json: copied to /root/.openclaw-edith/agents/main/agent/auth-profiles.json (chmod 600)
- auth-state.json: lastGood = openai-codex:jzedbiz@gmail.com
- Token: openai-codex:jzedbiz@gmail.com [openai-codex/oauth; expires 2026-06-06T23:57:52.103Z]
- Token valid for: 4 days at time of setup
- @openclaw/codex npm plugin: installed at /root/.openclaw-edith/npm/node_modules/@openclaw/codex
- codex-home dir: /root/.openclaw-edith/agents/main/agent/codex-home

### Renewal Note
Token expires 2026-06-06. Renew on Harry first (device code login), then copy to Suzy and Edith:
```bash
for agent in suzy edith; do
  cp /root/.openclaw-harry/agents/main/agent/auth-profiles.json \
     /root/.openclaw-${agent}/agents/main/agent/auth-profiles.json
  chmod 600 /root/.openclaw-${agent}/agents/main/agent/auth-profiles.json
  systemctl restart openclaw-${agent}
done
```
