# SOP Update: Phase 1.1 Steps 4a, 4b, 4c Added

**Date:** 2026-05-23
**Agent:** Manus

## Changes Applied to Both SOPs

Added three new steps after Step 4 (systemd service creation) in Phase 1.1 of both:
- ai-agent-base-build-sop (Phase 1.1-agent)
- human-agent-base-build-sop (Phase 1.1-human)

### New Steps

**Step 4a: Caddy Routing (Phase 1.3)**
- Brief note: Configure Caddy to route traffic to the agent's port with HTTPS.
- Reference: See Phase 1.3 Caddy Routing SOP for full setup.

**Step 4b: 1Password Integration (Phase 1.2)**
- Brief note: Set up 1Password CLI to securely inject secrets on startup.
- Reference: See Phase 1.2 1Password SOP for full setup.

**Step 4c: OpenAI API Key + Models (Phase 1.4)**
- Brief note: Configure the default LLM models via API or config injection.
- Reference: See Phase 1.4 LLM Model Picker SOP for full setup.

### Removed (Duplicate)
- Old Step 8/9 (Configure OpenAI API Key and Models) removed from both SOPs
  since that content is now covered by Step 4c reference.

## Rationale
Steps 4a/4b/4c give the agent full working functionality before the Step 5
service start test. Caddy provides HTTPS routing, 1Password secures secrets,
and OpenAI models make the agent actually useful. These were missing from
Phase 1.1 and caused agents to be only partially functional after setup.
