# Built-in Notion access for Terry and Harry

Date: 2026-09-24 | Author: Cody | Status: Live verified; source PR awaiting merge

## Result
Both agents can read and write Notion using the bundled OpenClaw notion skill and official ntn CLI while running outside Codex. Fresh Gateway-routed tests used Terry/DeepSeek V4 Pro and Harry/Kimi K2.6 with no model fallback. Existing Codex Apps access and model defaults were preserved.

## Authorized scope and implementation
Jack requested ongoing secondary access, explicitly selected the built-in skill, and completed each agent's separate browser login.
- Enabled only skills.entries.notion.enabled on both agents.
- Native route uses saved ZedBiz Notion CLI login, owned by ZedBiz Admin (admin@zedbiz.com).
- Terry credential home: /home/node/.openclaw/notion-cli, within the existing persistent config bind mount.
- Harry credential home: /root/.openclaw-harry/notion-cli.
- Directories are 0700 and files 0600, owned by each actual runtime user.
- Native CLI prefix is env -u NOTION_API_TOKEN NOTION_KEYRING=0 NOTION_HOME=<agent credential home> ntn. Terry has an obsolete injected token; excluding it prevents it overriding the valid saved login.
- No secret values are in this record, configs committed here, prompts, or source files.
- No new MCP service, custom skill, model change, service restart, account switch, or unrelated integration change.
- The initially prepared notion-native MCP entry was removed when Jack selected the bundled skill.

## Preservation register and source comparison
Retained all role, identity, reporting, operating modes, approval, publishing, privacy, security, Asana, memory, media, source-of-truth, and final email-trigger rules.
Replaced only Codex-exclusive Notion routing with approved runtime-specific routing.
Codex sessions retain Codex Apps; native sessions use bundled notion and saved CLI login.
Both routes retain the same permission, publishing, and governance limits; never switch routes to bypass a denied action.
Terry legacy TOOLS.md's contradictory Notion section was amended; other tool notes retained.
Harry's Notion Page Creation reference now points to the live routing section rather than absent TOOLS.md.
No unrelated instructions relocated, deleted, or consolidated.
Both live AGENTS baselines matched GitHub main substantively; one carriage-return-only blank line differed.
Terry TOOLS.md was absent in source and is now recorded from the actual live file with the narrow Notion edit.

## Candidate and live evidence
| Agent | Baseline SHA256 | Final live SHA256 | UTF-16 chars | Injection |
|---|---|---|---|---|
| Terry | be852f2cce674e9efbdd7ca44ffd3eed105743021d6911098c9cefe51d0bdbc0 | 067fe314ec05f2cd90a82e5dc0bf556dd187a21eb2231db675109140159de00f | 16825 to 17841 | 17840 trimmed chars injected; truncated=false; limit 20000 |
| Harry | c73d2d75c9e5c455c393fed84cb3d98928a7b86da48add30dd5dbfe7496893aa | 2a51e22c2458c8d987f09fceb917ca7a0ee6806c8bf783ee891136472ccc2d24 | 14605 to 15677 | 15676 trimmed chars injected; truncated=false; limit 24000 |

The installed AGENTS analyzer passed size limits and found no duplicate headings. Both files remain above the preferred 14000-character recommendation; this bounded routing repair preserves unrelated instructions rather than shortening them. Runtime injection evidence proves the complete final files were loaded.
Terry TOOLS.md live SHA256: e395a8cc5d8dfc3404da731eaa9d47f176abfac067c1e1aaae83f53cbd596a8c.
Independent before/after configuration comparisons, excluding only the intended notion skill entry and managed metadata, were equal on both hosts.
Terry running/healthy with restart count 0. Harry active/running with NRestarts=0.

## Real model acceptance
Source: https://app.notion.com/p/3e5a3e33d58180ba9cd5d9523798f83d
Journal: https://app.notion.com/p/3e5a3e33d58181bb99d9c94da7355551
- Terry fresh DeepSeek V4 Pro session: verified workspace identity, opened actual source, returned its title and headings, wrote/read journal marker. Eight tool calls, zero tool errors, no fallback. Role, review-only publishing boundary, and final-section Asana comment-notification guard passed.
- Independent QA caught one dropped page mention from Terry's first whole-page Markdown edit despite his preservation claim. Restored that exact mention and added a standing append-only rule for small additions.
- Terry fresh repeat: native blocks PATCH appended TERRY-NTN-20260924-B; read-back confirmed marker and source mention. Seven tool calls, zero tool errors, no fallback. Independent raw-JSON comparison confirmed all 14 pre-existing blocks unchanged and exactly one paragraph added.
- Harry fresh Kimi K2.6 session: verified identity and real source title/headings, appended HARRY-NTN-20260924-A with blocks PATCH and read it back. Seven tool calls, zero tool errors, no fallback. Role, paid-campaign approval gate, and final-section Asana notification guard passed.
- Independent Harry comparison confirmed all 19 pre-existing blocks unchanged and exactly one paragraph added. Harry's narrative incorrectly counted 14 initial blocks; the actual tool data and independent comparison establish 19.
- Neither reviewer feedback page was read or written, and no business review was performed. No channel messages sent.
- Existing main-chat model overrides were not reset. Use a fresh chat for the next review to load updated instructions and skill discovery.

## Persistence, backup and rollback
Terry originals and test evidence: /home/node/.openclaw/backups/notion-secondary-20260924/.
Harry originals and test evidence: /root/.openclaw-harry/backups/notion-secondary-20260924/.
Live hashes were rechecked immediately before deployment; ownership/modes preserved.
Terry auth move initially encountered a cross-filesystem rename limitation; copied to the protected persistent home instead. Original temporary login files were also permission-restricted.
Rollback restores AGENTS/TOOLS originals and the prior notion skill enablement only; preserve unrelated concurrent changes. No rollback required after final successful tests.
Credentials survive process restart and Terry container replacement through existing persistent storage; no disruptive restart was performed merely to test persistence.

## Operational limits
The native CLI route does not imply parity with Codex AI content search. Use API search/query capabilities and verify returned sources. Read/write tests covered the named source and setup journal, not every database operation or every model.
Normal Notion account permissions still apply. Renewal may be needed if authorization is revoked or expires; do not promise permanent login.
Installed ntn 0.22.12 uses pages edit rather than the newer pages update example in the bundled skill. Follow live help; append additions via blocks API and preserve unknown/truncated content on replacements.

## Source and tracking
Issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/400
PR: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/401
