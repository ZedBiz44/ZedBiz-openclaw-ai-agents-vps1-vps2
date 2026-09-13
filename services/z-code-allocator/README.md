# Z-Code Allocator Service

Date: 2026-07-21 | Author: Cody | Status: Production

The service is the transactional source of truth for Z-Code allocation. Notion is a non-blocking human-readable mirror processed from the durable `sync_outbox` table.

The `z-code-notion-mirror` companion container drains that outbox and maintains two Notion mirrors:

- `Z-Code-Registry` contains one row per complete Z-Code, the matching Record Title and Notion URL, and a relation to its topic.
- `Z-Code-Topic-Registry` contains one row per Knowledge Core, Knowledge Lane, and Topic Identifier. Name-Key and Topic-Name live there once instead of being copied into every record row.

If Notion is unavailable, events remain in SQLite and retry later; allocation continues normally.

Historical records imported before the mirror was enabled can be idempotently backfilled from authoritative SQLite. Test one record first, then require a complete reconciliation:

```bash
docker exec z-code-notion-mirror python -m app.backfill_registry --limit 1
docker exec z-code-notion-mirror python -m app.backfill_registry --require-complete
docker exec z-code-notion-mirror python -m app.backfill_registry --refresh-existing --require-complete
```

Backfilled historical rows are labelled `Source = Bootstrap`; normal live events remain `Source = Allocator`.

Allocation starts disabled. Import and verify all existing Notion Z-Codes through `POST /v1/admin/bootstrap`, then set `ZCODE_ALLOCATION_ENABLED=true` and restart the container.

## Local Development

```powershell
python -m pip install -r requirements-dev.txt
$env:ZCODE_DATABASE_PATH = "$PWD/data/zcode.db"
$env:ZCODE_API_KEYS_JSON = '{"marsha":"local-marsha-key","edith":"local-edith-key"}'
uvicorn app.main:create_default_app --factory --reload --port 8788
pytest -q
```

## Core Rules

- Every allocation runs inside `BEGIN IMMEDIATE` and the insert occurs in the same transaction.
- `request_id` makes retries idempotent.
- Every issued Topic Identifier and complete Z-Code is permanently reserved in durable history tables.
- Returned Z-Codes are never reused, including stale, abandoned, reassigned, withdrawn, or deleted records.
- A reassigned Z-Code remains a historical alias that resolves to its current replacement.
- Integer suffixes are formatted with leading zeros only when the complete Z-Code is assembled.
- Brief uses `010-019`, Biz-Plan uses `020-049`, and other Page Types use `050-999`.
- Name-Key conflicts across cores or lanes enter Edith's review queue.
- Topic reassignment changes every related Z-Code and records the previous code as an alias.
- An administrator can rename a topic once; the previous Name-Key remains an alias to the same topic.
- The Notion mirror reads the actual page title into `Record-Title` and connects each record to its single Topic Registry row.
- Notion failures never block allocation; mirror events remain in `sync_outbox` until completed.

## Authentication

Provide one unique bearer token per agent in `secrets/api_keys.json`. Never commit the real file.

Generate the initial file without printing credentials:

```bash
python scripts/generate_api_keys.py secrets/api_keys.json edith marsha frank ruby harry suzy
```

## Browser Administration

The normal write-capable dashboard is served by `z-code-admin`. It permits only controlled metadata edits and mirror resyncs; each action creates an audit event and a Notion outbox event.

- Public path: `https://edith.zbiz.ca/_zedbiz-zcode-admin/`
- Username and password: `ZCODE_ADMIN_USERNAME` and `ZCODE_ADMIN_PASSWORD` in the server `.env`
- The raw SQLite editor is `z-code-db-emergency`, uses a separate password, and is disabled unless its Docker Compose profile is explicitly started.

Raw editing requires a live SQLite backup, stopped allocator and mirror containers, foreign-key checks, `PRAGMA quick_check`, and a complete Notion reconciliation before allocation resumes. The raw editor supports writes by design and must never be left running after maintenance.

## Primary Endpoints

- `POST /v1/allocate`
- `POST /v1/confirm`
- `GET /v1/status/{request_id}`
- `GET /v1/lookup?name_key=...`
- `GET /v1/admin/queue`
- `POST /v1/admin/reassign-topic`
- `POST /v1/admin/rename-topic`
- `POST /v1/admin/stale/sweep`
- `GET /v1/admin/outbox`
- `GET /v1/admin/metrics`
- `POST /v1/admin/bootstrap`
- `GET /health`

