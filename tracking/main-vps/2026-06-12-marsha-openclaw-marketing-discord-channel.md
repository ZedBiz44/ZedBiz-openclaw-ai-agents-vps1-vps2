# 2026-06-12 - Marsha OpenClaw Marketing Discord Channel Access Fix

Date | Author | Status: 2026-06-12 | Cody | Completed

## Summary

- Fixed Marsha's Discord read access for the new `#openclaw-marketing` channel.
- Root cause was not the Discord role/member permission screen alone.
- Marsha's OpenClaw Discord connector was still configured with `groupPolicy: allowlist` and only allowed her original `#marsha` channel.
- Added the new channel ID `1515133129743007755` to Marsha's allowed channel map under the existing ZedBiz Agents guild.
- Restarted only the `marsha` container.
- Verified Marsha remained healthy and resolved both Discord channels at startup.
- Verified direct read access to `#openclaw-marketing`.
- Sent a visible confirmation message from Marsha into the channel.

## Live Server

- VPS1: `187.77.210.223`
- Container: `marsha`
- Guild: `ZedBiz Agents`
- Guild ID: `1491589465175621794`
- Existing Marsha channel ID: `1492966441169981632`
- New marketing channel ID: `1515133129743007755`

## Diagnosis

- Marsha was online and her container was healthy.
- Discord logs showed Marsha only resolving:
  - `1491589465175621794/1492966441169981632`
- OpenClaw message actions against the new channel failed with:
  - `Discord read target channel is not allowed`
- Runtime config showed:
  - `channels.discord.groupPolicy = allowlist`
  - `channels.discord.guilds[1491589465175621794].channels` only contained `1492966441169981632`

## Fix Applied

- Backed up Marsha's runtime config before changing it:
  - `/home/node/.openclaw/openclaw.json.bak-openclaw-marketing-channel-2026-06-12T23-53-25-372Z`
- Added:
  - `channels.discord.guilds[1491589465175621794].channels[1515133129743007755] = { enabled: true }`
- Restarted only Marsha.

## Verification

- Marsha returned to healthy state after restart.
- Startup logs showed both channels resolved:
  - `channel:marsha`
  - `channel:openclaw-marketing`
- Direct read test succeeded against:
  - `openclaw message read --channel discord --target channel:1515133129743007755 --limit 3 --json`
- The read test returned recent messages from Vivian, Maggie, and Inga in `#openclaw-marketing`.
- Direct send test succeeded and created Discord message:
  - `1515142534102384730`
- Post-send logs showed successful Discord message actions and no new `read target channel is not allowed` errors.

## Operating Note

- For private or allowlisted shared Discord channels, Discord-side role/member access is necessary but not always sufficient.
- Each OpenClaw agent with `groupPolicy: allowlist` also needs the channel ID added to its own `channels.discord.guilds.<guildId>.channels` map.
- If a channel was added while the agent already had an active Discord session, restart the affected agent or reset the stale channel session after updating the allowlist.

## Follow-Up: Standardize Marsha With The Fleet

- Compared VPS1 Discord configs across the active fleet.
- Found Marsha was the only active VPS1 agent using `channels.discord.groupPolicy = allowlist`.
- Other active agents use `groupPolicy = open` or unset/default group policy, with no per-channel allowlist entries.
- Changed Marsha to match the rest of the fleet:
  - `channels.discord.groupPolicy = open`
  - cleared the explicit per-channel map under the ZedBiz Agents guild
- Backup created before this change:
  - `/home/node/.openclaw/openclaw.json.bak-marsha-discord-group-open-2026-06-13T00-08-00-965Z`
- Restarted only Marsha.
- Verification after restart:
  - Marsha container remained healthy.
  - Runtime policy showed `groupPolicy: open`.
  - Runtime channel allowlist was empty.
  - Direct read test against `#openclaw-marketing` succeeded.
  - Direct send test succeeded with Discord message ID `1515146141824712925`.
  - No fresh `Discord read target channel is not allowed` errors appeared.
