# 2026-06-12 - Notion Access Diagnosis For Amanda, Inga, Gohzed, Maggie, And Marsha

Date | Author | Status: 2026-06-12 | Cody | Diagnosis Corrected - Amanda Not Fixed

## Summary

- Investigated why Amanda, Inga, Gohzed, Maggie, and Marsha cannot access Notion.
- Found all five containers are running and healthy.
- Found all five have the `openai-codex:jzedbiz@gmail.com` OAuth profile present in OpenClaw config.
- Found all five have only the `asana` MCP server configured.
- Found no `notion` MCP server path in the five named agents' OpenClaw config.
- Compared against Terry, which does have both `asana` and `notion` configured at the MCP layer.
- Found Terry's active Notion MCP block was pointing at an invalid stale Notion token.
- Found a valid `NOTION_API_KEY` already present in each agent's runtime environment.
- Added a plain Notion MCP server to Amanda that references `NOTION_API_KEY` instead of embedding the stale token.
- That only proved Amanda can access some Notion content through the plain Notion API.
- Amanda still cannot complete the user's real Biz Brain page workflow because that route cannot see the target page.
- Working agents use `codex_apps.notion_fetch` and `codex_apps.notion_notion-update-page`, not the plain `notion.API-*` route.

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
- Corrected diagnosis: the failed agents are not receiving the Codex Apps Notion connector tool surface used by the working agents.

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

## Recommended Next Step

- Do not roll out the plain Notion MCP config as the fix for this workflow.
- The correct fix needs to restore the OpenClaw Codex Apps Notion connector tool surface for the failing agents.
- Continue diagnosis at the connector/runtime provisioning layer that decides whether `codex_apps.notion_fetch` and `codex_apps.notion_notion-update-page` are included in an agent run.
- Avoid copying Terry's stale embedded token pattern.
