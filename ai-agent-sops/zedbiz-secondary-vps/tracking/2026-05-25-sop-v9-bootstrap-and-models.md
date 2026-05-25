# SOP v9 — Bootstrap Pre-Seeding Removal and Model Fix
**Date:** 2026-05-25
**Agent:** Manus
**Scope:** Both SOPs updated (ai-agent-base-build-sop-phase11.md, human-agent-base-build-sop-phase11.md)

## What Was Wrong

1. **Pre-Seeding Interference:** The SOP instructed the builder to manually create `IDENTITY.md`, `USER.md`, `SOUL.md`, and `AGENTS.md` before the agent's first launch. This bypassed and broke OpenClaw's native bootstrap process, which expects to gather this information through the initial conversation and write the files itself.
2. **Model Configuration:** The SOP specified `GPT-5.2` as a fallback, which does not exist. It also overrode the `gpt-4o` model definition to be text-only, breaking vision capabilities.

## The Fix

### Fix 1: Remove Pre-Seeding
Completely removed "Step 6c: Pre-Seed Workspace Files" from both SOPs. The agent will now start with a clean slate and use the native OpenClaw bootstrap process to establish its identity and rules during the first conversation.

### Fix 2: Correct Model Configuration
Updated the model configuration in the SOP:
- Main model: `GPT-4.1` (which natively supports vision)
- Default model: `GPT-4o` (which natively supports vision)
- Removed the manual `models.json` override that was restricting `gpt-4o` to text-only input.

## Next Step

Wipe Harry on VPS-2 and rebuild from scratch using the corrected v9 SOP. The agent will now properly execute the bootstrap process on first login and have vision capabilities enabled.
