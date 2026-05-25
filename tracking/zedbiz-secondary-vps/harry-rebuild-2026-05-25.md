# Harry Rebuild — 2026-05-25

## Summary
Full clean rebuild of Harry on VPS-2 (2.24.104.80) following the finalized Phase 1.1 SOP v5.

## What Changed
- VPS wiped and rebuilt fresh
- Port changed from 4000 to 4100 (spaced port convention)
- HOME set to per-agent: /root/.openclaw-harry
- 1Password wrapper uses escaped \$(cat .op.token) — token not baked into script
- systemd Environment= includes HOME, OPENCLAW_STATE_DIR, OPENCLAW_CONFIG_PATH
- Pre-start global workspace check added and passed
- 1Password hard gate passed (op run resolved OPENAI_API_KEY)
- Fail2Ban active with SSH jail
- Caddy v2.11.3 with HTTPS on harry.zbiz.ca
- IDENTITY.md created in per-agent workspace
- No global /root/.openclaw/workspace fallback found

## Verification Results
- Service: active (enabled)
- Port 4100: listening
- Internal port 4102: 127.0.0.1 only (expected OpenClaw IPC)
- HTTPS: HTTP/2 200 on https://harry.zbiz.ca
- Workspace isolation: PASS
- Global fallback: PASS (none)

## Agent Details
- OpenClaw: 2026.5.22
- Default model: openai/gpt-4o
- State dir: /root/.openclaw-harry
- Install dir: /opt/openclaw-harry
- Domain: https://harry.zbiz.ca
