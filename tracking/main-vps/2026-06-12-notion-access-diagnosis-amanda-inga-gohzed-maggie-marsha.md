# 2026-06-12 - Notion Access Diagnosis For Amanda, Inga, Gohzed, Maggie, And Marsha

Date | Author | Status: 2026-06-12 | Cody | Diagnosed - Awaiting Fix Confirmation

## Summary

- Investigated why Amanda, Inga, Gohzed, Maggie, and Marsha cannot access Notion.
- Found all five containers are running and healthy.
- Found all five have the `openai-codex:jzedbiz@gmail.com` OAuth profile present in OpenClaw config.
- Found all five have only the `asana` MCP server configured.
- Found no `notion` MCP server path in the five named agents' OpenClaw config.
- Compared against Terry, which does have both `asana` and `notion` configured at the MCP layer.

## Live Agents Checked

- `amanda`: healthy, MCP servers: `asana`
- `inga`: healthy, MCP servers: `asana`
- `gohzed`: healthy, MCP servers: `asana`
- `maggie`: healthy, MCP servers: `asana`
- `marsha`: healthy, MCP servers: `asana`

## Diagnosis

- This does not look like a simple expired OpenAI Codex OAuth problem.
- The OpenAI Codex OAuth profile exists in the five named agents.
- The missing piece is that Notion is not exposed to these agents as a configured MCP/tool server.
- In practical terms: the agents have their OpenAI/Codex identity, but they do not currently have the Notion tool doorway wired into their runtime.

## Comparison

- Terry is the known-good reference checked during this diagnosis.
- Terry's OpenClaw MCP layer includes both `asana` and `notion`.
- The five affected agents only include `asana`.

## Recommended Fix

- Test on one affected agent first, preferably Amanda.
- Add the same Notion MCP server pattern used by Terry to Amanda.
- Probe the Notion MCP server from Amanda.
- Run one harmless read-only Notion check.
- If Amanda passes, repeat for Inga, Gohzed, Maggie, and Marsha.
- Do not assume OpenAI Codex OAuth alone is enough; verify the Notion tool appears in each agent's MCP/tool list.

## No Server Fix Applied Yet

- This was a diagnosis-only pass.
- No agent configs were changed.
- No containers were restarted.
