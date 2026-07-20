# Z-Code Allocator Service

Date: 2026-07-20 | Author: Cody | Status: Pilot

The service is the transactional source of truth for Z-Code allocation. Notion is a non-blocking human-readable mirror processed from the durable `sync_outbox` table.

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
- Returned Z-Codes are never reused, including stale and abandoned reservations.
- Integer suffixes are formatted with leading zeros only when the complete Z-Code is assembled.
- Brief uses `010-019`, Biz-Plan uses `020-049`, and other Page Types use `050-999`.
- Name-Key conflicts across cores or lanes enter Edith's review queue.
- Topic reassignment changes every related Z-Code and records the previous code as an alias.
- Notion failures never block allocation; mirror events remain in `sync_outbox` until completed.

## Authentication

Provide one unique bearer token per agent in `secrets/api_keys.json`. Never commit the real file.

Generate the initial file without printing credentials:

```bash
python scripts/generate_api_keys.py secrets/api_keys.json edith marsha frank ruby harry suzy
```

## Primary Endpoints

- `POST /v1/allocate`
- `POST /v1/confirm`
- `GET /v1/status/{request_id}`
- `GET /v1/lookup?name_key=...`
- `GET /v1/admin/queue`
- `POST /v1/admin/reassign-topic`
- `POST /v1/admin/stale/sweep`
- `GET /v1/admin/outbox`
- `GET /v1/admin/metrics`
- `POST /v1/admin/bootstrap`
- `GET /health`
