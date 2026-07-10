# 2026-07-10 | Cody | Asana Agent Control Skill Rewrite

Date: 2026-07-10 | Agent: Cody | Status: Complete

## Summary

Rewrote the Notion page `Asana Agent Control Skill` as the master operating document for routing OpenClaw agent Asana work through each agent's PAT-based Asana MCP instead of Jack-authenticated Codex/ChatGPT Asana connector access.

## Work Completed

- Added overview of the two Asana authority paths: Codex/ChatGPT Asana app connector versus agent PAT-based MCP.
- Generalized the skill from Cody-specific task running to all ZedBiz/OpenClaw agents.
- Added an Asana identity gate requiring `me.email` to match the agent's own Asana email before task execution.
- Added `AGENTS.md` and `TOOLS.md` rollout blocks.
- Added SOP for implementing on one agent first, verifying identity, verifying task discovery, and verifying comment attribution.
- Added user guide prompts for identity check, task check, work command, and diagnose command.
- Added future hardening options such as removing Codex Asana exposure from agent runtimes or using a wrapper/gateway that refuses wrong-identity requests.

## Related Notion Records

- Asana Agent Control Skill: https://app.notion.com/p/399a3e33d5818001ad46f29b4f204b22
- Tech Updates journal: https://app.notion.com/p/399a3e33d58181e5a767ebd878f963bf

## Operating Decision

Start with `AGENTS.md`, `TOOLS.md`, and the `Asana Agent Control Skill` as the first control layer. Agent task execution should use the agent PAT-based MCP path; Jack/Codex Asana connector remains for intentional admin work only.
