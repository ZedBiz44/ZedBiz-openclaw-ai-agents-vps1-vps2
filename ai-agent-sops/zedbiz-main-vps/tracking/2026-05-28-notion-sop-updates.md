# Notion SOP Updates -- llm-model-picker and OpenAI-OAuth-Provider

**Date:** 2026-05-28 (Mountain Time)
**Agent:** Manus

---

## Pages Updated

### llm-model-picker
- URL: https://www.notion.so/112a3e33d58183e3982701e7462ce417
- Version: v3 (Fleet Standardized)

**Changes from previous version:**
- Added full 10-agent fleet table with ports and URLs
- Updated model list to reflect current 64-model standard (6 openai-codex + 58 openrouter)
- Removed `openai/gpt-5.5-pro` (requires Pro tier -- not available on current subscription)
- Added note about Pro Lite vs Pro tier model availability
- Added auth configuration section with correct order
- Added fleet rollout instructions
- Updated troubleshooting to include "Requested agent harness X is not registered" error
- Updated docker alpine workaround instructions
- Removed outdated references to `agentRuntime` overrides

### OpenAI-OAuth-Provider
- URL: https://www.notion.so/36da3e33d58180849714e16abdc8f1fc
- Version: v3 (Fleet Standardized)

**Changes from previous version:**
- Renamed from "OpenAI OAuth (Codex) Primary Setup - CORRECTED v2" to v3
- Added current token expiry date: 2026-06-07
- Added model availability table by subscription tier
- Updated examples to use `inga` as reference agent (not `terry`)
- Added fleet-wide renewal instructions (restart all agents after token renewal)
- Added API key backup registration loop for all 10 agents
- Added auth order fix reminder after paste-api-key
- Added key files table
- Removed outdated per-session model override examples (still valid but moved to secondary)
- Removed "Next Steps" placeholder text

---

## Key Facts Documented

- Codex OAuth token expires 2026-06-07 -- renewal required before that date
- `openai/gpt-5.5-pro` removed from all agents (requires Pro tier)
- `openai/*` and `openai-codex/*` both route through Codex app-server harness
- Valid `agentRuntime.id` values: `codex` only (not "pi", not "openclaw")
- paste-api-key always reorders auth -- always fix order after running it
- jackadmin is UID 1001 -- no sudo for chown; use docker alpine workaround
