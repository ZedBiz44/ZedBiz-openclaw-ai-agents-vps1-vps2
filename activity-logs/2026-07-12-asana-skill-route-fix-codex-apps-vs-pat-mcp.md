# 2026-07-12 | Cody | Asana Skill Route Fix For Codex Apps Vs PAT MCP

Date: 2026-07-12
Agent: Cody
Status: Complete

## Problem

After the Asana skill rollout, Inga, Terry, and Wilma correctly stopped when `mcp__codex_apps__asana` returned Jack (`jack@zedworks.com`). However, the regular skill language was still too easy for an agent to interpret as final stop instead of first rejecting the wrong connector and then finding the PAT-based OpenClaw Asana MCP route.

## Live Findings

- Codex Apps Asana connector in the Codex surface is Jack-authenticated.
- OpenClaw configs for Terry, Inga, and Wilma include an `mcp.servers.asana` entry using `@roychri/mcp-server-asana` and `ASANA_ACCESS_TOKEN`.
- `openclaw mcp probe asana` inside Terry, Inga, and Wilma containers reports the Asana MCP server starts and exposes 41 tools.
- A read-only OpenClaw agent-runner test for Terry using model `openai/gpt-5.5` successfully verified the PAT route as `terry@agents.zbiz.ca`, user GID `1214469570857381`, workspace `11298561585567`.

## Change Made

Updated the regular Asana skill and live agent instructions for Amanda, Terry, Wilma, and Inga:

- If `mcp__codex_apps__asana` returns Jack, treat that connector as the wrong route, not the final answer.
- Continue looking for the OpenClaw PAT MCP route named `asana`.
- Stop only if the PAT MCP route is configured but not callable in the active session.
- Use the phrase `Blocked on tool exposure` when that happens.

## Files Updated

- Global skill: `C:/Users/zener/.codex/skills/zedbiz-asana-agent-control/SKILL.md`
- Live agent skill copies under `/opt/openclaw/agents/{agent}/workspace/skills/zedbiz-asana-agent-control/`
- Live `AGENTS.md` and `TOOLS.md` for Amanda, Terry, Wilma, and Inga

## Practical Testing Note

The correct test surface is the OpenClaw agent runtime/session, not a Codex Apps-only surface. If an agent can only see `mcp__codex_apps__asana`, it should not do Asana work. If it can reach OpenClaw MCP server `asana`, it should use that PAT route.
