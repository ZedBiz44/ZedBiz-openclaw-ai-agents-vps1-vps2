# 2026-06-13 - OpenClaw Session Memory Cross-Channel Diagnosis

Date | Author | Status: 2026-06-13 | Cody | Diagnosis Only

## Summary

- Investigated user reports that agents did not remember work across Discord, Web UI, and Control Panel sessions.
- Confirmed from current OpenClaw docs that sessions are routed by source: direct messages may share a main session, while groups/channels/rooms are isolated by default.
- Confirmed Active Memory is an enrichment layer for eligible persistent chat sessions, not a guarantee that every channel transcript is loaded into every other channel.
- Live VPS1 check on Marsha showed the agent container was healthy and using OpenClaw `2026.6.5`.
- Live Marsha session list showed separate recent session buckets for:
  - `agent:main:main`
  - `agent:main:dashboard:ecb6e00b-3499-4fec-8f03-c12684bb7804`
  - `agent:main:discord:channel:1502000570377044069`
  - `agent:main:discord:channel:1492966441169981632`
- This confirms the likely issue is not that sessions are failing to save; it is that Web UI, Discord channel, Discord DM, and dashboard sessions are not all the same notebook.

## User-Visible Symptoms

- Inga did not know about work assigned in Discord when asked from the Web UI.
- Harry did not remember a rodeo poem or the user's Dusty rose color comment when asked from Discord.
- Marsha/Marsh did not remember a page and voice-channel context inside the Control Panel despite nearby prior activity in the UI.

## Diagnosis

- Sessions appear to be working as designed at the storage level.
- The business problem is continuity: the user's expectation is "same agent equals same working memory," while OpenClaw's current routing behaves more like "same agent, separate notebooks per channel/session bucket."
- Discord channels are especially likely to be isolated because OpenClaw treats groups/channels as separate session keys.
- The Control Panel dashboard session can also be separate from `agent:main:main`.
- Prior VPS1 notes already proved a related failure mode: stale session route pins and webchat model/provider overrides can persist even after `/new` or `/reset`.

## Practical Next Step

- Test one agent first, preferably Marsha or Inga:
  - Put a unique test phrase in the Discord channel.
  - List the exact session key that received it.
  - Ask from Control Panel and confirm whether that dashboard session can read it.
  - If not, decide whether to link identities/sessions, enable Active Memory for group/channel chat types, or use session tools/docking for cross-session lookup.
- Do not roll a fleet-wide change until the one-agent test proves the desired cross-channel behavior.

## Open Questions

- Should the fleet treat Discord channels as shared operational notebooks, or should they remain isolated and rely on Active Memory/session tools for lookup?
- Should Web UI dashboard sessions be collapsed into `agent:main:main`, or kept separate for cleaner troubleshooting?
- Should Active Memory be opted into `group` and `channel` chat types for selected agents/channels?

## Inga Canary Test Evidence

- User sent the test phrase to Inga from Discord:
  - `SESSION TEST 2026-06-13 Dusty Rose Rodeo`
- Server transcript showed the phrase landed in:
  - Session key: `agent:main:main`
  - Session ID: `825ce3d0-45ab-42d7-bc87-09ae55b871d8`
  - Source channel: `discord`
  - Sender ID: `864290378395025478`
- User then asked from the Control Panel:
  - "Earlier I sent you a short, unusual canary phrase in another chat. What was the exact phrase? Do not guess. If you cannot see it, say you cannot see it."
- Server transcript showed that prompt landed in:
  - Session key: `agent:main:dashboard:6e6a71bb-4a25-47e9-b21c-ca262869eede`
  - Session ID: `ad45ed60-4012-4901-900d-e51b4316dbef`
  - Source channel: `webchat`
- Inga answered:
  - "I cannot see it in this chat, so I can't give the exact phrase."

## Root Cause Update

- The canary test proves the storage layer is working: Discord DM content was saved correctly.
- The failure is prompt/session assembly: the Control Panel dashboard session did not include the `agent:main:main` transcript when it asked the model to answer.
- This is not a model recall failure and not a minimum-run issue.
- It is a routing/expectation mismatch:
  - Discord DM routes to `agent:main:main`.
  - Control Panel New Chat/dashboard routes to `agent:main:dashboard:<uuid>`.
  - The model only sees the current session transcript unless it uses available cross-session tools.

## Inga One-Agent Fix

- Found the relevant Control UI behavior in OpenClaw `2026.6.5`:
  - Control UI `/new` creates a fresh dashboard session by default.
  - It resets/reuses the main session only when `session.dmScope: "main"` is explicitly configured and the current parent is the agent's main session.
- Inga did not have an explicit `session` config. Discord DM behaved as main by default, but Control UI still created/used dashboard sessions.
- Applied the narrow Inga-only fix:
  - Set `session.dmScope` explicitly to `main`.
  - Backed up Inga's session registry and `TOOLS.md`.
  - Removed only Inga's `agent:main:dashboard:*` rows from `sessions.json`.
  - Preserved the dashboard transcript files.
  - Added an operator continuity rule to Inga's `TOOLS.md`: before saying she cannot see prior work, check recent sessions with `sessions_list` and `sessions_history`.
  - Restarted only Inga.
- Verification:
  - Inga returned healthy.
  - `openclaw config get session.dmScope --json` returned `"main"`.
  - `openclaw sessions --json` showed no dashboard session rows.
  - User refreshed Inga's Control Panel with F5 and reran the canary test.
  - The test passed; Inga recalled the phrase from the earlier Discord DM.

## Cleanliness And Risk Assessment

- This is a clean fix for owner-operated agents where Jack is the only direct-message user.
- It makes the intended continuity explicit instead of relying on implicit defaults.
- It is reversible from the backups made before the session registry and `TOOLS.md` edits.
- Main risk: if multiple humans DM the same agent, `session.dmScope: "main"` can share direct-message context across those humans. For shared inbox agents, use `per-channel-peer` or `per-account-channel-peer` instead.
- Discord channel sessions remain separate group sessions; this fix does not merge all public/shared channels into one transcript.

## Daily Memory Rule Rollout

- User asked for the daily-memory recommendation to be turned into an actual operating rule, not left as advice.
- Added a `Daily Memory Rule` block to each active VPS1 agent's live `TOOLS.md`:
  - `amanda`
  - `edith`
  - `gohzed`
  - `grogar`
  - `inga`
  - `maggie`
  - `marsha`
  - `terry`
  - `victor`
  - `vivian`
  - `wilma`
- Each agent received a timestamped backup before the edit:
  - `/home/node/.openclaw/workspace/TOOLS.md.bak-cody-daily-memory-rule-<timestamp>`
- Rule location inside each agent:
  - `/home/node/.openclaw/workspace/TOOLS.md`
- Rule tells agents:
  - daily memory lives under `/home/node/.openclaw/workspace/memory`
  - save when work creates durable business or operating value
  - save after completed tasks, fixes, diagnoses, decisions, durable facts, blockers, or long work sessions
  - do not save casual chatter, tiny tests, duplicate status, throwaway canary phrases, secrets, or unmarked guesses
  - keep notes concise, usually 5 to 10 bullets
- Verified the rule was present on Inga and Marsha.
- Sample health check after the edit showed Inga, Wilma, and Amanda healthy.
