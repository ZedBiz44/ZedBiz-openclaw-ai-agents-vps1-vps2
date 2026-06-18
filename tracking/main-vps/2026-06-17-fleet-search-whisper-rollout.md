# VPS1 Fleet Search + Whisper Rollout -- 2026-06-17
Date: 2026-06-17 | Author: Cody | Status: Completed

## Summary
Rolled out the shared skill/plugin/search/Whisper setup across all active VPS1 OpenClaw agents.
All 11 active agents updated, restarted, and verified healthy.

## Scope
Active agents updated: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, Wilma.
Zara was skipped -- does not currently have the normal active-agent files (.op.token, .env, compose, OpenClaw config).

## Changes Applied to All Active Agents
- Added 1Password-backed env refs for OPENAI_WHISPER_API_KEY, PERPLEXITY_API_KEY, TAVILY_API_KEY
- Refreshed .env.resolved from 1Password for every active agent
- Enabled the main SOP plugin set:
  Perplexity, Tavily, policy, webhooks, workboard, llm-task, codex-supervisor, diagnostics-otel,
  gradium, oc-path, open-prose, parallel, telegram, thread-ownership
- Enabled the internal main skill list; optional/off skills kept disabled per Skill Plugin Setup SOP
- Patched the live openai-whisper-api transcription helper to use OPENAI_WHISPER_API_KEY first,
  OPENAI_API_KEY only as fallback
- Restarted all active agents

## Search Provider Assignments
| Agent | Provider |
|-------|----------|
| Edith | Perplexity |
| Victor | Perplexity |
| Amanda | Tavily |
| Gohzed | Tavily |
| Grogar | Tavily |
| Inga | Tavily (temporary -- Brave not yet exposed in 2026.6.8 plugin inventory) |
| Maggie | Tavily |
| Marsha | Tavily |
| Terry | Tavily |
| Vivian | Tavily |
| Wilma | Tavily |

## Verification
- All 11 active agents up and healthy after restart
- Each active agent confirmed to have OPENAI_WHISPER_API_KEY, PERPLEXITY_API_KEY, TAVILY_API_KEY in running container environment
- Search smoke tests passed for every active agent using its selected provider
- Whisper API smoke tests passed for every active agent using generated one-second silent audio
- `openclaw doctor` returned exit code 0 for every active agent
- Plugin errors: 0 across all active agents

## Remaining Notes
- Doctor still reports missing skill requirements: 9 on most agents, 6 on Victor
  These are known main-skill binary/setup gaps, not rollout failures
- Live Whisper helper patch still needs to be baked into the next base image or durable skill overlay
  (already recorded in Phase 5.2 Docker Base Image Creation)

## Notion Reference
https://app.notion.com/p/382a3e33d5818126915cefe14b9e09a1
