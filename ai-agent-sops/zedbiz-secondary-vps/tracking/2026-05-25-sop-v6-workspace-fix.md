# SOP v6 — Workspace Path Fix + Pre-Seeded Workspace Files
**Date:** 2026-05-25
**Agent:** Manus
**Scope:** Both SOPs updated (ai-agent-base-build-sop-phase11.md, human-agent-base-build-sop-phase11.md)

## What Was Wrong

The v5 SOP had a critical workspace path bug that caused Harry to be broken after his first install.

**Root cause (diagnosed by Cody):**

The SOP set `HOME=/root/.openclaw-harry` in the systemd service and wrapper script. OpenClaw defaults to `~/.openclaw/workspace` for the workspace path. With `HOME` overridden, this resolved to:

```
/root/.openclaw-harry/.openclaw/workspace   <- actual active workspace
```

But the SOP and all verification steps were checking:

```
/root/.openclaw-harry/workspace             <- expected path, never used
```

Harry was running but his workspace was in the wrong nested location. IDENTITY.md was updated but USER.md, SOUL.md, and AGENTS.md were still stock defaults. Harry guessed at skill availability instead of checking `openclaw skills list`.

## Three Fixes Applied

### Fix 1: Explicit workspace in openclaw.json

Added `agents.defaults.workspace` to the config in Step 6:

```json
"agents": {
  "defaults": {
    "model": "openai/gpt-4o",
    "workspace": "/root/.openclaw-AGENT_ID/workspace"
  }
}
```

Without this field, OpenClaw ignores `OPENCLAW_STATE_DIR` for workspace resolution and falls back to `~/.openclaw/workspace`.

### Fix 2: openclaw setup --workspace command (new Step 6b)

Added a new Step 6b that runs:

```bash
openclaw setup --workspace /root/.openclaw-${AGENT_ID}/workspace --non-interactive
```

This creates the workspace directory and registers the path in the config. Verified that `--workspace` flag exists in OpenClaw v2026.5.22 (confirmed via `openclaw setup --help` on VPS-2).

Added three assertions after the setup command:
- Correct workspace must exist
- Nested workspace must NOT exist
- Global fallback must NOT exist

### Fix 3: Pre-seeded workspace files (new Step 6c)

Added a new Step 6c that pre-seeds four Harry-specific files before first launch:
- `IDENTITY.md` — who Harry is, his personality, his operator, his VPS details
- `USER.md` — who Jack is, his businesses, his working style
- `SOUL.md` — Harry's operating principles and character
- `AGENTS.md` — explicit instructions to run `openclaw skills list` before claiming any skill is available, plus rules for tools, memory, workspace, and 1Password

Also added `git init` and first commit in the workspace after seeding.

## Additional Changes

- Step 6 config now uses heredoc with placeholder substitution via `sed` to avoid variable expansion issues inside the heredoc
- Step 10 pre-start checks now verify IDENTITY.md and AGENTS.md are in place before starting the service
- Step 11 workspace isolation checks now include the nested workspace check
- Step 13 post-first-run checks now verify all four pre-seeded files survived
- Phase 1.1 Done When checklist updated to include all four workspace files and git init
- Added workspace path warning to the Critical Lines section

## Verified

- `openclaw setup --workspace` flag confirmed present in v2026.5.22 via SSH to VPS-2
- Both SOPs pushed to Notion (AI SOP: 3e4a3e33d5818352bdb701eed29da450, Human SOP: 04ea3e33d5818318b4ae812c80a98da3)

## Next Step

Wipe Harry on VPS-2 and rebuild from scratch using the corrected SOP.
