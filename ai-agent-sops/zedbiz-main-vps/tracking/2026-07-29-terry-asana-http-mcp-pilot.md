# Terry Persistent Asana MCP Rollout

Date: 2026-07-29 MDT | Agent: Cody | Status: Live rollout verified

## Purpose

- Move Terry's standard Asana route out of the Codex task lifecycle.
- Stop the stdio `npm exec` / shell / Node process group from consuming Terry's PID allowance after a task finishes.
- Reuse the persistent HTTP design already proven on Amanda.

## Scope

- Agent: Terry
- VPS: VPS1 at `187.77.210.223`
- Route changed: `asana`
- Routes not changed: all non-Asana tools and integrations
- GitHub issue: #94
- Notion diagnosis: Cody VPS1 Agent Diagnosis Solution

## Pre-Change Evidence

- Terry was Docker-healthy on OpenClaw 2026.7.1.
- Terry used 51 of 160 PIDs before the cutover.
- One Asana stdio process group was active under Codex: `npm exec`, shell, and Node, using 19 tasks in total.
- The live MCP configuration contained only the standard `asana` route.
- No recent user work appeared in Terry's Discord channel before the maintenance window.

## Identity Requirement

- PAT email: `terry@agents.zbiz.ca`
- User GID: `1214469570857381`
- Required workspace: `ZedBiz - Local Marketing Service`
- Workspace GID: `11298561585567`
- Jack-authenticated Codex/ChatGPT Asana access is prohibited for Terry's assigned work.

## Deployment Design

- One persistent internal Streamable HTTP service: `terry-asana-mcp`.
- Internal endpoint: `http://terry-asana-mcp:8080/mcp`.
- No host-published port.
- Bearer authentication uses Terry's existing PAT during this rollout.
- Session cap: 64.
- Idle session expiry: 15 minutes.
- Sidecar PID limit: 64.
- Terry's main PID limit remains 160.

## Verification

- The image built successfully from the same source proven on Amanda.
- The service exposed all 41 expected standard Asana tools.
- A real read-only `asana_list_workspaces` call returned Terry's two workspaces, including `ZedBiz - Local Marketing Service` (`11298561585567`).
- Terry and the sidecar survived Terry's normal 1Password-aware restart.
- Discord reconnected and resolved `@terry-openclaw`.
- Terry used 14 PIDs after the cutover, down from 51 before it.
- The sidecar used seven PIDs before its first real Asana call and stabilized at 11 afterward.
- Ten fresh MCP sessions did not increase the process counts.
- Five repeated real Asana calls left Terry at 14 PIDs and the sidecar at 11 across five samples.
- Terry had zero local `mcp-server-asana` or `npm exec @roychri` child processes after the cutover.
- Stopping the sidecar did not stop Terry or make his container unhealthy; the service restarted and passed the 41-tool smoke test.
- The original Compose file and OpenClaw JSON backup were both validated as usable rollback artifacts.

## Live Deployment

- Image: `zedbiz/asana-http-mcp:1.0.0-terry-pilot`
- Image manifest: `sha256:caf61f531664cf6f53ebfd209ac518a395a4b5ffd66610544b55b9db6dc0c7d2`
- Service: `terry-asana-mcp`
- Public host ports: none
- Terry remained at a 160 PID limit; raising it was not required.
- Deployment used Terry's existing `op-start-terry.sh` launcher so 1Password references continued to resolve normally.

## Rollback

- Restore `/opt/openclaw/agents/terry/docker-compose.yml.pre-http-mcp-20260729-181621` to `docker-compose.yml`.
- Restore `/opt/openclaw/agents/terry/config/openclaw.json.pre-http-mcp-20260729-181621` to `config/openclaw.json`.
- Use the documented Docker Alpine ownership workaround if the config directory blocks the host user.
- Run `/opt/openclaw/agents/terry/op-start-terry.sh restart`.
- Confirm Terry is healthy and the original stdio `asana.command` definition is present.

Validated checksums:

- Compose SHA-256: `62506f0c43473e8b509a314c8777e89f48c8379c8b3032215b795516decfcb3f`
- Config SHA-256: `9ff6cc87b883466f348c302bcc6d8496460591dc503e25ae700afbc3a6b4b286`

## Deployment Note

- The first backup attempt could copy the Compose file but the host user could not read Terry's `config/openclaw.json`.
- The deployment used the approved Docker Alpine root-volume workaround to make the config backup without exposing or changing Terry's secrets.
- The first source extraction preserved Windows read-only directory modes. The partial directory was removed only after its exact resolved path was verified, then re-extracted through the same Docker Alpine workaround with correct ownership.

## Dependency Note

- Five high audit findings remain in the old Asana SDK's bundled Babel CLI dependency tree.
- That CLI is not invoked by the runtime service.
- Replacing or removing the upstream Asana SDK remains separate hardening work and does not affect this MCP lifecycle correction.

## Files

- `docker/asana-http-mcp/`
- `docker/asana-http-mcp/deploy/terry/docker-compose.yml`
- `docker/asana-http-mcp/deploy/terry/switch-openclaw-mcp.mjs`
