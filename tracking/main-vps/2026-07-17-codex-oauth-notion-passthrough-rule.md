# Codex OAuth Notion Passthrough Rule

**Date:** 2026-07-17 Mountain Time
**Verified by:** Jack
**Recorded by:** Cody
**Status:** Confirmed

## Guide Name

- ZedBiz AI Agent Documentation Instructions (`AGENTS.md`)

## Broken Or Unclear Step

- Terry's inability to create a Z-Knowledge entry was diagnosed by testing the standalone `openclaw` Notion integration.
- That test was incorrectly treated as proof of Terry's actual Notion permissions.

## Old Assumption

- Agent Notion access depended on the standalone `NOTION_API_TOKEN` and resources being shared with the `openclaw` integration.

## Confirmed Correction

- ZedBiz agents access Notion through the Codex OAuth passthrough.
- This route gives the agents the same full Notion access available to Cody.
- The standalone Notion integration is not the authoritative test for agent Notion access.
- Future Notion access diagnoses must verify the Codex OAuth passthrough and whether the agent actually used it before checking any standalone integration token.

## Verification

- Jack directly confirmed the intended authentication and access architecture on 2026-07-17.
- Jack reset Terry's LLM dropdown to GPT-5.6, then issued `/new` and `/restart` to clear the old conversation state.
- Cody verified Terry's replacement session is running `openai/gpt-5.6-sol` with a valid Codex OAuth profile.
- Cody verified the fresh session loaded the Codex Apps connector cache and began checking live Notion through the Codex connector route.
- The older session that used the standalone `ntn` path is recorded as killed/aborted; the replacement GPT-5.6 session is running.
- The replacement session still selected `/app/skills/notion` and `ntn`, proving the root cause was the installed instruction route rather than the LLM selection or OAuth validity.
- The canonical `zedbiz-notion-knowledge-publishing` skill was updated to require Codex Apps Notion tools through the Codex OAuth passthrough and forbid silent fallback to `ntn`.
- A clean Terry test fetched the formerly blocked Content-Master-Databases page through `codex_apps.notion.fetch` with zero tool failures.
- The corrected skill was deployed to both installed skill locations for Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma, and to the shared rollout-master copy.
- Terry then created and live-verified `LegalShield-Canada-Personal-Plan-Research` in the Research data source through the Codex OAuth passthrough.
- Final LegalShield page: https://app.notion.com/p/3a0a3e33d5818101b3d1c41457ad4dc4
- Research data source ID: `92c48a76-aba2-49e6-b5a8-e8e2ce0765e4`
- Terry's stale Mem0 blocker was corrected to state that sharing with the separate `openclaw` integration is not required.
- Fresh standard wiki lint: 0 errors and 86 existing warnings; neither LegalShield file was named.
- Fresh ZedBiz custom frontmatter lint: 96 existing fleet-wide errors; neither LegalShield file was named.
- Canonical skill source commit: https://github.com/ZedBiz44/zedbiz-notion-knowledge-publishing-skill/commit/eac640b

## Files Changed

- `AGENTS.md`
- `tracking/main-vps/2026-07-17-codex-oauth-notion-passthrough-rule.md`

## Rollback Note

- Remove the `Notion Authentication And Access` section only if Jack explicitly changes the fleet's Notion authentication architecture.
