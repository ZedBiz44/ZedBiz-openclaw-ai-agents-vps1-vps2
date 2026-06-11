# 2026-06-11 | Manus | Frank Auth and Model Config Fix
Date: 2026-06-11 Mountain Time
Agent: Manus
Status: Done
Server: VPS2 / 2.24.104.80

## Summary
Fixed Frank's model config (wrong prefixes, deprecated models) and completed Codex OAuth setup.
Also updated VPS1 SOP pages Phase 1.4 and 1.4a with new fallback chain (gpt-5.4-mini as Fallback 1).

---

## Model Config Changes

### Before
- Primary: `codex/gpt-5.5` (correct) but also had `openai/gpt-5.5` as first fallback
- Fallbacks: `openai/gpt-5.5, openai/gpt-5.4, openai/gpt-5.4-mini, openai/gpt-5.3-codex, openai/gpt-5.5` (duplicates, deprecated, wrong prefix)
- `openai/gpt-5.3-codex` was deprecated and causing unknown-model errors

### After
- Primary: `codex/gpt-5.5`
- Fallback 1: `codex/gpt-5.4-mini`
- Fallback 2: `openrouter/google/gemini-3.1-flash-lite`
- Fallback 3: `openrouter/deepseek/deepseek-v4-flash:free`
- Removed: `openai/gpt-5.5`, `openai/gpt-5.4`, `openai/gpt-5.4-mini`, `openai/gpt-5.3-codex`
- Added: `codex/gpt-5.5`, `codex/gpt-5.4`, `codex/gpt-5.4-mini` with `agentRuntime: codex`

---

## Auth Setup

### Issue
Frank was copied from VPS1 Docker agents. His `.env` uses `op://` 1Password references.
The `auth login --provider openai-codex --device-code` command failed with "No provider plugins found"
because the Hostinger browser terminal does not resolve `~/npm` plugin paths the same way SSH does.

### Root Cause
- Frank's Codex plugin is at `~/npm/node_modules/@openclaw/codex/dist/index.js`
- In the Hostinger terminal, HOME=/root, so `~/npm` = `/root/npm` which did not exist
- Created symlink `/root/npm -> /root/.openclaw-frank/npm` to fix path resolution
- However the `openai-codex` provider ID appears to be unified into `openai` in OpenClaw 2026.6.5

### Resolution (Cody)
Cody ran the auth flow using `--provider openai` (not `openai-codex`):
```bash
./node_modules/.bin/openclaw models auth login --provider openai --device-code --force --set-default
```
This produced `Auth profile: openai:jzedbiz@gmail.com (openai/oauth)` with `source=codex-app-server`
confirming it IS the Codex subscription OAuth path in this version.

### Auth Order Added
Added `auth.order.openai` to `openclaw.json`:
```json
"auth": {
  "order": {
    "openai": [
      "openai-codex:jzedbiz@gmail.com",
      "openai:api-key-backup"
    ]
  }
}
```

---

## OpenClaw 2026.6.5 Auth Provider Note
In this version, the Codex OAuth flow stores under the `openai` provider (not `openai-codex`).
The profile `openai:jzedbiz@gmail.com` with `source=codex-app-server` IS the Codex subscription auth.
The `openai-codex` provider ID from earlier versions appears to have been unified into `openai`.

---

## Pending
- Frank's 1Password vault setup (Jack to action) -- until done, manual CLI commands show `op://` noise
- Edith (VPS1) still needs Codex OAuth: `docker exec -it edith openclaw models auth login --provider openai --device-code`

---

## SOP Updates (Notion)
- Phase 1.4 LLM Model Picker: updated fallback chain, pricing table, deprecated model notes
- Phase 1.4a OpenAI OAuth Provider: updated provider naming, fallback chain, auth flow notes
- Both bumped to v4
