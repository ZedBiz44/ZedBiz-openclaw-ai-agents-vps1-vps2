# 2026-07-07 - Victor 1Password Connect Secret Skill

Date: 2026-07-07 Mountain Time | Agent Name: Cody | Status: Testing

## Summary

- Built Option A for Victor: a custom `onepassword-connect-secrets` skill that uses the existing VPS1 1Password Connect REST API instead of the desktop-only 1Password MCP workflow.
- Added a small Python helper for Connect health checks, vault/item metadata, password-item creation, and field updates.
- Installed the token file path expected by the skill inside Victor's mounted config space.
- Installed the matching 1Password Connect credentials file supplied by Jack.
- Reset the stale local Connect cache volume after changing credentials.
- Verified Victor can authenticate to 1Password Connect and list vault metadata.

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
  - `http://1password-connect-api:8080`
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
  - `1password-connect-api` is on `openclaw`; Victor reaches it by Docker DNS name `1password-connect-api`.
- Connect health from Victor:
  - `GET /health` succeeded and returned 1Password Connect API `1.8.2`.
- Token authentication:
  - `GET /v1/vaults` returned `401` with the currently available token file.

## 2026-07-07 Retest After Token Was Added To Victor Vault

- Retrieved the `credential` field from the `victor_1password-token` item in the `agent-victor` 1Password vault using Victor's service-account token.
- Wrote that value into Victor's mounted Connect-token path:
  - `/home/node/.openclaw/credentials/1password-connect-token`
- Restarted Victor.
- Verified Victor returned to Docker health `healthy`.
- Re-tested Connect health from Victor:
  - `health` still succeeds.
- Re-tested Connect authentication from Victor:
  - `vaults` still fails with `401`.
  - Error changed to `Authentication: (Invalid token signature), Each header's KID must match the KID of the public key`.
- Metadata-only JWT/header check showed the token key ID does not match the key ID in the current VPS1 Connect credentials file.

## 2026-07-07 Credentials File Replacement And Cache Reset

- Replaced `/opt/openclaw/1password-connect/1password-credentials.json` with the matching credentials file supplied by Jack.
- Backup created:
  - `/opt/openclaw/1password-connect/1password-credentials.json.bak-victor-connect-token-20260707T224936Z`
- Restarted `1password-connect-api` and `1password-connect-sync`.
- The old local Connect data volume had a different local account UUID and failed with a SQLite foreign-key error.
- Backed up and recreated the local cache volume.
- Cache backup created:
  - `/opt/openclaw/1password-connect/1password-data-volume-backup-20260707T225049Z.tgz`
- Updated Victor's helper default host from fragile IP `http://172.18.0.3:8080` to Docker DNS name `http://1password-connect-api:8080`.
- Verified `vaults` succeeds from Victor and returns vault metadata.

## Current Status

- Resolved.
- Ongoing verification command:

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
