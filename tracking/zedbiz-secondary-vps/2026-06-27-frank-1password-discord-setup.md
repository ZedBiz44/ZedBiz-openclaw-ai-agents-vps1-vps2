# Frank 1Password Service Account + Discord Setup

Date: 2026-06-27 | Agent: Cody | Status: Final

## Summary

- Rotated Frank's 1Password service-account token on VPS2.
- Confirmed the new token can access both `agent-frank` and `openclaw-agents-shared` vaults.
- Added vault-backed Discord environment references for Frank.
- Enabled Frank's Discord channel bridge and Discord skill in OpenClaw.
- Restricted Frank's Discord guild access to the ZedBiz Agents `#frank` channel.
- Restarted `openclaw-frank` and verified the web gateway and Discord path.

## Live System

- Host: `srv1677638` / VPS2.
- Service: `openclaw-frank`.
- Agent directory: `/opt/openclaw-frank`.
- State directory: `/root/.openclaw-frank`.
- Public endpoint: `https://frank.zbiz.ca`.

## Files Updated

- `/root/.openclaw-frank/.op.token`
- `/root/.openclaw-frank/.env`
- `/root/.openclaw-frank/openclaw.json`

## Config Changes

- `channels.discord.enabled = true`
- `channels.discord.token` uses env secret reference `DISCORD_BOT_TOKEN`.
- `channels.discord.groupPolicy = allowlist`.
- The allowlist is scoped to the ZedBiz Agents guild and the `#frank` channel.
- `plugins.entries.discord.enabled = true`.
- `skills.entries.discord.enabled = true`.

## Verification

- 1Password CLI `whoami` succeeded with the new service account.
- 1Password vault access confirmed for `agent-frank` and `openclaw-agents-shared`.
- Discord API confirmed the bot identity as `frank-openclaw`.
- Discord API confirmed access to channel `#frank`.
- `systemctl is-active openclaw-frank` returned `active`.
- `https://frank.zbiz.ca` returned HTTP 200.
- A Discord test message was sent through Frank's configured bot and read back successfully.
- Test message ID: `1520525937769316472`.

## Backups

- Old 1Password token backup: `/root/.openclaw-frank/.op.token.bak-20260627T142247-0600`.
- Pre-change `.env` and `openclaw.json` backups were created with the `bak-discord-20260627T142437-0600` suffix.

## Security Notes

- No secret values were stored in this record.
- The live token file remains permissioned `600` under root-owned Frank state.
