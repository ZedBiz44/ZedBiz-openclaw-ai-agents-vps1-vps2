# Mem0 agent profile placement verification

Date: 2026-09-29 | Agent: Cody | Status: Deployed and verified

## Result

Harry, Edith and Terry now receive the current USER.md profile through AGENTS.md, SOUL.md and IDENTITY.md. USER.md is unchanged as a reference. Existing role, approval, privacy, source-of-truth and completion rules remain. Terry and Edith retain their September 29 condensed operating files. No connector, model, hook, service or bootstrap-limit changes; no restart.

## Authority and source

Jack requested review of chat 01a0ed78-0b2e-77a1-8c2f-b7345dea07f9 and implementation for all three. The prior plan required Harry first, then Edith/Terry, and save/search acceptance. Harry passed profile and memory acceptance before either other deployment.

Current live files were the baseline. Terry/Edith AGENTS matched main commit 7e5b4daa. Harry's live file contained later memory, journal and native Notion rules absent from main; these are preserved in the committed candidate. USER profile text was moved without re-researching Jack's biography or rewriting business direction.

Candidate commit: 86fdaaa012e7e230b032610bb7b70586e52f64fa. PR #431. Main is pending review/merge; the branch contains the exact deployed files.

## Placement and preservation

- AGENTS.md: opportunity priority, sending authority, agent-relevant expectations and profile-maintenance routing. Existing operating modes and research/validation/completion rules cover the equivalent USER instruction.
- SOUL.md: answer-first communication, tone, separate Marketing Jack/Farmer Jack voices and Style Manifesto link.
- IDENTITY.md: clearly labelled employer/user section, location, background, business direction, dated focus split and profile sources.
- USER.md: unchanged bytes and permissions, all four files backed up externally per agent.
- Registers map every USER bullet. Existing file material is retained except exact routing phrases redirected from USER.md to loaded destinations. No role cleanup or unrelated rewrite performed.

## Validation

All run OpenClaw 2026.9.4 through the Codex harness. Harry used configured GPT-5.6 Sol; Edith and Terry used configured GPT-6 Astra. No fallback. Each context test used a unique new session ID and returned with no tool calls. Each correctly answered profile, voice, focus meaning, sending boundary, Diagnose boundary, source routing, role expectations, private-context and final-file-rule checks.

SOUL.md and IDENTITY.md reports explicitly show truncated=false and full injection. AGENTS.md reports native_unverified with null injection count/truncation, so its full injection is NOT claimed. Correct profile rules and final-section behavior provide practical acceptance evidence. USER.md remains absent from the automatic file report.

All three memory tests used actual memory_add, mem0_get and mem0_search. Runtime terminal receipts show all three successful tool names, toolSummary reports three calls and zero failures, and returned record IDs and exact-marker matches are saved in verification.json. Each test creates one clearly labelled harmless test record. No local-memory substitute or unrelated business action was requested.

Final readback matched all nine candidate hashes and original permissions; all three USER hashes unchanged. Harry active/NRestarts=0; Edith/Terry running/healthy/restart count 0. External backups passed hash, ownership and copy-to-temporary-directory restoration checks. Rollback not needed.

## Size and limits

AGENTS.md including trailing newline: Harry 16733 to 17556; Edith 13523 to 14362; Terry 13997 to 14788 UTF-16 characters. Their limits are 24000, 20000 and 20000 respectively. Exceeding the 14000 preferred guideline is a documented narrow exception: preserve the newly condensed files and existing safeguards while adding the requested profile. Tail behavior passed. No limit raised. Per-file before/after counts, hashes, registers and analysis accompany this report.

## Attempts and limitations

- Corrected a code-search argument mismatch and candidate section parser before any production write.
- A local Drive file lock required patch-tool editing instead of a pipeline write.
- Windows command-length failure was resolved by streaming the deployment script through SSH stdin. Template replacement syntax errors were corrected before execution. Failed attempts did not alter live files.
- Legacy session JSONL and trajectory-path probes were absent for these current sessions. Verification uses the returned runtime terminal receipts, tool summaries, context reports and behavior, not an invented transcript readback.
- Existing profile sources and retained runtime rules can contain older wording; broad profile revision and rule cleanup were outside this placement task.

## Recovery

Backup paths and hashes are in verification.json. Restore only AGENTS.md, SOUL.md and IDENTITY.md from the named agent's backup, preserving file owner/mode, then test a new session. USER.md need not be restored because it was not changed. Restore route was rehearsed to a temporary directory without overwriting production.

## References

- Workstream: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/425
- PR: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/431
- Official workspace reference checked: https://docs.openclaw.ai/concepts/agent-workspace
