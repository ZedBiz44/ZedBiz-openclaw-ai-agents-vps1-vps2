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

## Full VPS1 Fleet Rollout

Jack approved extending the tested Maggie/Vivian correction to the remaining VPS1 agents on 2026-07-13.

### Agents Added

- Amanda
- Gohzed
- Grogar
- Inga
- Marsha
- Victor
- Wilma

### Rollout Method

- Verified every individual `.op.token` with `op whoami` before changing the agent.
- Proved every `.env` resolved successfully in a temporary file with zero remaining `op://` references.
- Applied the tested per-agent `op inject` startup helper and systemd service pattern.
- Enabled and restarted the services in controlled batches.
- Verified service state, image version, HTTP health, secret presence, generated-file ownership, and Discord startup.

### Victor Custom Image Exception

Victor's Compose file hard-coded `zedbiz-openclaw-victor:2026.6.8-ssh`, so changing his `.env` did not update the running image. His custom Dockerfile adds the Docker CLI and OpenSSH client required for his administrator role.

The first rebuild attempt exposed two separate build-path problems:

- GHCR rejected the anonymous metadata request with HTTP 403 even though the approved base image was already present locally.
- Building from Victor's full workspace failed because protected backup files were incorrectly included in the Docker build context.

The tested correction was to build from a temporary minimal context containing only `Dockerfile.victor`, use the already-downloaded `ghcr.io/zedbiz44/openclaw-base:latest` image, tag the result as `zedbiz-openclaw-victor:2026.7.1-ssh`, and recreate only Victor. Docker CLI and OpenSSH availability were reverified inside the new container.

### Final Fleet Audit

All ten primary VPS1 agents passed:

- OpenClaw image label `2026.7.1`
- Systemd service enabled and active
- HTTP health endpoint returned 200
- Container restart count zero
- Zero unresolved `op://` references
- `.env.resolved` owned by UID/GID `1001:1001`
- `.env.resolved` mode `600`

Agents audited: Amanda, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma.

## Edith Separate Deployment Update

Edith was updated separately after the primary ten-agent fleet because she had no systemd service and was surviving through Docker's `unless-stopped` policy with a `.env.resolved` snapshot from 2026-06-23.

### Correction

- Verified Edith's individual 1Password service-account token.
- Proved her `.env` resolved with zero remaining `op://` references.
- Backed up her generated environment, startup helper, and Compose file.
- Installed the tested per-agent `op inject` startup helper.
- Created and enabled `openclaw-edith.service`.
- Recreated Edith on the approved shared v2026.7.1 image.

### Verification

- OpenClaw image label: `2026.7.1`
- Systemd service: enabled and active
- HTTP health endpoint: 200
- Container restart count: zero
- Discord identity: `@edith-openclaw`
- Required OpenAI, OpenRouter, Discord, and Notion environment values: present
- Zero unresolved `op://` references
- `.env.resolved`: `1001:1001`, mode `600`

### OAuth Finding

Edith's stored OAuth metadata reported an unexpired date, but the required live provider probe failed. OpenAI returned `refresh_token_invalidated` and stated that the session had ended and must be authorized again. This proves the stored expiry date was not a valid health test. Edith requires a new human device-code login before OAuth can be considered working; the API-key backup remains available in the meantime.
