# 2026-06-12 - Notion Access Diagnosis For Amanda, Inga, Gohzed, Maggie, And Marsha

Date | Author | Status: 2026-06-12 | Cody | Fixed And Verified

## Summary

- Investigated why Amanda, Inga, Gohzed, Maggie, and Marsha cannot access Notion.
- Found all five containers are running and healthy.
- Found Amanda, Inga, Gohzed, and Maggie were still using legacy `codex/gpt-*` model refs and legacy `openai-codex:*` auth profile routing.
- Found Marsha already had the newer `openai/gpt-*` model config, but her failed workflow was still tied to stale session/runtime state.
- Compared against Terry, which does have both `asana` and `notion` configured at the MCP layer.
- Found Terry's active Notion MCP block was pointing at an invalid stale Notion token.
- Found a valid `NOTION_API_KEY` already present in each agent's runtime environment.
- Added a plain Notion MCP server to Amanda that references `NOTION_API_KEY` instead of embedding the stale token.
- That only proved Amanda can access some Notion content through the plain Notion API.
- Amanda still cannot complete the user's real Biz Brain page workflow because that route cannot see the target page.
- Working agents use `codex_apps.notion_fetch` and `codex_apps.notion_notion-update-page`, not the plain `notion.API-*` route.
- Correct fix was to repair the Codex runtime route so the agents receive the Codex Apps Notion connector tools.
- Applied `openclaw doctor --fix` to Amanda first, verified the exact user workflow, then applied the same repair to Inga, Gohzed, Maggie, and Marsha.
- All five affected agents now successfully accessed and wrote to the target Notion page using the Codex Apps Notion connector tools.

## Live Agents Checked

- `amanda`: healthy, MCP servers: `asana`
- `inga`: healthy, MCP servers: `asana`
- `gohzed`: healthy, MCP servers: `asana`
- `maggie`: healthy, MCP servers: `asana`
- `marsha`: healthy, MCP servers: `asana`

## Diagnosis

- This was not a simple expired OpenAI Codex OAuth problem.
- The OpenAI Codex OAuth profile exists in the five named agents.
- The Notion API key also exists and validates successfully in runtime.
- The plain Notion MCP route is not enough for the user's target page.
- Amanda's exact workflow test against the Biz Brain page returned `object_not_found`, with Notion saying the page must be shared with the `openclaw` integration.
- The working agents' traces show they used the OpenClaw app connector tools:
  - `codex_apps.notion_fetch`
  - `codex_apps.notion_notion-update-page`
- The failing agents' traces do not show those `codex_apps.notion_*` tools.
- Corrected diagnosis: the failed agents were not receiving the Codex Apps Notion connector tool surface used by the working agents because their Codex route/session state was legacy or stale.
- OpenClaw's Codex harness docs state that legacy `codex/gpt-*` refs should be migrated to canonical `openai/gpt-*` refs and that `openclaw doctor --fix` repairs legacy refs and stale session route pins.
- For this workflow, the "Notion doorway" is the Codex Apps connector surface exposed inside Codex-backed turns, not a manually configured Notion MCP server in `mcpServers`.

## Comparison

- Terry is the known-good reference checked during this diagnosis.
- Terry's OpenClaw MCP layer includes both `asana` and `notion`.
- The five affected agents only include `asana`.
- Terry's existing Notion MCP block used a stale embedded token and returned `401 unauthorized`.
- The valid pattern is to use the runtime `NOTION_API_KEY`, which returned `200 OK`.

## Amanda Tests

- Backed up Amanda's OpenClaw config.
- Added a `notion` MCP server to Amanda using:
  - `/usr/local/bin/npx`
  - `@notionhq/notion-mcp-server`
  - `OPENAPI_MCP_HEADERS` built from `NOTION_API_KEY`
- Reloaded Amanda's MCP runtime.
- Verified Amanda's direct Notion API search returned `200 OK`.
- Verified `openclaw mcp probe notion` returned 22 tools.
- Ran a read-only Amanda agent-runtime test.
- Amanda replied: `NOTION_OK Technical Documentation`.
- Runtime trace showed one Notion tool call and zero failures.
- Amanda stayed healthy.
- Ran the user's exact Biz Brain page workflow against Amanda.
- Amanda failed with `object_not_found` because the plain Notion API integration cannot see that page.
- Tested an app-connector alignment experiment by temporarily changing Amanda's auth route to the working `openai:jzedbiz@gmail.com` profile and removing the plain Notion MCP detour.
- Even after a fresh session and an Amanda container restart, Amanda still did not receive `codex_apps.notion_*`.
- The auth-alignment experiment was reverted to the backup taken before that change.
- Removed the plain Notion MCP detour again to avoid masking the real connector test.
- Ran `openclaw doctor --fix` on Amanda.
- Doctor migrated Amanda from legacy `codex/gpt-*` refs to canonical `openai/gpt-*` refs, migrated the legacy OpenAI Codex auth profile to the canonical OpenAI provider, and repaired one Codex session route.
- Amanda config after repair:
  - Primary model: `openai/gpt-5.5`
  - Fallback: `openai/gpt-5.4-mini`
  - Auth order: `openai:jzedbiz@gmail.com`, then `openai:api-key-backup`
  - Codex plugin: enabled
  - MCP servers: none
