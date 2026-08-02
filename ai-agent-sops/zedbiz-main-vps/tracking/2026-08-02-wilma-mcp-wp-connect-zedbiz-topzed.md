# 2026-08-02 - Wilma MCP-WP-Connect Pilot for ZedBiz and TopZed

## Summary

- **Date:** 2026-08-02 Mountain Time
- **Changed By:** Cody
- **VPS:** Main VPS, `187.77.210.223`
- **Affected Agent:** Wilma
- **Status:** Done and live-tested

## Change Reason

- Add the new MCP-WP-Connect WordPress connections for ZedBiz.com and TopZed.com to Wilma as the first OpenClaw pilot.
- Keep the existing AllZed AI Engine WordPress connection unchanged.
- Read credentials from Wilma's dedicated 1Password vault instead of placing bearer tokens in GitHub or OpenClaw configuration.

## Change Details

- **Agent path:** `/opt/openclaw/agents/wilma`
- **Backup:** `/opt/openclaw/agents/wilma/backups/20260802-1308MDT-mcp-wp-connect-zedbiz-topzed`
- Added these 1Password-backed environment references to `.env` and `docker-compose.yml`:
  - `WP_MCP_KEY_ZEDBIZ_COM`
  - `WP_MCP_ENDPOINT_ZEDBIZ_COM`
  - `WP_MCP_KEY_TOPZED_COM`
  - `WP_MCP_ENDPOINT_TOPZED_COM`
- Added these native OpenClaw MCP routes to `config/openclaw.json`:
  - `wordpress-zedbiz-com`
  - `wordpress-topzed-com`
- Both working routes use the plugin's full MCP endpoint, `/wp-json/mcp/v2/http`, with streamable HTTP transport.
- Both routes explicitly set `requestTimeoutMs` to `60000`. OpenClaw otherwise applies a 1.5-second tool-discovery limit; these WordPress requests measured about 1.3 to 1.6 seconds and intermittently timed out without the explicit setting.
- Wilma is restarted through `/opt/openclaw/agents/wilma/op-start-wilma.sh`, which resolves her per-agent 1Password references before Docker Compose starts.
- The existing `wordpress-allzed` AI Engine route and `AIENGINE_BEARER_TOKEN` reference were preserved.

## Compatibility Finding

- The plugin screen currently labels `/wp-json/mcp/v1/http` as the OpenClaw endpoint and `/wp-json/mcp/v2/http` as the Hermes endpoint.
- OpenClaw `2026.7.1` now performs the full MCP initialization handshake. The v1 endpoint only supports direct `tools/list` and `tools/call`, so the native OpenClaw probe returns `Method not found`.
- The v2 endpoint supports `initialize`, `notifications/initialized`, `ping`, `tools/list`, and `tools/call`, so it is the endpoint that works with this OpenClaw version.
- The two endpoint items in the `agent-wilma` 1Password vault still display `/v1/http`. Wilma's service account is read-only and could not edit them. A human vault editor must change only those two endpoint credential values to `/v2/http`; the bearer-token items are correct.

## Verification

- Wilma container after a clean recreation: healthy.
- Public Wilma page: HTTP 200.
- Native OpenClaw probe for ZedBiz: six tools, 60-second request timeout, zero diagnostics.
- Native OpenClaw probe for TopZed: six tools, 60-second request timeout, zero diagnostics.
- End-to-end Wilma agent turn called both read-only post tools with zero failures:
  - ZedBiz returned post title `Testing this thing`.
  - TopZed returned post title `Wedding Planning Download01`.
- Both WordPress sites remained in global read-only mode during validation.
- No bearer token was printed into this record or committed.

## Rollback Note

- Restore `.env`, `docker-compose.yml`, and `openclaw.json` from `/opt/openclaw/agents/wilma/backups/20260802-1308MDT-mcp-wp-connect-zedbiz-topzed`.
- Restart Wilma with `/opt/openclaw/agents/wilma/op-start-wilma.sh restart`.
- Verify the Wilma container is healthy and `https://wilma.zbiz.ca/` returns HTTP 200.

## Follow-Up

- Update the two 1Password endpoint credential values from `/v1/http` to `/v2/http` so the vault matches the proven OpenClaw configuration.
- Update the MCP-WP-Connect plugin labels and operator documentation so current OpenClaw users are directed to the full MCP endpoint.

## Links

- [Technical Documentation journal entry](https://app.notion.com/p/3b0a3e33d58181278e97e296243c2436)
