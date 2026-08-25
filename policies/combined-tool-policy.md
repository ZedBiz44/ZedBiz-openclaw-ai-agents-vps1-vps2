# Combined Tool Policy for Terry and Vivian

## Purpose

This policy lets Terry and Vivian use **GPT-5.6 Sol through Codex** for normal work and governed Notion work while discovering only the approved OpenClaw tools needed for video and operations. It prevents a broad runtime switch from hiding Codex Apps Notion access.

## Normal Model and Notion Rules

- GPT-5.6 Sol is the normal model and uses the Codex runtime.
- Use Codex Apps discovery and the approved OAuth connection for all governed Notion search, create, update, and fetch work.
- Complete the required duplicate search before creating a Notion record, then refetch any created or updated record and report its exact URL.
- Do not use `codex_endpoint_probe`, `codex_sessions_list`, a supervisor socket, `ntn`, a direct API, an environment token, or a standalone Notion fallback as a Notion health check or substitute route.
- If Codex Apps Notion discovery or an approved Notion call fails, stop and report the exact failure. Do not improvise an alternate Notion route.

## Video and Operations Rules

- Remain in the Sol Codex session when video, Percify, browser, memory, Wiki, Asana, scheduling, or another OpenClaw capability is needed.
- Use deferred tool discovery to load only the required approved OpenClaw tool or tools for the task.
- Do not change the agent’s normal model runtime merely to access a tool.
- Tool discovery and model listing do not authorize paid media generation. Follow all existing approval, cost, filename, and delivery rules before generating media.
- Clearly report the exact tool used and whether it was Codex Apps, Codex built-in, or OpenClaw discovered when the distinction affects verification.

## Backup Model Rules

- GPT-5.6 Terra and GPT-5.6 Luna remain OpenClaw backups.
- If a Terra or Luna fallback session needs governed Notion work, stop and request a Sol Codex session. Do not improvise a Notion route.

## Asana Identity Rules

- Preserve the agent-owned, PAT-backed OpenClaw Asana route for agent-owned work.
- Never use Jack’s personal Codex or ChatGPT identity for agent-owned Asana actions.

## Completion Rules

- For governed Notion work, report the exact Notion URL, the approved route used, and the verification result.
- Keep GitHub as the technical source of truth for configuration and deployment changes.
