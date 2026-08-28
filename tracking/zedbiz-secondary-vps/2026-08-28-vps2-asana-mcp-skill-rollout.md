# 2026-08-28 | Manus | VPS2 Asana MCP and Skill Rollout

date: 2026-08-28 MDT | agent: Manus | status: Complete, functional task-workflow test pending Jack

## Summary

Deployed the ZedBiz standard PAT-backed Streamable HTTP Asana MCP and `z-asana-agent-control` Skill to Harry, Suzy, and Frank on VPS2. Each native OpenClaw agent now has a dedicated loopback-only Asana service, an OpenClaw route named `asana`, its existing agent-specific 1Password Asana reference, and the current renamed Skill. No Asana task was created, modified, commented on, or completed during deployment or verification.

## Final Deployment State

| Agent | Local Asana MCP service | Bind | Authenticated Asana identity | User GID | Workspace GID | Incomplete assigned-task count | Skill status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Harry | `zedbiz-asana-mcp@harry.service` | `127.0.0.1:4110` | `harry@agents.zbiz.ca` | `1215559750337835` | `11298561585567` | 5 | Installed, new-only discovery |
| Suzy | `zedbiz-asana-mcp@suzy.service` | `127.0.0.1:4210` | `suzy@agents.zbiz.ca` | `1215557534470003` | `11298561585567` | 3 | Installed, new-only discovery |
| Frank | `zedbiz-asana-mcp@frank.service` | `127.0.0.1:4310` | `frank@agents.zbiz.ca` | `1215596271715682` | `11298561585567` | 3 | Installed, new-only discovery |

Every Asana MCP service and OpenClaw agent service was active during the final independent audit. Each MCP route exposed 47 standard tools, including the required `asana_get_user`, `asana_get_my_tasks`, `asana_get_task`, `asana_create_task_story`, and `asana_update_task` tools. The new Skill package SHA-256 was `72d2ef93a498f30347bf00a074e3e6854118e52f003ca1d8785dd5b5a92a188c` for all three agents. No `zedbiz-asana-agent-control` directory, runtime discovery entry, or backup reference remains.

## Credential and Network Design

The services use the existing agent-specific 1Password records:

- `op://agent-harry/asana-api-key-harry/credential`
- `op://agent-suzy/asana-api-key-suzy/credential`
- `op://agent-frank/asana-api-key-frank/credential`

The references stay in each agent's existing `.env` file. Each OpenClaw startup wrapper and the new local Asana service use `op run` to resolve the reference only when the process starts. No PAT was copied into Git, an OpenClaw JSON file, an installer argument, a systemd unit, this record, or a command result.

Each service binds only to `127.0.0.1` on its own port. It is therefore not exposed through VPS2's public network, Caddy, or the other two agents. The local MCP route sends `Authorization: Bearer ${ASANA_ACCESS_TOKEN}` through environment substitution, matching the established ZedBiz pilot pattern.

## Issue Encountered and Fix Applied

The first pilot implementation incorrectly assumed a separate internal bearer record had to be created in each agent vault. The existing agent service accounts have read access but not permission to create new vault items, so 1Password denied the attempted creation. The guarded installer rolled Harry back successfully. No partial service, route, Skill, or legacy package remained.

The correct existing pattern was then applied: both the local sidecar and OpenClaw resolve the agent's already-existing Asana key at startup through `op run`. A second preflight error came from reading the `username` label of the `email-address-<agent>` item rather than its protected `credential` value. The installer was corrected, published, and Harry then passed the real Asana identity and workspace check. Suzy and Frank were deployed only after Harry passed.

## Source Changes

| Commit | Change |
| --- | --- |
| `3c2596d` | Added native VPS2 deployment adapter and loopback bind control. |
| `69b3421` | Added deployment rollback safeguards. |
| `366f531` | Switched installer to established 1Password startup injection. |
| `5461ead` | Corrected protected agent email preflight field. |
| `f8e9baf` | Silenced the expected first-start readiness race. |

The reusable implementation is under `docker/asana-http-mcp/deploy/vps2/` and includes a per-agent installer, a real authenticated verifier, and a final three-agent audit.

## Remaining Test Gate

The technical rollout is complete. Jack should run normal agent-owned Asana prompts for Harry, Suzy, and Frank and verify that the Skill checks the expected identity and stays within task-level action boundaries. Do not use the Skill for project, portfolio, bulk, delete, team-membership, or other structural work. Those requests remain restricted and must route to `z-advanced-asana-control` with approval.
