# Edith file execution safeguard

Date: 2026-09-17 | Agent: Cody | Status: Operational correction for Edith only

## Purpose and boundary

This module enforces saved content decisions in the existing folder-cleanup executor. It does not classify files and cannot prove that an agent understood content. Ruby independently reviews the final work. Existing accepted copies and historical plans are preserved. It does not authorize changes to the held credential document or protected subtrees.

Only `copy`, planned `mkdir`, and verified-original-to-archive `move` are supported writes. Other write operations stop. Reads remain available. The module is integrated at the shared `albertawide/work.py` GOG boundary used by the existing executors. It is not an OS-wide restriction on all Drive clients; the work instructions prohibit bypassing this boundary.

## Prepare a folder for writing

- Finish the installed skill's whole-folder `prewrite-plan.json`, using successful inspection of each file. Existing path names may describe business context but cannot supply unobserved content classifications.
- Preserve `initial-inventory.json`. Verify current source revisions before copying, using the existing executor's source metadata checks.
- Save `plan-review.json` after reviewing representative content across the planned asset types. Include `reviewer`, UTC `reviewed_at`, `representative_content_checked: true`, SHA-256 hashes of the exact plan and inventory as `plan_sha256` and `inventory_sha256`, `archive_paths`, and a nonempty `pilot_source_ids` list naming the first populated section.
- Its `evidence` object is keyed by each non-held source ID. Each value contains `source_id`, the absolute `path` to that file's actual inspection evidence, and its SHA-256 as `sha256`. Evidence must exist in the private folder-cleanup evidence area. Contact sheets are allowed only with the decision table's source-to-position mapping; a sibling preview is not the original's evidence. Do not copy secret-bearing excerpts into shared reports.
- Executor state maps exact relative destination paths to returned Drive folder IDs. The safeguard refuses alternate names or unknown parents. After the pilot, save the genuine `first-section-review.json` with `passed` and nonempty source-linked `files`; it is a producer self-check, not Ruby's final acceptance.
- Existing cached source inspection may be reused only after confirming its source revision still matches. A changed plan or evidence invalidates the review hashes and requires a new review record; retain the earlier record for audit.

## Uncertain writes and recovery

Each mutation writes a durable intent before the remote call. A successful result is saved before returning to the caller. Repeating an identical confirmed call returns the saved result without making another copy. A timeout, cancellation or killed process leaves an intent/uncertain record and blocks automatic replay.

Reconcile that operation read-only against live Drive: compare source ID/revision, exact destination parent/name, returned object ID if known, checksum/size and permissions. If exactly one valid result exists, preserve the original journal and record the verified result and evidence before resuming. If the outcome is ambiguous, Amanda owns the exception; do not guess or delete duplicates. Absence of a response is not proof the write failed. There is deliberately no automatic clear-and-retry command.

## Deployment and rollback

Install the module in Edith's workspace scripts, then wrap the shared executor's original GOG function with `execution_guard.run(P, ROOT, args, lambda: _gog(*args), check_file_plan)` from the installed Files & Folders checker. Back up the exact original `work.py` before editing. Restart no container or active worker. Update the recovery work instructions so future executors use this boundary. Roll back only by restoring that exact backup after pausing affected writes; inspection can continue.

The tests use synthetic data and no Drive mutations. They cover exact decisions, invented names, unknown parents/source IDs, changed/missing evidence, changed plans, failed inspections, empty pilots, protected IDs, archive prerequisites, duplicate notifications, uncertain responses, interruptions and destructive command rejection. Run the existing skill tests separately. A passing suite is not a real mixed-content quality acceptance.
