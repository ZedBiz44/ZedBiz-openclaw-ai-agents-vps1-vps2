---
name: wordpress-mcp
description: Manage authorized WordPress sites through MCP using on-demand bearer tokens from the dedicated 1Password `wordpress-mcp` vault. Use for WordPress reads, drafts, edits, publishing, SEO, media, taxonomy, analytics, and site-management tasks. Never request, reveal, store, or paste bearer tokens in chat, notes, configuration, memory, files, or logs.
---
# WordPress MCP

Use `/home/node/.openclaw/skills/wordpress-mcp/scripts/wp-mcp-1password` for every WordPress MCP action. Do not use bearer-token environment variables, `TOOLS.md`, workspace files, or direct `curl` commands containing a token.

## Safe workflow

- Receive a domain and a clearly authorized action.
- For a new site, run discovery first: `wp-mcp-1password discover <domain>`.
- Read the available tools before choosing a tool call.
- Complete only the authorized action. Draft means draft. Read-only means no write.
- Report the safe result, never the token or service-account details.

## Commands

```bash
# Discover the working standard endpoint and available tools.
/home/node/.openclaw/skills/wordpress-mcp/scripts/wp-mcp-1password discover zedwebhosting.com

# Call a discovered MCP tool.
/home/node/.openclaw/skills/wordpress-mcp/scripts/wp-mcp-1password call zedwebhosting.com wp_get_posts '{"per_page":5}'
```

## Site onboarding rule

A site is ready when the `wordpress-mcp` 1Password vault contains an item named `wp-mcp-key-<domain-with-dashes>` with:

- the bearer token in `credential`
- the site root URL in `url`

Do not add per-site environment variables or restarts. The script derives the standard v2 and v1 MCP URLs from the stored URL and checks them safely. Stop and diagnose when neither succeeds.

## Guardrails

- Do not reveal, print, repeat, write, or request a bearer token.
- Do not call 1Password directly outside the approved script.
- Do not publish, delete, update, install, or change WordPress content unless the user explicitly authorizes that operation.
- Stop when the site item is missing, the URL is blank, the endpoint fails, or 1Password denies access.
- Use the direct service-account workflow only for the dedicated `wordpress-mcp` vault. It is not permission to access other 1Password vaults.
