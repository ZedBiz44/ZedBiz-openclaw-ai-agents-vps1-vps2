# Native Notion pilot - Terry and Harry

Date: 2026-09-24 | Author: Cody | Status: Terry candidate committed; pilot pending

## Authority and scope
Jack requested secondary access outside Codex, selected the built-in OpenClaw Notion skill, and completed Terry's Notion CLI login. Pilot Terry first, then Harry after proof. Preserve model choices, existing Codex Apps access, existing approval boundaries, and unrelated services.

## Preservation register
- Retain: role, identity, reporting, authority, Diagnose/Get-er-Done modes, safety, security, publishing, privacy, Asana identity, media gates, memory, source-of-truth, email triggers, final-section instructions.
- Replace: Notion-only Codex restriction with runtime-specific routing. Codex uses Codex Apps; native models use bundled notion skill and official ntn.
- Retire: automatic requirement to change native models to Codex to perform Notion work. Superseded by Jack's explicit secondary-access request.
- Amend: matching legacy TOOLS.md Notion restriction to prevent conflicting guidance. No other tool-note edits.
- No instructions relocated or unrelated rules removed.

## Source comparison
Live Terry AGENTS matches GitHub main's substantive lines; one carriage-return-only blank line differs. Canonical source agents/terry/AGENTS.md. TOOLS.md was absent at that repository path and is added from the current live file with the narrow Notion correction.

## Candidate analysis
Baseline SHA256 be852f2cce674e9efbdd7ca44ffd3eed105743021d6911098c9cefe51d0bdbc0; 16833 UTF-8 bytes, 16825 UTF-16 units, 192 lines.
Candidate SHA256 e539748c92fb1bf5d2c180ef2d1e48c971057c071f2a7ace876a0e4b3ba4006f; 17510 bytes, 17502 UTF-16 units, 194 lines.
Installed analyzer run on both files; no duplicate headings; final email-rule marker retained.
Both exceed the preferred 14000 characters but remain below the 20000 default per-file limit; live config has no override. This is intentionally a narrow routing repair, not an unrelated instruction-shortening exercise. Require fresh-session behavior/injection evidence.

## Credentials and runtime
Official ntn 0.22.12 is already installed and bundled notion skill exists but was disabled. CLI login verified workspace ZedBiz Notion through users/me.
Terry's obsolete NOTION_API_TOKEN environment value overrides saved CLI auth. Native route explicitly removes that variable for each ntn command; no token values are printed or stored in GitHub.
Credential home: /home/node/.openclaw/notion-cli, in existing persistent config bind mount. Directory 0700; files 0600; runtime owner node/1000. No additional service or Notion MCP needed.
Native command prefix: env -u NOTION_API_TOKEN NOTION_KEYRING=0 NOTION_HOME=/home/node/.openclaw/notion-cli ntn.
CLI uses pages edit; bundled skill's pages update example is newer than installed CLI, so instructions require command help.
The attempted initial rename into persistent storage hit EXDEV; copied to the protected destination instead. Original login directory was already protected. No credential content recorded.
The earlier temporary notion-native MCP entry was removed after Jack selected the bundled skill.

## Deployment and rollback
Candidate and original files are staged outside the workspace at /home/node/.openclaw/backups/notion-secondary-20260924/{before,after}/.
Before deploy, verify original hashes, preserve file owner/mode, back up current config, and enable only skills.entries.notion.
Rollback restores those original files and prior skill entry; preserves unrelated concurrent changes. No gateway restart expected.
Fresh DeepSeek session must read real source content, append one marked verification note to the setup journal and read it back; preserve review content. Verify role, authorization boundary and tail email rule. Do not treat CLI-only proof as model proof.
Harry remains untouched until Terry passes and needs his own account authorization.

## Tracking
https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/400
