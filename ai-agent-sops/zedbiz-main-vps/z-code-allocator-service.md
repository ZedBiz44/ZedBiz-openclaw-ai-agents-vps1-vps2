# Z-Code Allocator Service SOP

Date: 2026-08-27 | Author: Cody | Status: Active

## Purpose

Issue unique Z-Codes through one transactional service so authorized agents on VPS1, VPS2, VPS3, and VPS4 never select the same Topic Identifier or record suffix.

The human-and-agent allocation workflow, copy-ready prompts, imported-content rules, and integration contract for broader Content Master Database record-creation skills are maintained in the live [Z-Code Allocation SOP](https://app.notion.com/p/3a3a3e33d58180f7bf5ed69f0a398b84).

## Source Of Truth

- Runtime allocation state: `/opt/zedbiz-services/z-code-allocator/data/zcode.db` on VPS1.
- Code and configuration: `services/z-code-allocator/` in this repository.
- Agent workflow: [`z-code-allocation-Skill`](https://github.com/ZedBiz44/z-code-allocation-Skill), deployed from its validated `dist/z-code-allocation` package.
- Notion: asynchronous human-readable mirror only; it must never block allocation.

## Operating Rules

- Agents must call the allocator before creating a final Z-Knowledge database record.
- Agents must not calculate or increment codes themselves.
- Use the same `request_id` when retrying an allocation.
- A returned Z-Code is permanently consumed, including stale and abandoned reservations.
- Confirm the code only after the Notion page exists.
- Report a failed page creation so the reservation becomes `abandoned`.
- Core/lane conflicts enter Edith's review queue.
- Edith is the only initial admin for review resolution and topic reassignment.

## Pilot Endpoint

The initial route reuses Edith's existing HTTPS hostname:

`https://edith.zbiz.ca/_zedbiz-zcode`

A dedicated `zcode.zbiz.ca` hostname may replace it after DNS is created. Agent wrappers use `ZCODE_ALLOCATOR_URL`, so the change does not require rewriting the skill.

## Deployment

- Live directory: `/opt/zedbiz-services/z-code-allocator`
- Container: `z-code-allocator`
- Docker network: `openclaw`
- Internal port: `8788`
- Persistent volume: `./data:/data`
- Secret file: `./secrets/api_keys.json`, mode `600`, never committed

Deploy from the repository directory copied to the live path:

```bash
docker compose build
docker compose up -d
docker compose ps
docker logs --tail 100 z-code-allocator
```

## Verification

- `GET /health` returns `ok: true` without authentication.
- Requests without a valid agent token return `401`.
- Repeating an allocation with the same `request_id` returns the same Z-Code.
- Concurrent requests for one topic return unique suffixes.
- Stale or failed reservations are never reused.
- A conflicting Name-Key returns `requires_review` and a queue ID.
- Topic reassignment changes all related complete Z-Codes and preserves aliases.
- Notion outbox failures do not stop allocations.
- Before first allocation, all existing Notion Z-Codes are imported through the admin bootstrap endpoint and the service remains locked with `ZCODE_ALLOCATION_ENABLED=false`.

Every client must also pass an authenticated lookup-only check. A genuine miss must return `found: false` with exit `0`; authentication, configuration, malformed-command, transport, and server failures must remain nonzero.

## Client Enrollment

- Give every agent a unique registered key. Never share another agent's credential.
- Store the allocator registry only in `/opt/zedbiz-services/z-code-allocator/secrets/api_keys.json` with mode `600`.
- Store each client credential in that agent's protected runtime configuration and expose only `ZCODE_ALLOCATOR_URL`, `ZCODE_API_KEY`, and `ZCODE_AGENT_NAME` to its process.
- Back up the registry and the client's prior service configuration before enrollment.
- Restart the allocator after a registry change and reload or restart the client service after its environment changes.
- Verify configuration by checking variable names and presence only. Never print values.
- Use a deliberately nonexistent Name-Key for the first authenticated test. Do not allocate merely to prove connectivity.

Rocky uses `/home/openclaw/.openclaw/.env.zcode` with mode `600` and the user-service drop-in `/home/openclaw/.config/systemd/user/openclaw-gateway.service.d/zcode-allocator.conf`.

## Backup

Use SQLite's online backup method or stop the container briefly before copying the database. Back up the database and WAL files together when copying a live database directly.

## Failure Handling

- If the allocator is unavailable, agents may keep working notes but must not invent a code or create a final record.
- If Notion mirroring fails, leave the outbox event pending or retry; do not roll back the allocation.
- If a reservation expires, mark it stale and alert Edith. Do not reuse it.
- If the Z-Knowledge-Core was wrong, Edith reassigns the complete topic through the admin endpoint.

## Rollback

- Remove the Caddy route and reload Caddy.
- Run `docker compose down` in the live directory.
- Preserve `data/zcode.db` and the secret file for investigation.
- Agents revert to draft-only record preparation; do not resume manual numbering without Jack's approval.
