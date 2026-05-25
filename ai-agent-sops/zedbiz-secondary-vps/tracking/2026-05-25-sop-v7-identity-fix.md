# SOP v7 — Identity and Instructions Path Fix
**Date:** 2026-05-25
**Agent:** Manus
**Scope:** Both SOPs updated (ai-agent-base-build-sop-phase11.md, human-agent-base-build-sop-phase11.md)

## What Was Wrong

After the v6 rebuild, Harry was hallucinating his skills and ignoring his instructions. He claimed he didn't have access to the OpenClaw control panel and didn't know what skills were active.

**Root cause:**

The v6 SOP seeded `IDENTITY.md`, `USER.md`, `SOUL.md`, and `AGENTS.md` into the `workspace` directory (`/root/.openclaw-harry/workspace/`). 

However, OpenClaw's `workspace` setting in `openclaw.json` only controls where the agent's *tools* (like `file_write` or `dir_list`) operate. It **does not** control where OpenClaw looks for the agent's system prompt, identity, or instructions.

OpenClaw looks for agent instructions in `OPENCLAW_STATE_DIR/agents/main/agent/`. Because the SOP set `OPENCLAW_STATE_DIR=/root/.openclaw-harry`, OpenClaw created the `agents/main/agent/` directory structure there, but it was empty. Harry was running with a blank system prompt.

## The Fix

The SOP must seed the instruction files into the correct directory where OpenClaw actually reads them to build the system prompt.

### Fix 1: Change the seed directory in Step 6c

Changed the target directory for the four seeded files from:
`/root/.openclaw-${AGENT_ID}/workspace/`
To:
`/root/.openclaw-${AGENT_ID}/agents/main/agent/`

### Fix 2: Ensure the directory exists before seeding

Added `mkdir -p /root/.openclaw-${AGENT_ID}/agents/main/agent` at the start of Step 6c.

### Fix 3: Update the Workspace Rule in AGENTS.md

Updated the `AGENTS.md` file to clarify the distinction between instructions and workspace:

```markdown
## Workspace Rule
My workspace is at `/root/.openclaw-harry/workspace`. All files I create or reference should live there. My instructions live in `/root/.openclaw-harry/agents/main/agent/`.
```

### Fix 4: Update the git init location

The git repository should track the instructions, not just the empty workspace. Changed the `git init` location in Step 6c to `/root/.openclaw-${AGENT_ID}/agents/main/agent/`.

### Fix 5: Update verification paths

Updated the verification checks in Step 6c, Step 10, and Step 13 to look for the files in the new `agents/main/agent/` path instead of `workspace/`.

## Next Step

Wipe Harry on VPS-2 and rebuild from scratch using the corrected v7 SOP.
