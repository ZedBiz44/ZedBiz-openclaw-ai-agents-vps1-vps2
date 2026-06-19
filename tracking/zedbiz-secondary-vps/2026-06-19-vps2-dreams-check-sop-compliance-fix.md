# 2026-06-19 | Manus | VPS2 Dreams Check + SOP Compliance Fix (All Three Agents)
Date: 2026-06-19 Mountain Time
Agent: Manus
Status: Done
Server: VPS2 / Hostinger / 2.24.104.80

## Summary

Two-part session: (1) checked Dreams cycle status for Harry, Suzy, and Frank after the 2:00 AM MDT run; (2) audited all three agents against the LLM Model Picker SOP and OpenAI OAuth Provider SOP -- found non-compliance on all three and applied fixes. All three agents now fully SOP-compliant and restarted clean.

---

## Part 1: Dreams Status Check

All three agents ran their Dreams cycle at 2:00 AM MDT as scheduled. All three phases (light, REM, deep) completed on all agents.

### Harry
- Light phase: 49 candidates staged
- REM phase: 49 reflections written
- Deep phase: 20 ranked, 0 promoted (all candidates have `recalls=0`, `queries=1` -- below `minRecallCount: 2` threshold)
- DREAMS.md: active, writing daily entries
- Memory files: 22 daily `.md` files, MEMORY.md only 12 lines (sparse but expected at this stage)
- Ingestion state: `daily-ingestion.json.migrated` -- no active ingestion file (pre-existing known issue)

### Suzy
- Same phase completion as Harry
- Light phase: 35 candidates staged
- Deep phase: 0 promotions (same low recall count reason)
- REM phase: some echo/repetition in reflections (pre-existing known issue)
- Ingestion state: same migrated state as Harry

### Frank
- All phases completed
- Dream diary written via Gemini fallback (was hitting 401 on OpenAI every call -- root cause identified and fixed in Part 2)
- No MEMORY.md file exists -- deep phase has nowhere to promote to (low priority, promotions not happening yet anyway)

### Dreams Diagnosis: 0 Promotions Across All Three
Not a bug. All memory candidates have `recalls=0` and `queries=1` -- they haven't been recalled or queried enough to hit the `minRecallCount: 2` threshold. This is expected behavior for agents with limited active conversation history. Promotions will start flowing naturally as agents get more use.

---

## Part 2: SOP Compliance Audit and Fix

### SOPs Referenced
- LLM Model Picker SOP: `https://app.notion.com/p/112a3e33d58183e3982701e7462ce417`
- OpenAI OAuth Provider SOP: `https://app.notion.com/p/36da3e33d58180849714e16abdc8f1fc`

### SOP Requirements (All Agents)
```json
{
  "model": {
    "primary": "codex/gpt-5.5",
    "fallbacks": [
      "codex/gpt-5.4-mini",
      "openrouter/google/gemini-3.1-flash-lite",
      "openrouter/deepseek/deepseek-v4-flash:free"
    ]
  },
  "auth": {
    "order": {
      "openai": ["openai-codex:jzedbiz@gmail.com", "openai:api-key-backup"]
    }
  }
}
```
No `auth.json` in `codex-home/`. No `agentRuntime` override in models config.

### Audit Results (Before Fix)

| Check | Harry | Suzy | Frank |
|---|---|---|---|
| Primary model | `openai/gpt-5.5` (WRONG) | `openai/gpt-5.5` (WRONG) | `codex/gpt-5.5` (OK) |
| Fallback chain | Old chain with deprecated `gpt-5.3-codex` (WRONG) | Same (WRONG) | SOP chain (OK) |
| Auth order | NOT SET (WRONG) | NOT SET (WRONG) | Set correctly (OK) |
| `agentRuntime` override | `{id: codex}` present (WRONG) | Same (WRONG) | None (OK) |
| `codex-home/auth.json` | Not present (OK) | Not present (OK) | EXISTS with `auth_mode: apikey` and unresolved `op://` ref (WRONG) |

### Root Cause: Frank's auth.json
Frank had a `codex-home/auth.json` with:
```json
{
  "auth_mode": "apikey",
  "OPENAI_API_KEY": "op://openclaw-agents-shared/openai-api-key/credential"
}
```
The codex plugin reads this file raw -- it does NOT resolve `op://` references. The literal string was being sent to OpenAI as the API key, causing 401 Unauthorized on every call. Frank was falling back to Gemini on every single request including Dreams narrative generation.

Harry and Suzy were using `openai/gpt-5.5` with `agentRuntime: codex` -- a different routing path that worked but was not SOP-compliant (wrong model prefix, stale fallback chain, missing auth order).

### Fix Applied
Script: `/tmp/fix_agents_sop.py` (run on VPS2)

**Harry changes:**
- `primary`: `openai/gpt-5.5` -> `codex/gpt-5.5`
- Fallbacks: old chain -> SOP chain
- Added `auth.order.openai: [openai-codex:jzedbiz@gmail.com, openai:api-key-backup]`
- Removed `agentRuntime: {id: codex}` from `openai/gpt-5.5` models entry
- Removed now-empty `openai/gpt-5.5` entry from models

**Suzy changes:** Same as Harry.

**Frank changes:**
- `openclaw.json`: no changes needed (already SOP-compliant)
- Deleted `codex-home/auth.json` (backed up as `auth.json.bak-sop-fix`)

All `openclaw.json` files backed up before modification as `openclaw.json.bak-sop-fix-20260619-163532`.

### Post-Fix Verification
All three services restarted. Startup logs confirmed:
- All three: `agent model: codex/gpt-5.5 (thinking=medium, fast=off)`
- All three: `provider auth state pre-warmed` -- no 401 errors
- Audit script re-run: all checks green on all three agents

---

## Files Modified
- `/root/.openclaw-harry/openclaw.json`
- `/root/.openclaw-suzy/openclaw.json`
- `/root/.openclaw-frank/agents/main/agent/codex-home/auth.json` (deleted)

## Backups
- `/root/.openclaw-harry/openclaw.json.bak-sop-fix-20260619-163532`
- `/root/.openclaw-suzy/openclaw.json.bak-sop-fix-20260619-163532`
- `/root/.openclaw-frank/openclaw.json.bak-sop-fix-20260619-163532` (no changes, backup still created)
- `/root/.openclaw-frank/agents/main/agent/codex-home/auth.json.bak-sop-fix`

## Open Items
- Frank has no `MEMORY.md` -- low priority until recall counts build up and deep phase starts promoting
- All three agents have `daily-ingestion.json.migrated` -- pre-existing issue, tracked separately
- Codex OAuth token (`openai-codex:jzedbiz@gmail.com`) expiry should be checked periodically -- renewal is a human task (device code flow per SOP)
