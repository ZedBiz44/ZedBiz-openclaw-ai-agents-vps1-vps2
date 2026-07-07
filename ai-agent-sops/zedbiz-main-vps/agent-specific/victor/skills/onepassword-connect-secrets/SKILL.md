---
name: onepassword-connect-secrets
description: Use Victor's VPS1 1Password Connect API route to create, inspect, and update agent secrets without the desktop-only 1Password MCP workflow.
metadata:
  short-description: Manage agent secrets through 1Password Connect
---

# 1Password Connect Secrets

Date: 2026-07-07 Mountain Time | Agent Name: Cody | Status: Testing

## Purpose

Use this skill when Victor needs to create, inspect, or update ZedBiz agent secrets through the VPS1 1Password Connect API.

This replaces the desktop-app 1Password MCP workflow for Victor. Victor is a headless Docker agent, so use the local Connect REST API instead.

## Connection

- Connect API URL from Victor: `http://1password-connect-api:8080`
- Token file inside Victor: `/home/node/.openclaw/credentials/1password-connect-token`
- Helper script: `/home/node/.openclaw/skills/onepassword-connect-secrets/scripts/op_connect.py`
- The helper also accepts `OP_CONNECT_HOST`, `OP_CONNECT_TOKEN`, `ONEPASSWORD_CONNECT_TOKEN`, and `OP_CONNECT_TOKEN_FILE`.

## Guardrails

- Do not print secret values in chat, logs, GitHub, Notion, or terminal summaries.
- Prefer `--value-file` or `--value-stdin` instead of putting secret values directly on a command line.
- Log only safe metadata: vault name or ID, item title, field label, agent, date, status, and test result.
- If the API returns `401`, stop and report that the Connect access token is missing, stale, or scoped incorrectly.
- If a secret change affects an agent, record it in GitHub before summarizing it in Notion.

## Quick Checks

Check Connect health without a token:

```bash
python3 /home/node/.openclaw/skills/onepassword-connect-secrets/scripts/op_connect.py health
```

Check token authentication:

```bash
python3 /home/node/.openclaw/skills/onepassword-connect-secrets/scripts/op_connect.py vaults
```

## Common Workflows

### List Vaults

```bash
python3 /home/node/.openclaw/skills/onepassword-connect-secrets/scripts/op_connect.py vaults
```

### List Items In A Vault

```bash
python3 /home/node/.openclaw/skills/onepassword-connect-secrets/scripts/op_connect.py items --vault VAULT_UUID
```

### Create An Agent Secret Item

Store the secret value in a temporary file with tight permissions, create the item, then remove the temporary file.

```bash
tmp_secret="$(mktemp)"
chmod 600 "$tmp_secret"
printf '%s' "$SECRET_VALUE" > "$tmp_secret"
python3 /home/node/.openclaw/skills/onepassword-connect-secrets/scripts/op_connect.py create-password \
  --vault VAULT_UUID \
  --title "Victor Agent Secret - Service Name" \
  --label "api_key" \
  --value-file "$tmp_secret" \
  --tag zedbiz-agent-secret \
  --tag victor
rm -f "$tmp_secret"
```

### Update One Field On An Existing Item

```bash
tmp_secret="$(mktemp)"
chmod 600 "$tmp_secret"
printf '%s' "$SECRET_VALUE" > "$tmp_secret"
python3 /home/node/.openclaw/skills/onepassword-connect-secrets/scripts/op_connect.py update-field \
  --vault VAULT_UUID \
  --item ITEM_UUID \
  --label "api_key" \
  --value-file "$tmp_secret"
rm -f "$tmp_secret"
```

### Inspect Item Metadata

Default output redacts field values.

```bash
python3 /home/node/.openclaw/skills/onepassword-connect-secrets/scripts/op_connect.py get-item \
  --vault VAULT_UUID \
  --item ITEM_UUID
```

## Verification Standard

- `health` returns the 1Password Connect API service status.
- `vaults` returns vault metadata without `401`.
- For a create or update, re-read the item with default redacted output and confirm the expected title and field label exist.
- Do not claim the secret value itself was correct unless it was tested through the consuming agent or service.

## Rollback

- Remove the skill folder from both:
  - `/home/node/.openclaw/skills/onepassword-connect-secrets`
  - `/home/node/.openclaw/workspace/skills/onepassword-connect-secrets`
- Remove the token file only if Victor should no longer have Connect access:
  - `/home/node/.openclaw/credentials/1password-connect-token`
