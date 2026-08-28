# Google Drive GOG Fleet Activation

Date: 2026-08-28 | Agent: Cody | Status: Software active; Google authorization pending

## Scope

- Audited Google Drive readiness across the sixteen active ZedBiz agents.
- Activated the appropriate Google Workspace software route without connecting an account or granting Drive permissions.
- Kept Ruby on Hermes' native `google-workspace` skill; Ruby does not use OpenClaw's bundled GOG skill.

## Audit Result

- VPS1: Victor alone had a working `gog` binary. The other ten agents had the skill definition but it was ineligible because the binary was absent.
- VPS2: Harry, Frank, and Suzy had GOG v0.19.0 eligible and visible, with no OAuth client credentials or tokens.
- VPS3: Ruby had the Hermes `google-workspace` skill v1.2.0, with no Google token or client credentials.
- VPS4: Rocky had GOG v0.34.1 eligible and visible, with no OAuth client credentials or tokens.

## Changes

- Installed checksum-verified GOG v0.34.1 from the official `openclaw/gogcli` release on VPS1 and VPS2.
- Added a protected wrapper and a persistent, encrypted file-keyring location for each OpenClaw agent.
- Added the GOG bind mount to all eleven VPS1 agent Compose files.
- Enabled `skills.entries.gog.enabled` for the OpenClaw agents.
- Preserved per-agent OAuth/token isolation. No OAuth client JSON, refresh token, service-account key, or keyring password was committed.
- Left Rocky's existing protected GOG installation unchanged.
- Left Ruby's existing Hermes-native Google Workspace skill unchanged.

## Canary And Rollout

- Amanda was the VPS1 canary.
- Amanda reached healthy state with GOG v0.34.1 eligible and model-visible before the remaining agents were changed.
- The remaining VPS1 agents were then updated sequentially.
- VPS2 was upgraded after VPS1 verification.

## Incident And Correction

- The first VPS1 recreation command used bare `docker compose`, which bypassed 1Password injection and passed unresolved `op://` references into recreated containers.
- The error was corrected by rerunning every affected agent through its `op-start-{agent}.sh` wrapper.
- Wilma's live vault is still missing historical WordPress MCP items. Her existing protected `.env.resolved` fallback was used, matching the previously tracked August 26 procedure.
- Final verification found zero unresolved `op://` values in all eleven VPS1 container environments and zero new authentication errors in the checked post-repair logs.

## Verification

- VPS1: all eleven agents running and healthy, zero restarts, not OOM-killed, GOG v0.34.1, skill eligible, skill model-visible, gateway-ready, and no unresolved runtime secret references.
- VPS2: Harry, Frank, and Suzy running; GOG v0.34.1 eligible and model-visible.
- VPS4: Rocky GOG v0.34.1 eligible and model-visible.
- No Google account is connected yet on any audited agent.

## Authentication Recommendation

- For a fast first connection, use one Google Cloud Desktop OAuth client and authorize only Drive.
- Start with `--services drive --drive-scope readonly` for a known-folder read test.
- Upgrade selected agents to full Drive access only when their role needs write, rename, move, or trash actions.
- For a long-term Google Workspace fleet identity, prefer a dedicated ZedBiz automation user or a tightly scoped service account with domain-wide delegation, rather than Jack's personal account.

## Human Gate

- Jack must choose the Google account and access level.
- A Google Cloud project must have the Drive API enabled and a Desktop OAuth client JSON downloaded.
- The JSON must be transferred through a protected channel, never committed to GitHub or pasted into Notion.
- Each target runtime then completes the manual/headless authorization flow and a known-file Drive test.

## Files

- `ai-agent-sops/shared-scripts/install-vps1-gog-fleet.sh`
- `ai-agent-sops/shared-scripts/gog`
- `ai-agent-sops/shared-scripts/verify-vps1-gog-fleet.sh`
- `ai-agent-sops/shared-scripts/install-vps2-gog-fleet.sh`
- `ai-agent-sops/shared-scripts/gog-vps2`

## Rollback

- VPS1 Compose backups were created beside each live Compose file with the `backup-YYYYMMDDTHHMMSS` suffix.
- Restore the newest backup and recreate through the agent's 1Password-aware start wrapper.
- The previous VPS1 GOG binary was backed up in `/opt/openclaw/shared/bin/`.
- The previous VPS2 binary was backed up in `/usr/local/bin/`.

