---
name: request-z-code
description: Reserve, look up, confirm, or check authoritative Z-Codes through the centralized ZedBiz allocator. Use whenever an agent is about to create a Z-Knowledge Notion record, needs the existing code for a Name-Key, must confirm a newly created Notion page, or must report a failed record creation without reusing the code.
---

# Request Z-Code

Use the bundled `scripts/request_z_code.mjs` on OpenClaw/Hermes agents. The Python helper is retained for Python-based runtimes. Never calculate, guess, or increment a Z-Code manually.

## Before Creating A Record

- Determine the proposed Name-Key, Z-Knowledge-Core, Knowledge Lane, and Page-Type.
- Search the allocator with `lookup` when the Name-Key may already exist.
- Run `allocate` before creating the Notion record.
- Keep the returned `request_id`; retries with the same ID return the same reservation.
- If the service returns `requires_review`, stop record creation and give Edith the `queue_id`.
- If the allocator is unavailable, keep research as a draft but do not invent a Z-Code or create a final database record.

## Create And Confirm

- Use the returned complete Z-Code exactly as provided.
- Create the Notion record using the approved Name-Key and classification.
- Run `confirm` with the completed Notion page URL.
- If page creation fails, run `failed` with the Z-Code and reason. The code becomes abandoned and is never reused.

## Commands

```bash
node scripts/request_z_code.mjs lookup --name-key Biz-Plan-Template

node scripts/request_z_code.mjs allocate \
  --request-id marsha-20260720-biz-plan-template \
  --name-key Biz-Plan-Template \
  --core Z1ST \
  --lane 80001 \
  --page-type Biz-Plan

node scripts/request_z_code.mjs confirm \
  --z-code Z1ST-80001-100043-020 \
  --notion-url https://www.notion.so/example

node scripts/request_z_code.mjs failed \
  --z-code Z1ST-80001-100043-020 \
  --reason "Notion page creation failed"

node scripts/request_z_code.mjs status \
  --request-id marsha-20260720-biz-plan-template
```

The runtime must provide:

- `ZCODE_ALLOCATOR_URL`
- `ZCODE_API_KEY`
- `ZCODE_AGENT_NAME`

Do not print or store the API key in a page, log, prompt, or GitHub file.
