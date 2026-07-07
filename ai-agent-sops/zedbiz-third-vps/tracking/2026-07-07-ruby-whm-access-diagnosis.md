# 2026-07-07 - Ruby WHM Access Diagnosis

2026-07-07 | Cody | Status: In Progress

## Summary

- **Date:** 2026-07-07 Mountain Time
- **Agent:** Cody
- **System:** ZedBiz Third VPS / Ruby / WHM API access
- **Change Type:** diagnosis, SOP candidate
- **Status:** in-progress

## What Happened

- Ruby attempted a WHM API call for the `jez44-whm-api` vault item.
- Ruby used the vault item or token label as the WHM API username.
- Ruby also treated a short hostname value as a public DNS hostname.
- The attempted command exposed enough credential shape in chat that the WHM token should be treated as compromised and rotated after access is corrected.

## Diagnosis

- WHM API token authentication requires this header shape: `Authorization: whm <actual-whm-user>:<api-token>`.
- The username is the WHM user that owns the token, normally `root` or a reseller WHM username. It is not the token name and not the 1Password item title.
- A short hostname such as `cdnyrdwr` is not enough for public API access unless it resolves in the current DNS context. Ruby should use the full server hostname or server IP from the vault item.
- If `jez44.com:2087` reaches WHM but returns access denied, that points more toward bad authentication, missing token privileges, IP restriction, or root/reseller access control than toward DNS.

## Proper Instruction For Ruby

- Re-read the 1Password item and identify these separate fields:
  - WHM owner username: `root` or the reseller WHM user.
  - API token: the secret token value.
  - WHM API host: full server hostname or server IP, not the hosted website domain unless explicitly marked as the WHM endpoint.
  - Token name/item name: label only; do not use it as the API username.
- Never paste raw tokens into chat or tracking notes.
- Test DNS first with an available resolver tool such as `getent hosts`, `nslookup`, or Python socket lookup.
- Test the WHM endpoint separately from authentication by checking whether `https://<host>:2087/` responds.
- Test the API using the real WHM owner username and token.
- If authentication still fails, check WHM token privileges and any WHM access/IP restriction before trying random vault tokens.

## SOP Candidate

- Create a reusable WHM/cPanel skill that explains:
  - WHM API versus cPanel UAPI.
  - Port `2087` for secure WHM API calls and `2083` for secure cPanel UAPI calls.
  - Header format differences: `whm <user>:<token>` versus `cpanel <user>:<token>`.
  - How to read 1Password fields without confusing item names, token labels, usernames, hostnames, domains, and short host aliases.
  - A no-secret logging rule for agent chat and tracking files.

## Links

- Notion journal: https://app.notion.com/p/396a3e33d58181379371f9204678f858
- cPanel WHM API tokens documentation: https://api.docs.cpanel.net/whm/tokens
- cPanel API authentication guide: https://api.docs.cpanel.net/guides/guide-to-api-authentication
