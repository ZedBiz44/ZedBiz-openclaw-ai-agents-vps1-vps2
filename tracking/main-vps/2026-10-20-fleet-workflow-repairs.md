# October 20 fleet workflow repairs

Date: 2026-10-20 America/Edmonton | Agent: Cody | Status: Named repairs verified

Jack approved implementation after diagnosis. Existing workstream: https://github.com/ZedBiz44/z-agent-health-report-Skill/issues/6

## Changes and rollback

- Ruby: changed only `/opt/hermes-ruby/backups/config/config.yaml.good.20261020-000013` from root:root to10000:10000. Preserved0640 and content hash. Original metadata/hash in `/root/zedbiz-repairs-20261020/ruby-backup-metadata.json`. Actual `backup_config(..., 'good', keep=1000)` as UID10000 completed without warnings and correctly skipped an identical backup. A separate new verification backup was created and hash/readback/UID10000/mode0640 checked, then only that test backup was removed. Existing backups preserved. No config rewrite, Ruby restart or recursive chown.
- Maggie/Frank: corrected existing daily-journal payloads to use `openclaw gateway call memory.search --params '{"version":2,"agentId":"main","query":"...","maxResults":8}' --json`. This uses selected Hindsight, unlike the sidecar CLI. Actual journal runs retrieved memory, preserved dated history and verified Notion. Frank additionally needed supported exact-title lookup instead of unsupported connector `mode=rows`. Old jobs saved privately under `<state>/repair-backups/20261020/<job-id>.json`.
- Rocky: installed `workspace/scripts/rocky-journal-recall.py`, owner openclaw0750. This read-only helper searches only rocky-vps4-discord, rocky-vps4-telegram, rocky-vps4-webchat; never enumerates legacy banks at runtime or changes banks/provider. Actual service-user probe returned8/0/8 results. Existing daily journal now uses this route, checks optional notes before reading, avoids retired TOOLS.md, and preserves historical coverage gaps. Journal run passed with no failed tools and saved/read back Notion and a local daily note. Rollback: restore saved job payload through native cron edit, then remove the helper only after removing its caller.
- Suzy: report filing completed by Suzy's existing runtime from the saved report. Research page3ffa3e33d58181429d73edb46efa17a4, active allocation ZZZR-30000-100002-050, topic Suzy-Daily-Marketing-Developments. Creator/Primary-Agent Suzy; canonical Research, ZZZR research classification, IM, Trend, Research page type. Weather excluded. Original report delivery temporarily none during filing verification, then restored exactly; schedule preserved. Future payload updates the verified existing record. Prompt and research records are maintained in Notion/runtime, not duplicated here.
- Amanda/Maggie: native system-owned Workshop monitor rejects cron-client edits. Derived OpenClaw2026.10.4 image changes only the built-in empty-collection prompt. Current-directory listing must explicitly use ls({}); empty listing succeeds without leaving sandbox. Docker Compose image reference and derived image make the correction persistent across recreation. Image upgrade must revalidate this patch against upstream. Use the existing op-run startup method to resolve credentials.

## Verification receipts

- Maggie journal:84ff6bfa-9af6-4318-af60-9cd4ec3a8fe5, ok. Actual v2 Hindsight call successful; Notion3ffa3e33d581815eada5de3164dbfae1 read back.
- Rocky journal:5b223d0c-8f38-4223-af69-ef0c253b1b3b, ok. Actual helper ran, no failed tools, Notion3ffa3e33d5818139bdedd77cc9d68460 read back.
- Frank journal: first974bf9aa-67b3-402d-8990-63ae496d5ccf error from unsupported Notion rows lookup; after lookup correction75d80fc0-28c9-4229-86f3-4d90c325fc98 ok.
- Suzy filing:4a321d7a-7c36-4050-8506-9b3b10527145, ok. Final Research fetched independently by Cody; original delivery and schedule read back after restoration.

## Attempts and limitations

Native Workshop cron edit failed as designed; no SQL job mutation attempted. Amanda initial plain-Compose recreate incorrectly passed unresolved op references. Corrected via existing `op run --env-file .env -- docker compose up -d --no-deps amanda`; zero unresolved credential refs, Discord/Telegram authentication and connection probes passed. An early review attempt during startup failed before mail_reader admission was ready. First prompt pilot then stopped because it lacked an explicit directory argument; revised to native current-directory ls({}). All failed receipts preserved.

Historical completeness of memory capture remains unproven; successful retrieval does not establish that every prior conversation was saved. Old journal gaps were not backfilled or invented. Broader security, performance and monitoring findings are outside this repair scope and remain open.

## Final Workshop acceptance

- Amanda: receipt016cd044-e208-4456-aaf9-bd8b9eea800e ok, session1acd22d2-68be-471a-9654-ee88fbf1e79f. Native ls{} succeeded, empty review completed without failed tools. The preceding v2 pilot had still received the v1 job snapshot during startup reconciliation; after verifying the persisted v2 payload the rerun passed.
- Maggie: receipt664176a6-8a0e-46af-a893-843f7719cf4c ok, session8e7908a1-9bca-4222-97a3-c9fa9a1b5381. Native ls{} succeeded, empty review completed without failed tools.
- Amanda image `zedbiz/amanda:2026.10.4-workshop-empty-20261020-v2`, image ID65d66ab4d2aca9d2ba71ef7575800abe847d3162ebf487d542e5bb588e7e701a; module SHA256073cf6acb90c6b6fea9ac50e39edce419918ee1f284732260f3760169b854ea0. This image retains the first empty-handling sentence plus its explicit cwd refinement.
- Maggie image `zedbiz/maggie:2026.10.4-workshop-empty-20261020-v2`, image ID300401eb7a513708e77608199902738c9ebeb97329c7ca953f578a8de64618d0; module SHA256bbee19a8f0cd3b661b1650a99330acda7267df06b7d3bafd02bc862b0591291c. One combined explicit cwd/empty-handling sentence. Both preserve all upstream review instructions and tool restrictions.
- Each Compose file has a `before-workshop-20261020-v2` backup; Amanda also has the original `before-workshop-20261020` backup. To roll back use the original per-agent image reference and existing op-run credential injection, then verify startup, persisted job definition and required channel probes. Do not use Amanda's intermediate v1 image as the original baseline.
- Final Amanda Discord/Telegram and Maggie Discord probes passed, running true, lastError null, eventLoopDegraded false, zero unresolved secret refs. Recreated containers report restartCount0; this is a new baseline, not a claim that no recreations occurred.
- Victor's eight named findings updated atomically to resolved with preserved history and concrete receipts; unrelated findings unchanged. Backup ledger in `workspace/artifacts/fleet-health/repair-20261020/open-findings.before-workflow-repair.json`. Verified repair routes added to existing health-operations.md, including service UID for Ruby diagnostics, op-run recreation, native selected-provider recall and canonical Suzy filing. No new monitoring schedule created.
