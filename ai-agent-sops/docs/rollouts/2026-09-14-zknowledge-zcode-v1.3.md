# Z-Knowledge And Z-Code Version 1.3 Rollout

Date: 2026-09-14 | Agent: Cody | Status: Resolved

## Production Service

- GitHub release: merged PR 353, commit `d1231675dc9099859a3589e55061583e1ad86a64`.
- Live image: `zedbiz-z-code-allocator:1.3.0` for allocator, admin, and mirror.
- Pre-upgrade backup: `/opt/zedbiz-services/z-code-allocator/backups/zcode-before-v1.3-20260914.db`.
- Preserved 457 records and 155 topics.
- SQLite `quick_check` returned `ok`; `foreign_key_check` returned no rows.
- Added `topic_name` and `record_title` columns.
- Imported 155 Topic Names and 455 existing Record Titles from the verified Notion registries.
- Two Record Titles remain blank: one abandoned reservation has no Notion page and one active historical test record points to a page that is not found.
- Missing linked pages use the allocator's last known Record Title so one deleted page cannot stop registry reconciliation.
- Automated tests: 19 passed.

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

## Notion Connection Resolution

- Reused the existing `Hermes-Notion-API` connection; it already had access to both registries.
- Replaced the rejected VPS1 connection key without displaying or committing it.
- PR 358 removed the obsolete `Registry-Entry` write and matched the live `Z-Code` field.
- All 68 waiting changes completed; the final waiting count is zero.
- Complete read-only reconciliation passed:
  - 457 SQLite records and 457 Notion registry rows.
  - 155 topics with 155 Topic Names, 155 Name-Keys, and 155 unique Topic Keys.
  - All 457 registry records have a Topic relation.
  - No duplicate, missing, or extra Z-Codes.
- GitHub issue 321 is closed as completed.

## Rollback

- Restore the pre-upgrade SQLite backup only if schema or data integrity fails.
- Redeploy the previous committed service image and committed skill package.
- Do not delete issuance or alias history.
- Do not use Notion as a reverse-sync workaround.
