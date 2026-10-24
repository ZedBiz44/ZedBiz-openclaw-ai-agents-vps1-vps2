## Notion Search Routing

- Keep Notion work in the approved Sol/Codex session and existing Codex Apps OAuth connection. Fetch `self` before the first content search.
- Prefer the dedicated AI-search tool when it is callable and access allows it. If `self` reports `ai_search` available but that separate tool is not listed, use the existing Codex Apps Notion `search` tool with a nonempty query. This supported entry point can perform AI search and return `type: "ai_search"`; a missing tool alias is not proof that search is unavailable.
- For that first search, omit optional exact filters and non-relevance sorting. Inspect the returned type, then fetch a relevant result before relying on it. Do not claim AI search if the response instead reports workspace search.
- Respect actual permission, billing and authentication errors. Do not switch accounts or use direct API tokens as a substitute. Preserve the existing governed publishing rules.

Reference: https://developers.notion.com/guides/mcp/mcp-supported-tools
