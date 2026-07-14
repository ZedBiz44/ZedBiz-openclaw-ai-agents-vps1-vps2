# Maggie and Vivian 1Password Startup Repair and v2026.7.1 Test

Date: 2026-07-13 Mountain Time  
Verified by: Cody  
VPS: VPS1  
Related GitHub issue: ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2#60

## Purpose

Restore Maggie and Vivian as controlled test agents, repair their 1Password secret injection path, and update both to OpenClaw v2026.7.1 before comparing model behavior.

## Broken Step

The `openclaw-maggie.service` and `openclaw-vivian.service` units called each agent's legacy `start-agent.sh`. That wrapper called the shared `/opt/openclaw/scripts/resolve-secrets.sh`, which attempted to use the shared 1Password Connect token file. The shared file contained a service-account token, not the Connect JWT expected by that resolver, so startup failed with HTTP 401 and no container survived the Docker/host restart.

## Old Assumption

The old units assumed the shared 1Password Connect resolver remained the valid startup path for every VPS1 agent. Maggie and Vivian already had their own working `.op.token` service-account credentials and agent-specific `op-start-AGENT.sh` scripts, but systemd did not use them.

## Tested Correction

- Backed up each existing `.env.resolved`, `op-start-AGENT.sh`, and systemd service file.
- Changed each agent startup helper to read only its own `.op.token`.
- Added `op inject -i .env -o .env.resolved --force` before every start or restart.
- Kept `.env.resolved` mode at `600` and preserved agent ownership for manual maintenance.
- Changed each systemd unit to call the corrected agent-specific `op-start-AGENT.sh` helper.
- Reloaded and enabled systemd using the approved Docker Alpine root workaround.
- Restarted Maggie first and verified the complete path before applying it to Vivian.

## Files Changed on VPS1

- `/opt/openclaw/agents/maggie/op-start-maggie.sh`
- `/etc/systemd/system/openclaw-maggie.service`
- `/opt/openclaw/agents/vivian/op-start-vivian.sh`
- `/etc/systemd/system/openclaw-vivian.service`
- Each agent's generated `.env.resolved` file

No secret values were recorded.

## Test Results

### Maggie

- Systemd service: active and enabled
- Container: running and healthy
- OpenClaw image label: `2026.7.1`
- Host health endpoint: HTTP 200
- Resolved 1Password values present: OpenAI, OpenRouter, Discord, and Notion
- Discord identity: `@maggie-openclaw`
- Gateway selected model: `openai/gpt-5.5`

### Vivian

- Systemd service: active and enabled
- Container: running; host health endpoint returned HTTP 200 during startup grace
- OpenClaw image label: `2026.7.1`
- Resolved 1Password values present: OpenAI, OpenRouter, Discord, and Notion
- Discord identity: `@vivian-openclaw`
- Gateway selected model: `codex/gpt-5.5`
- OAuth profile `openai:jzedbiz@gmail.com`: expired
- API-key backup profile remains present

## Remaining Test

Jack must complete Vivian's browser device-code authorization. After authorization, verify the new OAuth expiry, confirm OAuth is first in the effective profile order, send a live GPT-5.5 request, and prove no API-key or OpenRouter fallback handled it. Then compare Vivian's response behavior with Maggie's.

## Rollback

Restore the timestamped agent helper and `.env.resolved` backups plus the backed-up systemd service files, reload systemd, and restart only the affected agent. Do not restore or expose secret contents in GitHub.
