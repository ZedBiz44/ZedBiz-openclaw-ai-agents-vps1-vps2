# VPS1 Himalaya email migration

Date: 2026-10-03 | Agent: Cody | Status: Fleet rollout in progress

## Authorization and scope

Jack approved completing the remaining VPS1 compatibility work after the prior maintenance pass. The migration targets Himalaya 2.2.1 on Terry first, followed by the other ten agents after the pilot. Existing model defaults remain ten GPT 6.1 Sol agents and Marsha on GPT 6 Astra, all through Codex OAuth. Sending email was not authorized and is excluded from testing.

## Implementation

- Verify the official release asset SHA256 before installation. Retain the host's 1.2.0 binary and use `/opt/openclaw/shared/bin/himalaya-2.2.1` as the new container bind-mount source.
- Migrate each account's existing configuration into the v2 IMAP, SMTP and mailbox-alias schema. Preserve TLS, account identity and protected command-based credential retrieval. Resolve sender-address placeholders for draft composition.
- Edith's existing account credentials were present, but her Himalaya config was missing. Build her configuration from those same protected account settings and verify it before activation.
- Replace the existing `himalaya` workspace guide with the reviewed v2 compatibility guide. Move the full old skill into `workspace/backups/email-migration-20261003/himalaya-v1` so obsolete configuration and composition references are outside skill discovery.
- Preserve the rest of each agent's instructions. Existing main-file `message write` and `message reply` commands remain recognized v2 commands; the loaded skill explains unsent draft behavior and explicit sending authority.
- Recreate each agent separately using its existing Compose project, preserving all other image, model, auth and service settings.

## Checks and recovery

All eleven candidate accounts passed IMAP and SMTP authentication, mailbox and envelope listing, reading an existing message without changing flags, and local unsent draft composition with the correct sender. No test message was sent or saved to a mailbox. Private message bodies are parsed in memory and excluded from published evidence.

Native OpenClaw and central ZedBiz runtime skill validation passed. The first validator invocation used a user unable to traverse the protected maintenance directory; rerunning with the scoped helper's root user passed. The first test parser incorrectly expected a top-level envelope array; v2 returns an `envelopes` array inside an object, and the corrected parser passed.

Terry's first recreation encountered a five-minute stale gateway owner lease after the Docker shell failed to forward graceful shutdown. The old container was gone; no database locks were manually rewritten. Subsequent activation explicitly signals the verified gateway owner process and allows it to release ownership before recreating its container.

The first activation also used plain Compose instead of the existing `op-start-<agent>.sh up` wrapper. This left `op://` references unresolved and failed the live email authentication check. Corrected the activation script to use the established 1Password wrapper and assert that email environment values are resolved. Wider rollout remains gated on Terry's live agent proof after this repair.

Protected configuration and Compose backups are under `/opt/openclaw/builds/vps1-email-20261003/<agent>/`. Restore the saved Compose file, v1 config and old skill together to roll back an agent. Edith's prior state had no config. The old host binary and original images remain available.

## Mem0 compatibility review

The installed Mem0 plugin 1.2.1 is the latest published plugin. Its installed SDK is 3.0.7. The latest SDK, 3.3.1, was downloaded separately for source inspection; its Qdrant adapter still calls `this.client.search(...)`. Qdrant client 1.19.0 removes that API. Therefore the verified 1.18.0 client remains required, and no untested SDK override was deployed. The Qdrant server itself remains 1.19.1. Existing memory recall is rechecked after each restart.

The custom knowledge retention, Notion routing and approved project rules remain preserved. They are intentional local behavior, not unfinished email migration work.

## Records

- [Official migration guide](https://github.com/pimalaya/himalaya/blob/v2.2.1/MIGRATION.md)
- [Official v2 configuration](https://github.com/pimalaya/himalaya/blob/v2.2.1/config.sample.toml)
- [Technical issue](https://github.com/ZedBiz44/ZedBiz-general-tech-issues-updates/issues/94)
- [Source review](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/437)
