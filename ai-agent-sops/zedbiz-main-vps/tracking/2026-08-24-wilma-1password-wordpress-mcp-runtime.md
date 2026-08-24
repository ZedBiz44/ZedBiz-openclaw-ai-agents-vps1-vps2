# Wilma 1Password-Backed WordPress MCP Runtime Setup

**Date:** 2026-08-24 MDT  
**Agent:** Manus  
**Status:** Implemented, ready for Jack's one-site functional test

## Purpose

Configure Wilma to retrieve WordPress MCP bearer tokens only when required from the dedicated 1Password `wordpress-mcp` vault. This replaces the need to add a permanent Wilma environment variable and restart her for every new site.

## Implemented

Wilma now has access to the existing host-managed 1Password CLI through a read-only container mount at `/usr/local/bin/op`. The CLI is static and version `2.35.0`.

The `wilma-wordpress` service-account token is resolved from the existing administrator-controlled `agent-wilma` vault item and is stored only in Wilma's locked runtime file:

```text
/home/node/.openclaw/credentials/onepassword/service-account-token
```

The runtime file is mode `600` and owned by Wilma's container user. The service account has verified read access to `wordpress-mcp` and verified denial of the unrelated `agent-wilma` vault.

The tracked `skills/wordpress-mcp` skill now includes `scripts/wp-mcp-1password`. The script accepts a domain, derives the expected `wp-mcp-key-<domain-with-dashes>` item name, reads the site URL and bearer token from the dedicated vault through the official 1Password CLI, and tries the standard v2 then v1 MCP endpoint. It never prints the token.

## Important Correction During Setup

Long 1Password service-account values must be extracted from structured JSON using the exact `credential` field. The CLI's abbreviated field-output mode returned only a short portion of the long token, which caused an initial false authentication failure. The final deployment uses the full structured field and verified the runtime copy by hash without revealing the value.

## Verification Completed

| Check | Result |
|---|---|
| Pre-change backup | Created at `/opt/openclaw/agents/wilma/backups/20260824-124439-MDT-pre-wordpress-1password/` |
| Wilma container health | Healthy after restart |
| 1Password CLI | Available in Wilma, version `2.35.0` |
| Credential file | Mode `600`, owned by `node:node` |
| `wordpress-mcp` item read | Passed without printing token values |
| `agent-wilma` vault access by Wilma service account | Denied as expected |
| WordPress skill script | Syntax checked successfully |
| WordPress HTTP calls by Manus | Zero |

## Jack's Functional Test

Jack should ask Wilma to perform a harmless discovery or read on `zedwebhosting.com`. The expected workflow is that Wilma uses the `wordpress-mcp` skill, finds `wp-mcp-key-zedwebhosting-com`, checks the available MCP tools, and reports the safe result without displaying any credential.

Do not test with a post creation, update, publish, delete, plugin, theme, database, or settings action first.

## Rollback

If Wilma becomes unhealthy or the implementation must be removed, restore the backup above, remove the read-only `/usr/bin/op` mount from Wilma's Compose configuration, and restart with `/opt/openclaw/agents/wilma/op-start-wilma.sh restart`. Revoke the `wilma-wordpress` service account only if the service-account token may have been exposed.
