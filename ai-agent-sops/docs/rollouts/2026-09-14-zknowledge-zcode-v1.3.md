# Z-Knowledge And Z-Code Version 1.3 Rollout

Date: 2026-09-14 | Agent: Cody | Status: In Progress

## Production Service

- GitHub release: merged PR 353, commit `d1231675dc9099859a3589e55061583e1ad86a64`.
- Live image: `zedbiz-z-code-allocator:1.3.0` for allocator, admin, and mirror.
- Pre-upgrade backup: `/opt/zedbiz-services/z-code-allocator/backups/zcode-before-v1.3-20260914.db`.
- Preserved 457 records and 155 topics.
- SQLite `quick_check` returned `ok`; `foreign_key_check` returned no rows.
- Added `topic_name` and `record_title` columns.
- Imported 155 Topic Names and 455 existing Record Titles from the verified Notion registries.
- Two Record Titles remain blank: one abandoned reservation has no Notion page and one active historical test record points to a page that is not found.
- Automated tests: 18 passed.

## Skill Releases

- `z-record-knowledge` PR 4: requested output selects Page-Type; no automatic Brief; no direct small-bite call.
- `z-code-allocation` PR 3: permanent retirement, aliases, controlled rename/reassignment, registry verification, and optional Record Title confirmation.
- `z-notion-knowledge-publish` PR 2: governed Z-Code, Record Title, Topic relation, allocator authority, and read-back verification.

## Pilot And Fleet

- Edith was the pilot.
- Fresh Edith test correctly refused Z-Code reuse, explained aliases and permanent retirement, named allocator/Topic Registry/Z-Code Registry/alias/record verification, and respected a review-only no-write instruction.
- Deployed matching files to 11 VPS1 agents, Frank, Harry, Suzy, Ruby, and Rocky.
- Matching SHA-256 values:
  - `z-code-allocation`: `f6c87cde719d0815dddc8eeb26a3d76b66f3e129ea23a66f5606ede816b5e426`
  - `z-record-knowledge`: `65d1277d618604064e89598e7827cb27220a0ce4b0c1a78d314839254be56333`
  - `z-notion-knowledge-publish`: `c7374f55a9f9001b5cd9ec0d92ec61cbda9802eb82097ed7f1ffc588f3b47709`
- Removed the older research-only small-bite gate and made it an independent everyday rule.
- Replaced Victor's unsafe automatic-publication rule with scope-aware skill routing.
- VPS2 services, Ruby maintenance restart, and Rocky gateway restart completed successfully.

## Open Credential Issue

- `z-code-notion-mirror` receives Notion HTTP 401.
- All checked VPS1 `NOTION_API_TOKEN` and `NOTION_API_KEY` values return 401.
- The available local 1Password service account sees only `special-agents`, which contains no Notion credential.
- The version 1.3 circuit breaker safely pauses all 68 queued events after an authentication failure.
- Complete repair requires an authorized new or renewed Notion integration credential with access to both registries. Track this in issue 321.

## Rollback

- Restore the pre-upgrade SQLite backup only if schema or data integrity fails.
- Redeploy the previous committed service image and committed skill package.
- Do not delete issuance or alias history.
- Do not use Notion as a reverse-sync workaround.

