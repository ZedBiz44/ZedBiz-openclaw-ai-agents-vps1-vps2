# ZedBiz Asana HTTP MCP

Persistent Streamable HTTP MCP services for ZedBiz OpenClaw agents.

## Entry Points

- `dist/index.js` - standard Asana task, project, section, story, tag, prompt, and resource tools derived from `@roychri/mcp-server-asana` 1.8.0.
- `dist/team-server.js` - Amanda's advanced team and membership tools.
- `dist/smoke-test.js` - authenticated connection and tool-inventory test.

## Required Environment

- `ASANA_ACCESS_TOKEN`
- `MCP_AUTH_TOKEN`
- `MCP_ALLOWED_HOSTS`

Optional:

- `PORT` (default `8080`)
- `MCP_SESSION_TTL_MS` (default 15 minutes)
- `MCP_MAX_SESSIONS` (default 64)
- `ASANA_WORKSPACE_GID` (advanced server default `11298561585567`)

Both services expose `/mcp` and `/healthz`. They must remain on an internal Docker network with no published host port.

The Amanda pilot intentionally reuses her existing Asana PAT as the internal bearer token. This avoids adding a second secret during the one-agent test. A separate internal bearer secret can be introduced later without changing the service design.

## Upstream

The standard Asana tool implementation is based on `@roychri/mcp-server-asana` 1.8.0 under the included MIT license. ZedBiz adds native Streamable HTTP transport, bearer authentication, bounded sessions, health checking, and the separate advanced team entrypoint.
