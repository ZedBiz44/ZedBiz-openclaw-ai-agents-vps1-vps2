# Health follow-through repairs — October 12, 2026

Cody, with Victor coordinating Amanda investigation. Parent: https://github.com/ZedBiz44/z-agent-health-report-Skill/issues/6

## Harry journal lookup repaired

The journal job passed mode=rows to a connector schema that accepts view queries. Harry recovered through the existing approved ntn CLI and saved the October 12 journal, but the original tool error remained in the job receipt.

Installed a read-only exact-title lookup helper on Harry and updated the existing job message through cron.update. Updated runtime TOOLS.md. Live lookup exited 0 and returned one existing journal. Read back the saved job; schedule, enabled state, delivery and timeoutSeconds=0 remain unchanged. No restart, new credential, duplicate journal or database write.

Backup and proof: /root/.openclaw-harry/workspace/artifacts/health-checks/harry-journal-repair-20261012/. To undo the job instruction change, apply the backed-up payload via cron.update, not direct SQLite edits; restore TOOLS-before.md and remove only the added helper after checking no newer edits. The next full scheduled run remains Victor's observation responsibility; do not describe the targeted lookup test as a full scheduled-run pass.

## Lightweight remote checks deployed

Frank, Harry and Suzy's full OpenClaw CLI checks had been skipped for insufficient memory headroom. The restricted diagnostic route could read saved results but could not refresh them. Added fixed check operations for these three named services, plus read-only job names and error receipts. Existing SSH key restrictions and pinned host keys remain; no arbitrary shell or repair operation is exposed.

The host-side Node client talks to the already-running gateway using existing authentication and operator.read. It calls health and channels.status sequentially without importing OpenClaw. The existing health-report lock is retained. A host memory admission check requires 256 MiB available; actual reader RSS was 61–62 MiB. Existing heavy CLI guards were not lowered. Network response deadlines are 15 seconds and the channel check deadline is 10 seconds; these detect failed requests, not terminate agent work.

Deployed VPS2 endpoint: /usr/local/sbin/zedbiz-fleet-diagnostics. Reader: /usr/local/lib/zedbiz-fleet/light-health.mjs. Victor client: /home/node/.openclaw/workspace/scripts/victor-fleet-inspect.py, optional --checks for frank, harry or suzy.

Verified node syntax, Python compilation, four rejected command forms and a Frank pilot. Then ran all three checks from Victor's own runtime, serially. All three returned health ok, Discord connected, live Discord check ok and configured-channel audit ok. Reader RSS: Frank 61.6 MiB, Harry 61.3 MiB, Suzy 62.0 MiB. Evidence saved on each target and in Victor's artifacts/fleet-health/investigation-20261012/<agent>-fresh-gateway-channels.json. These checks establish current service/channel operation, not a new model reply or a cure for underlying memory use.

Backups: VPS2 /root/zedbiz-fleet-diagnostics-backup-20261012/endpoint-before.py; Victor scripts/victor-fleet-inspect.before-checks-20261012.py. Rollback restores these two files with original ownership/mode and removes only the new Node reader after checking for newer edits. No service restart needed. A first attempt to write Victor's root-owned scripts as his runtime user was denied; installation used the already-approved host administrator, then tests ran as Victor.

## Still open

- Daily agent reports still use the guarded CLI runner; Victor can now recover skipped remote checks with the lightweight route. Next scheduled investigation must demonstrate follow-through.
- Significant VPS2 swap use and retained gateway/Codex memory remain an investigation, not a proven leak or fixed memory problem.
- Victor found Amanda health and Dreaming both start at 03:00 Mountain. A ten-minute health-job shift is proposed, not applied. Weekly CPU warnings show this overlap is not the only possible cause.
- Ruby was restored to xAI OAuth in Jack's separate repair task. Daily/weekly job model and provider overrides are null; today's earlier credit error remains historical. No Ruby settings changed here.
- Incident stays open. SOPs/prompts are maintained in Notion, not copied here. Source PR must be reviewed before main is treated as reflecting this deployment.
