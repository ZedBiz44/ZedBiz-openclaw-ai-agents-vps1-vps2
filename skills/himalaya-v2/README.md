# VPS1 Himalaya 2 compatibility guide

Owner: ZedBiz. Scope: the eleven OpenClaw agents on VPS1. Cody maintains this repository-owned compatibility guide; it is not a public skill release.

Deploy only SKILL.md into the existing workspace `skills/himalaya/` directory. The runtime name deliberately remains `himalaya` to replace the bundled version-1 guide through OpenClaw workspace precedence. This is the platform mapping for the existing skill, rather than a new public ZedBiz identifier.

Adapted from the reviewed ZedBiz VPS4 implementation in PR 58 and verified against the installed Himalaya 2.2.1 help. No upstream implementation code or credentials are embedded.

Sources:
- https://github.com/pimalaya/himalaya/blob/v2.2.1/MIGRATION.md
- https://github.com/pimalaya/himalaya/blob/v2.2.1/config.sample.toml

Operational scope: account checks, authorized reads and local unsent drafts. Sending and mailbox changes require explicit matching authorization. Tests use protected agent credentials, never print mail bodies, preserve message flags and never send mail.

Rollback: restore the saved version-1 binary mount, configuration and complete skill directory together, then recreate the agent through its existing `op-start-<agent>.sh up` wrapper so 1Password references are resolved. The version-1 binary is retained in the protected maintenance directory after the host upgrade; point the rollback mount there. Edith previously had no Himalaya configuration; her rollback removes only the newly created configuration. The migration record owns deployment hashes, approval and live test receipts.
