# Edith scoped Drive repair build

Date: 2026-09-18 Mountain | Agent: Cody | Status: Deployed to Edith cleanup; two-session pilot in progress

## Source and scope

Use GOG v0.38.1, upstream commit prefix `324f656a`, from `https://github.com/openclaw/gogcli`. The installed shared binary reports that same version/commit. Build with Go 1.26.6 as required by its go.mod. Apply `gog-v0.38.1-copy-timeout.patch` and place `edith_timeout_test.go` in `internal/googleapi/`.

Run `go test ./internal/googleapi`, `go test ./internal/cmd -run Copy -count=1`, and `go build -o gog-edith ./cmd/gog`. Keep the built binary at `/home/node/.openclaw/workspace/edith-drive-repair/gog-edith`.

Install `edith_drive_recovery.py` and the tests into Edith's workspace scripts directory. Run the recovery tests before `install_edith_drive_repair.py`. The installer expects the pre-repair source and refuses unmatched replacements. It is not a general fleet installer. Copy the workload summary and pilot launcher/briefs into the same scripts directory.

Only the cleanup helper's copy command invokes this binary. Its wrapper preserves the existing GOG keyring and email-mode behavior. Normal reads use shared GOG. Neither the shared binary nor credentials change.

## Behavior

- Copy response headers can take up to 120 seconds; the enclosing copy subprocess allows 180 seconds. These are individual request limits, not agent work-session limits.
- Copy requests disable GOG replay, including automatic retries after server errors. A failed copy triggers read-only, paginated reconciliation. Exactly one recent matching destination with source checksum, size, name, parent and Drive must be verified; otherwise the uncertain-write hold remains. Zero search results never authorize another copy.
- Normal output content/access checks still run after recovery. Existing originals, protected IDs and write journals remain intact.
- Evidence hash reuse checks inode, size, modification time and change time; files changed within two seconds bypass reuse, protecting against coarse timestamp races.
- Destination lists are paginated and reused within one executor process. Concurrent out-of-band additions are checked during final reconciliation; this is not a global uniqueness lock.
- Full inventory obtains the same metadata from paginated folder listings rather than a separate get for every file. Three live sample records matched direct get exactly.
- `pending_rows` filters completed proof-plus-archive rows before remote calls. Progress counts are not a completion or reviewer-acceptance verdict.

## Model pilot

Only Terra's runtime mapping changed from openclaw to codex to keep the comparison on Edith's existing execution engine. Existing default model remains unchanged. Each pilot explicitly requests `openai/gpt-5.6-terra`, `medium`, and `--timeout 0`, which the installed CLI documents as disabling the work timeout. No container restart or recurring continuation was used.

Two natural sessions cover exported graphics/documents first, then preserved Photoshop files and final folder review preparation. Compare actual native model/effort, output, elapsed time, retries, token usage, correctness and required operator intervention. Do not call a successful launch a successful pilot.

## Verification and observed limitations

- Recovery tests: five passed, covering exact match, ambiguity, changed/old content, missing checksum, pagination and no write replay.
- GOG Google API tests and copy command tests passed. A server deliberately delaying headers for 31 seconds passed under the patched client.
- All three historical timed-out copies were present on Drive. Journals were reconciled and missing proof records completed without copying again. This includes the older DOCX.
- Native pilot A turn_context confirmed `gpt-5.6-terra` and `medium`.
- Pilot A initially selected all non-PSD rows and rechecked completed work despite the brief. Cody sent a normal in-session correction to use unfinished-row filtering. The `/codex steer` control command was rejected as requiring authorization; no authorization settings were changed. The ordinary task clarification used the existing chat route. This intervention must be included in the efficiency assessment.

## Rollback

Restore the `.before-drive-repair-20260918` backups for `albertawide/work.py`, `execute-pilot.py`, and `execution_guard.py` only while no worker is running. Restore only Terra's prior runtime mapping from `openclaw.json.before-terra-pilot-20260918`; do not overwrite unrelated later configuration. Leave recovered journals and valid file proofs intact. Never re-enable the old periodic dispatcher as part of rollback.

## Continuous phase executor and pilot correction

`edith_run_saved_plan.py` runs only the saved Laughs And Fun exports or Photoshop phase. It filters completed rows before remote calls, keeps one imported executor, records each result, refuses another runner instance and stops at an unresolved exception. It does not schedule or restart an agent. Twelve recovery, duplicate-proof and runner tests passed on Edith's runtime.

The initial Terra session generated a loop that reread completed work. Cody stopped only that read-heavy file subprocess at a verified safe boundary; the Edith model session continued. This cost and intervention belong in the pilot result. The tested phase runner replaces that ad hoc loop in session B.

Exact duplicate aliases get their own source-ID proof tied to the existing canonical copy, with checksum, size, name, path and access checks. Archive moves additionally compare current source checksum and size against the saved proof. Photoshop exception rows keep original names and use metadata/checksum/access verification without downloading or rendering PSD/PSB content.

Inventory uses `gog drive ls --parent ... --fields files(...),nextPageToken`; `search --fields` was tested and rejected because it did not return the required metadata in this installed version. Paginated recursion, empty folders and malformed responses were checked. Generic copy skips GOG's duplicate metadata GET after the executor has verified the source; typed copies retain their MIME check. Copy command tests passed after this change.

These implementation changes were made during the pilot. Results assess the combined workflow and model; they are not a controlled model-only speed comparison. The default model remains unchanged while two real Terra sessions are evaluated.

