# 2026-07-20 - Feature Change - Z-Code Allocator Pilot

## Summary

- **Date:** 2026-07-20 Mountain Time
- **Added By:** Cody
- **System:** VPS1 shared services, VPS1/VPS2 OpenClaw, VPS3 Hermes
- **Feature Status:** testing

## Feature Purpose

- Issue Z-Codes atomically from one fast server service.
- Prevent duplicate Topic Identifiers and suffixes when several agents create records concurrently.
- Reduce Notion lookups and LLM context usage.

## Implementation Notes

- Files changed:
  - `services/z-code-allocator/`
  - `skills/request-z-code/`
  - `ai-agent-sops/zedbiz-main-vps/z-code-allocator-service.md`
- Service stack: FastAPI, SQLite, Uvicorn, Docker Compose.
- Safeguards: `BEGIN IMMEDIATE`, uniqueness constraints, request idempotency, permanent consumption of stale/abandoned codes, audit events, reassignment aliases, durable mirror outbox, per-agent credentials.
- Medium-confidence peer feedback was reviewed. Atomicity, idempotency, integer suffixes, audit history, versioned endpoints, health, metrics, and client retry handling were adopted.
- `force_new_topic` and reservation reuse were rejected because they conflict with the unique Name-Key and never-reuse policies.

## Verification

- Local automated tests: six passed.
- Covered allocation ranges, idempotency, confirmation, review conflicts, stale and failed non-reuse, concurrent uniqueness, reassignment, and authentication.
- Skill validation: passed.
- Container and live pilot verification: pending.
- Live deployment review found that an empty allocator could collide with existing Notion Z-Codes. A bootstrap import endpoint and default-off allocation lock were added before any live code was issued.

## Rollback Note

- Stop and remove the allocator container and Caddy route.
- Preserve the SQLite database for audit.
- Remove the pilot skill from the tested agent only.

## Links

- Notion journal: pending final deployment record
- Related commit: pending
