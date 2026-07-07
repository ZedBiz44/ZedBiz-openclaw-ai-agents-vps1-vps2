# 2026-07-07 - Victor 1Password Connect Secret Skill

Date: 2026-07-07 Mountain Time | Agent Name: Cody | Status: Testing

## Summary

- Built Option A for Victor: a custom `onepassword-connect-secrets` skill that uses the existing VPS1 1Password Connect REST API instead of the desktop-only 1Password MCP workflow.
- Added a small Python helper for Connect health checks, vault/item metadata, password-item creation, and field updates.
- Installed the token file path expected by the skill inside Victor's mounted config space.
- Verified the Connect server is reachable from Victor.
- Authentication is not fully live yet because the available token file returns `401`.

## Skill Purpose

- Let Victor create and edit ZedBiz agent secrets through 1Password Connect from a headless Docker container.
- Avoid the ClawHub/built-in `@steipete/1password` desktop workflow, which requires 1Password desktop app integration and interactive sign-in.
- Keep secret values out of chat, GitHub, Notion, and ordinary command output.

## Setup Details

- Skill folder in repo:
  - `ai-agent-sops/zedbiz-main-vps/agent-specific/victor/skills/onepassword-connect-secrets`
- Live Victor skill folders:
  - `/home/node/.openclaw/skills/onepassword-connect-secrets`
  - `/home/node/.openclaw/workspace/skills/onepassword-connect-secrets`
- Helper script:
  - `scripts/op_connect.py`
- Connect API URL from Victor:
  - `http://172.18.0.3:8080`
- Token file path inside Victor:
  - `/home/node/.openclaw/credentials/1password-connect-token`

## Files Changed

- Added `SKILL.md` for Victor's 1Password Connect workflow.
- Added `scripts/op_connect.py` helper.
- Copied Victor's existing host token file into the mounted credential path:
  - From `/opt/openclaw/agents/victor/.op.token`
  - To `/opt/openclaw/agents/victor/config/credentials/1password-connect-token`

## Commands Used

- Used SSH to VPS1 as `jackadmin`.
- Used Docker to inspect Victor and 1Password Connect network placement.
- Used the Alpine root-container workaround to place and chown the token file without sudo.
- Used Victor's own container to test Connect health and helper availability.

## Test Result

- Victor container status: `running healthy`.
- 1Password Connect containers:
  - `1password-connect-api` running.
  - `1password-connect-sync` running.
- Docker network:
  - Victor is on `openclaw`.
  - `1password-connect-api` is on `openclaw` at `172.18.0.3`.
- Connect health from Victor:
  - `GET /health` succeeded and returned 1Password Connect API `1.8.2`.
- Token authentication:
  - `GET /v1/vaults` returned `401` with the currently available token file.

## Current Blocker

- The available token file is not accepted as a 1Password Connect API bearer token.
- The next action is to replace `/home/node/.openclaw/credentials/1password-connect-token` with a valid Connect access token scoped to the intended agent/secrets vault.
- After replacement, run:

```bash
python3 /home/node/.openclaw/skills/onepassword-connect-secrets/scripts/op_connect.py vaults
```

## Rollback Note

- Remove the live skill folders:
  - `/home/node/.openclaw/skills/onepassword-connect-secrets`
  - `/home/node/.openclaw/workspace/skills/onepassword-connect-secrets`
- Remove the token copy if Victor should not have Connect access:
  - `/home/node/.openclaw/credentials/1password-connect-token`

## Links

- GitHub Issue: Not created
- Notion page: https://app.notion.com/p/396a3e33d5818174b3a4fafd9a9dbebb
- Related commit: This commit
