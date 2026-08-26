# Canonical ZedBiz AGENTS.md Template

Date: 2026-08-26 Mountain Time
Agent: Cody
Status: Complete

## Purpose

Replace the June Edith-specific Notion sample with a generic, current ZedBiz OpenClaw `AGENTS.md` template based on the approved Guidelines and live fleet reassessment.

## Files And Pages

- Canonical GitHub template: `docs/templates/standard-agents-md-template.md`
- Notion template: https://app.notion.com/p/37ba3e33d581805797e0c5273bb50a3b
- Guidelines: https://app.notion.com/p/3c8a3e33d58180c79670e5a06201d4d6
- Assessment: https://app.notion.com/p/3c8a3e33d58180fa92e9fcc512d46aec

## Main Corrections

- Removed all Edith-specific identity, VPS, route, skill-count, and approval assumptions.
- Removed stale `ntn` routing and generic tracker names.
- Removed broad automatic memory and publishing requirements.
- Removed generic heartbeat, weather, email, calendar, and social-notification examples.
- Added explicit Get-er-Done and Diagnose modes.
- Added review-only, scope, write, architecture, credential, production, and destructive-action boundaries.
- Added live capability and authenticated-identity verification.
- Added clean GitHub, Notion, Asana, and runtime source-of-truth separation.
- Added assignment acknowledgement, continuity, delivery, verification, rollback, and handoff standards.
- Added provider-neutral memory boundaries with agent-specific routes only when verified.
- Added context-budget and maintenance requirements.

## Deployment Boundary

This task creates the canonical template and updates documentation. It does not deploy the template to any live agent.

Before a live rollout:

- Replace every placeholder.
- Remove template-control instructions and inapplicable sections.
- Verify the agent's host, runtime, paths, channels, identities, routes, skills, providers, authority, and approvals.
- Back up the existing live file.
- Pilot on Harry.
- Test chat-only, review-only, Diagnose Mode, authorized publishing, missing-route, fresh-session, and originating-channel delivery behavior.
- Apply to other agents only after the pilot passes.

## Verification

- Template contains no agent name, host IP, credential, token, stale tracker, `ntn` route, or sample provider assumption.
- Template explicitly includes both operating modes and assignment-scoped write boundaries.
- Template remains below the observed OpenClaw bootstrap ceiling.
- No live agent file or runtime configuration was changed.

## Rollback

Git history and Notion page history preserve the previous sample and allow comparison or rollback.
