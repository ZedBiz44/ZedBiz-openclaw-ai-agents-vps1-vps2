# 2026-07-12 | Cody | Asana Skills Rollout To Amanda Terry Wilma Inga

Date: 2026-07-12
Agent: Cody
Status: Complete

## Summary

Rolled out the ZedBiz Asana skills to the live OpenClaw agent workspaces on VPS1.

## Agents Updated

- Amanda: regular Asana Agent Control skill and Advanced Asana Control skill
- Terry: regular Asana Agent Control skill
- Wilma: regular Asana Agent Control skill
- Inga: regular Asana Agent Control skill

## Files Updated

Each target agent workspace received the skill files under `workspace/skills`.

- `workspace/skills/zedbiz-asana-agent-control/SKILL.md`
- `workspace/skills/zedbiz-asana-agent-control/agents/openai.yaml`
- Amanda only: `workspace/skills/zedbiz-advanced-asana-control/SKILL.md`
- Amanda only: `workspace/skills/zedbiz-advanced-asana-control/agents/openai.yaml`

Each target agent also received lean Asana routing sections in:

- `workspace/AGENTS.md`
- `workspace/TOOLS.md`

## Identity Values Installed

- Amanda: Amanda zbiz, `amanda@zedworks.com`, user GID `1213974002925107`
- Terry: Terry Zagent, `terry@agents.zbiz.ca`, user GID `1214469570857381`
- Wilma: Wilma Zagent, `wilma@agents.zbiz.ca`, user GID `1214049698033540`
- Inga: Inga Zagent, `inga@agents.zbiz.ca`, user GID `1214056417378023`
- Workspace GID: `11298561585567`
- Expected Asana MCP server: `@roychri/mcp-server-asana`

## Verification

Verified on VPS1 that:

- Amanda has both regular and advanced Asana skills installed.
- Terry, Wilma, and Inga have the regular Asana skill installed.
- All four have `## Asana Identity And Tool Routing` in `AGENTS.md`.
- Amanda has `## Advanced Asana Authority` in `AGENTS.md`.
- All four have `## Asana Tools` in `TOOLS.md`.
- Amanda has `## Advanced Asana Tools` in `TOOLS.md`.
- Active OpenClaw config files contain `@roychri/mcp-server-asana` and `ASANA_ACCESS_TOKEN` markers for all four agents. Token values were not printed or recorded.

## Next Test

Start a fresh session for each agent and ask it to check Asana identity only. Expected result: the PAT-based MCP `me` call returns that agent's own Asana email and workspace `11298561585567`. If any agent returns Jack or the Codex/ChatGPT connector, the skill should stop the work and report the authority-path failure.
