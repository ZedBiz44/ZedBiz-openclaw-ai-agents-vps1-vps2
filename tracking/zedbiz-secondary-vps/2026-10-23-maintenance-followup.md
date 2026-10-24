# VPS2 maintenance follow-up — 2026-10-23

Owner: Cody. Scope approved by Jack after the OpenClaw upgrade and maintenance audit. Evidence: issue #477 / PR #478. This record supersedes the initial core-upgrade record's Hindsight version and reboot-pending statements after final verification below.

## Applied updates

- OpenClaw 2026.10.6 and Node 24.22.1 remain deployed on Frank, Harry and Suzy. The ten approved Ubuntu/package updates were applied in the initial upgrade.
- Shared Asana HTTP MCP now pins SDK 1.32.2; lockfile updates include body-parser 2.4.0, fast-uri 3.1.9, ip-address 10.7.4 and zod 4.6.7. Typecheck, build, XML valid/invalid probes and production npm audit passed with zero advisories. Frank's isolated port-4917 pilot passed before the three live lanes restarted in sequence. All lanes exposed 47 tools and passed their own identity/task read checks.
- Stable tools: gog 0.47.0, gh 2.103.2, ntn 0.23.25, summarize 0.25.3, mcporter 0.16.0, Codex CLI 0.164.0 and Gemini CLI 0.65.0. Official gog/gh assets were checksum verified. The gog wrapper retains each agent's private credential store and draft-only safeguard.
- Frank then Suzy upgraded Hindsight 1.0.0 to 1.2.0 after protected stopped-state backups and isolated rehearsals. Both retain their original banks and automatic recall/retention. Set memoryMode=context and allowKnowledgeDelete=false to preserve the previous actual automatic-only behavior: the old enableKnowledgeTools field did not expose manual tools in 1.0.0. Version 1.2 declares ten tool contracts; its context-mode runtime gate suppresses their registration. No new manual deletion access was enabled.
- Harry's Mem0 1.2.1, existing guards and IMAP correction remain intact. Current Caddy/Himalaya were retained; unrelated npm/TypeScript major upgrades were not introduced. Ubuntu's vendor-phased cloud-init remains deferred.

## Verification and resolved attempts

All three agents passed real internal, read-only GPT-6.1-Sol turns before reboot with rerouted=false: memory recall, own Asana identity, Notion SOP fetch, Google Drive list and all seven tool versions. No external test messages were sent.

Hindsight rehearsal initially encountered an uncopyable 1Password Unix socket; the running service was restored immediately and the rehearsal was built from the checked archive instead. Setting new config fields before upgrading failed the old plugin schema; the corrected order upgrades first, then applies the new fields. An immediate startup probe hit connection-refused before readiness; bounded readiness polling resolved it. Suzy's active work was allowed to drain before cutover. These were handled without changing credentials, model routing or memory banks.

## Recovery and cleanup

Protected follow-up evidence and rollback material: /root/cody-vps2-followup-20261023. Initial checked core archives/auth recovery remain in /root/cody-vps2-20261023. Follow-up retention includes Asana's prior application, original global CLI bundle, previous gog wrapper/binary, previous gh package and both Hindsight stopped-state archives plus fresh activation SQLite/config snapshots.

Removed 35.779 GiB of core candidate/rehearsal/extracted duplicates only after rechecking original archive SHA256 hashes and active-process/symlink references. Removed another 7.515 GiB of follow-up candidate copies after both Hindsight acceptances and archive checks. Cleared npm download cache and apt package cache. Active agent data, browser caches, credentials and business files were retained.

Historical maintenance directories are consolidated into protected compressed archives under /root/zedbiz-maintenance-archives/2026-10-23. Each archive must pass compressor integrity and tar content comparison plus SHA256 recording before its original directory is removed. The manifest records exact paths, sizes and hashes. The first archives use gzip; remaining folders use the already installed Zstandard tool for faster compression. The initial orchestrator was paused while its current gzip verifier finished, then stopped and replaced by the resumable version; existing completed archives were retained and checked again. Retention review preserves recovery history; no unattended future deletion policy was added.

The dated scripts in scripts/ are execution evidence for this maintenance, with explicit staging paths and prerequisites. They are not generic rerunnable SOPs. Maintained procedures remain in Notion. Restoring old state can discard later work and requires preserving current state first.

## Final verification

Completed. Nine historical/test folders totaling 78.792 GiB were retained in 48.143 GiB of checked archives, reclaiming another 30.649 GiB. The retired /opt/zedbiz-tests/mem0-clean-20260929 directory is included. Current release rollback files remain separate. Final disk: 54% used, 89 GiB available (193 GiB filesystem), versus approximately 89% used / 23 GiB free before the approved cleanup.

The reboot changed boot ID from 22148c68-508d-4aa0-98af-6becaa13020f to 6e26b5e3-3bb1-41fe-b058-32c38d1b8a7f. All agents, their Asana services and Caddy started automatically. Kernel 6.8.0-147-generic matches the installed expected kernel. needrestart lists no pending service/session restarts; no failed units. Only phased cloud-init remains deferred.

Initial gateway checks during startup timed out at the default ten-second limit; Harry's plugin startup took about three minutes before normal operation. A memory recall initially timed out, followed by successful injected memories and explicit mem0_search. Harry recorded 440 memory.high pressure events during warm-up, but no memory.max, OOM or OOM-kill events; no service restarted. This is an observed startup delay, not a claim of long-term performance validation. No memory limits were changed. All subsequent public/CLI health, Discord, plugin, Asana identity/task and schedule checks passed. Retained business schedules: Frank 6, Harry 6, Suzy 7.

All three then completed actual postboot GPT-6.1-Sol turns with rerouted=false and successful memory, own Asana identity, Notion SOP fetch, three Google Drive results and all seven CLI version checks. Harry again noted the previously absent TOOLS.md; it did not prevent any requested check. Terminal run IDs and machine-readable host verification are in 2026-10-23-followup-verification.json. Archive sizes/checksums are in 2026-10-23-recovery-archive-manifest.json. Sensitive raw logs remain protected on VPS2.

GitHub publication read-back caught output truncation in the first lockfile transfer. Commit 670d386 restored the complete lockfile, and all changed/new source blob hashes were checked against the worktree before proceeding. Deployed files were unaffected. PR #478 remains the review branch and is not merged to main.