- Restarted Amanda and confirmed healthy.
- Ran the user's exact Biz Brain page workflow again.
- Amanda succeeded, using:
  - `codex_apps.notion_fetch`
  - `codex_apps.notion_notion-update-page`
- Amanda added the limerick at the top of the Notion page and reported the main headings/sections.

## Rest Of Fleet Check

- `inga`: valid `NOTION_API_KEY`, no Notion MCP server yet.
- `gohzed`: valid `NOTION_API_KEY`, no Notion MCP server yet.
- `maggie`: valid `NOTION_API_KEY`, no Notion MCP server yet.
- `marsha`: valid `NOTION_API_KEY`, no Notion MCP server yet.
- `terry`: has Notion MCP server, but the active embedded Notion token is stale; runtime `NOTION_API_KEY` is valid.
- `victor`: valid `NOTION_API_KEY`, no Notion MCP server yet.
- `vivian`: valid `NOTION_API_KEY`, no Notion MCP server yet.
- `wilma`: valid `NOTION_API_KEY`, no Notion MCP server yet.
- `edith`: valid `NOTION_API_KEY`, no MCP servers currently configured.
- Working agents for the user's exact page workflow show `codex_apps.notion_*` tools in their runtime traces:
  - `victor`
  - `terry`
  - `grogar`
  - `edith`
  - `wilma`
  - `vivian`
- Failing agents do not show `codex_apps.notion_*` in their runtime traces:
  - `amanda`
  - `inga`
  - `gohzed`
  - `maggie`
  - `marsha`

## Fleet Repair

- Applied the Amanda-proven repair to the remaining affected agents:
  - `inga`
  - `gohzed`
  - `maggie`
  - `marsha`
- Inga, Gohzed, and Maggie were migrated from legacy `codex/gpt-*` refs to canonical `openai/gpt-*` refs and from legacy `openai-codex:*` auth routing to canonical `openai:*` auth routing.
- Maggie also had stale Codex session routes repaired.
- Marsha already had canonical model/auth config; `openclaw doctor --fix` completed without config migration, then restart cleared her runtime state.
- Restarted all four containers and confirmed healthy.
- Final repaired config pattern:
  - Primary model: `openai/gpt-5.5`
  - Fallback: `openai/gpt-5.4-mini`
  - Auth order: `openai:jzedbiz@gmail.com`, then `openai:api-key-backup`
  - Codex plugin: enabled
  - MCP servers: none

## Final Verification

- Amanda: succeeded on the exact Notion page workflow and used `codex_apps.notion_fetch` plus `codex_apps.notion_notion-update-page`.
- Inga: succeeded on the exact Notion page workflow and used `codex_apps.notion_fetch` plus `codex_apps.notion_notion-update-page`.
- Gohzed: succeeded on the exact Notion page workflow and used `codex_apps.notion_fetch` plus `codex_apps.notion_notion-update-page`.
- Maggie: succeeded on the exact Notion page workflow and used `codex_apps.notion_fetch` plus `codex_apps.notion_notion-update-page`.
- Marsha: succeeded on the exact Notion page workflow and used `codex_apps.notion_fetch`, `codex_apps.read_mcp_resource`, and `codex_apps.notion_notion-update-page`.
- Each agent added a new limerick at the top of the page and signed it with their name.

## Operational Lesson

- Do not install plain Notion MCP as the first fix for this workflow.
- The business workflow depends on the Codex Apps connector layer.
- If an agent can use generic Notion API tools but cannot access the user's shared workspace page, check whether it is receiving `codex_apps.notion_*` tools.
- If not, check for legacy `codex/gpt-*` refs, legacy `openai-codex:*` auth routing, and stale session route pins.
- Use `openclaw doctor --fix` on one agent first, restart, then verify the exact page workflow before rolling out.
