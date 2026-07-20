# 2026-07-20 - Feature Change - Z-Code Allocator Pilot

## Summary

- **Date:** 2026-07-20 Mountain Time
- **Added By:** Cody
- **System:** VPS1 shared services, VPS1/VPS2 OpenClaw, VPS3 Hermes
- **Feature Status:** deployed, enabled, piloted, and rolled out to the six approved agents

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

- Local automated tests: seven passed.
- Covered allocation ranges, idempotency, confirmation, review conflicts, stale and failed non-reuse, concurrent uniqueness, reassignment, and authentication.
- Skill validation: passed.
- The Docker container is running and healthy on VPS1.
- Internal and public HTTPS smoke tests passed for health, authentication rejection, and the bootstrap safety lock.
- Pilot endpoint: `https://edith.zbiz.ca/_zedbiz-zcode`
- Allocation is enabled through an explicit live environment setting; the source-controlled default remains disabled for safe fresh deployments.
- Live deployment review found that an empty allocator could collide with existing Notion Z-Codes. A bootstrap import endpoint and default-off allocation lock were added before any live code was issued.
- The corrected Notion inventory was imported and verified: 349 distinct Z-Codes across 80 topic groups.
- Final Notion scan found zero duplicate codes and zero invalid formats.
- Marsha completed the one-agent pilot by allocating `Z1ST-80001-100001-010`, creating the Notion Tools record, confirming its exact page URL, and replaying the original request without receiving a second code.
- The agent skill was then rolled out to Edith and Marsha on VPS1, Frank, Harry, and Suzy on VPS2, and Ruby on VPS3.
- Every agent completed an authenticated lookup of the same confirmed allocator record.
- Added a Node.js client helper for OpenClaw containers while retaining the Python helper for Python-based runtimes such as Hermes.
- Temporary credential-transfer files were removed from all three servers and the local workstation after rollout.
- Created the `Z-Code-Registry` database under `Z-Knowledge-Master-Databases` and deployed a separate non-blocking mirror worker container.
- The mirror drained both pilot events, upserted one Active registry row, and left zero pending outbox events.
- Verified the registry row contains the exact Z-Code, topic, suffix, source record URL, request ID, and Marsha ownership.
- Created and verified the comprehensive Notion owner and repair manual at `https://app.notion.com/p/3a3a3e33d581803e8c40ed6621b341ce`.
- The manual records architecture, ownership, sources of truth, allocation rules, agent installations, endpoints, database design, secrets handling, backup/restore procedures, troubleshooting, change control, verification, and handoff requirements.
- Created a post-go-live SQLite recovery backup containing 81 topics and 350 records: `/opt/zedbiz-services/z-code-allocator/data/backups/zcode-post-go-live-20260720-1548MDT.db`.
- Verified the new backup with `PRAGMA quick_check=ok`; SHA-256 is `b8a4149b9f3babff933092f39a93a24162d2205b83c2d64652ca8e0e3ba51d4c`.
- Detailed bootstrap record: `activity-logs/2026-07-20-z-code-bootstrap-import.md`

## Rollback Note

- Stop and remove the allocator container and Caddy route.
- Preserve the SQLite database for audit.
- Restore each agent's dated environment backup, remove the `request-z-code` skill, and restart that agent.

## Links

- Notion journal: `https://app.notion.com/p/3a3a3e33d581817dbcaee4f8736e4df8`
- Source branch: `codex/z-code-allocator`
- Confirmed Notion record: `https://app.notion.com/p/3a3a3e33d58181d29936e6047dfbfc11`
- Notion registry: `https://app.notion.com/p/89267d1e18f84f669269c900dc730b08`
- Owner and repair manual: `https://app.notion.com/p/3a3a3e33d581803e8c40ed6621b341ce`
- Human and agent allocation SOP: `https://app.notion.com/p/3a3a3e33d58180f7bf5ed69f0a398b84`

## Human And Agent SOP

- Replaced the short Notion allocation outline with a complete SOP for people and agents.
- Added raw-import, Brief, Biz-Plan, Research, multiple-record, duplicate, stale, failed, review, and reassignment workflows.
- Added copy-ready human and agent prompts, a completion-report template, and final quality-control checklist.
- Defined the integration boundary for Marsha's future Content Master Database record-creation skill: the broader skill owns intake, research, classification, database fields, relations, and content quality, while the existing `request-z-code` skill remains the only allocation mechanism.
