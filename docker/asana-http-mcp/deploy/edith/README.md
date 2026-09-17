# Edith project recovery deployment

Date: 2026-09-17 | Agent: Cody | Status: Deployed to Edith; first production sitting verified; folder acceptance remains open

## Scope and operating model

Jack approved Amanda as coordinator, Ruby as independent reviewer, Edith continuing unrelated approved work, and an Asana-first wake-up design. This deployment targets project 1218559074752632 and Edith only; it does not roll the connector change across the fleet or certify all 52 review requirements as passed.

- Native Asana Rule "Edith — release scheduled work by assignment email": incomplete task overdue by one minute, name contains [Edith dispatch], assignee empty, then assign Edith.
- Native Rule "Ruby — release scheduled review check by assignment email": same trigger and empty-assignee condition, name contains [Ruby review], then assign Ruby.
- Top-level sitting/check tasks live in Work Sessions and Review Checks (1218615286033089). Due timestamps on these tasks are dispatch times, separate from folder deadlines.
- The native builder exposes relative create-task dates in days/weeks/months/workdays, not a relative hour. Already-awake agents/helpers create exact future due_at timestamps. Asana performs the delayed assignment.
- Email intake runs the helper, returns promptly, and leaves production to a separate main-agent session.
- Before production starts, the helper creates the next unassigned work sitting twenty minutes ahead and a review check sixty minutes ahead if none is open. It retains a global worker lock and per-task launch receipts.
- Worker prompt reserves twelve minutes for work/checkpointing; OpenClaw limit is 900 seconds. An outer 960-second process-group deadline records timeout status. Three previous incomplete production sittings pause the automatic chain and request coordinator intervention.
- Ruby checks readiness separately from acceptance. Blocked checks defer one hour. Ten original acceptance subtasks are now pending native approvals; dependencies remain intact and they remain unassigned until ready.
- No ten-minute coordinator LLM polling, Asana AI action, or OpenClaw heartbeat was enabled.

## Files and deployment

The running connector was image zedbiz/asana-http-mcp:2.0.0-standard, while the repository source/catalog was an older variant. Therefore Dockerfile.expiry derives from the installed image and patch-expired-session.mjs requires exact matching of the three affected responses.

Installed image: zedbiz/asana-http-mcp:2.0.0-standard-edith-expiry-20260917.
Unknown supplied MCP session IDs return 404; missing IDs remain 400; invalid authentication remains 401.
Compose: /opt/openclaw/agents/edith/docker-compose.yml.
Backup: docker-compose.yml.before-edith-expiry-20260917.

Recreate only edith-asana-mcp through the existing 1Password-protected op run environment. A plain docker compose invocation initially passed literal op:// references and failed authentication; it was corrected immediately using op run. The authenticated Edith identity/workspace was then read back.

Persistent worker files:
- /home/node/.openclaw/workspace/scripts/edith-project-dispatch.py
- /home/node/.openclaw/workspace/scripts/edith-recovery-work.md
- Private receipts under /home/node/.openclaw/private/edith-dispatch/

The helper uses Edith's configured PAT MCP and verifies user 1215564984542462 and workspace 11298561585567. No Jack-authenticated connector runs Edith's work. Existing model, gateway, memory integration and email sender controls remain in place.

## Live evidence

All times below are UTC; subtract six hours for Mountain daylight time.

- Isolated connector: POST/GET/DELETE unknown session 404, missing session 400, unauthorized 401; initialize/catalog and accelerated expiry passed.
- First pilot 1218600472888762: native assignment 19:06:12, verified Asana email UID144 dispatched 19:07:04, task completed 19:08:33. Email handler later hit its 120-second limit while finishing records. This was a partial success and motivated the separate worker.
- Separate-worker pilot 1218617626739115: assignment 19:14:43, email 19:15:24, helper 19:15:49, intake returned status ok at 19:15:56, task completed 19:17:06, worker exit zero at 19:17:41. No Drive changes.
- Production restart 1218617629784120: native assignment 19:22:24; email UID146 dispatched 19:23:05; helper launched 19:23:30; intake status ok 19:23:40. It created continuation 1218604531998882 due 19:43:30 and Ruby check 1218617631258923 due 20:23:33 before doing production work.
- Production sitting completed with live task read-back, worker exit zero 19:30:15. Marketing Tool Comparisons parent 1218574348046598 is Ready for Review and incomplete. Edith reports reconciling 583 saved items without duplicate copies. Independent content acceptance remains Ruby's job.
- Shared evidence: https://drive.google.com/file/d/1H7XiYTxhbIa-OA-SacVj9sljMOP20GCz/view. Amanda's own running gog connector successfully read its metadata after upload.
- Saved next action: reconcile InCanmore and publish its handoff.
- Outer-timeout harness used a harmless sleeping process and child, verified process-group termination, worker-timeout receipt, exit 124 and incomplete-sitting notice.
- Ruby blocked-review pilot 1218615286142485 completed 19:25:53 after creating unassigned retry 1218601414531304. Native assignment occurred 19:28:53; Ruby posted email wake proof and completed retry 19:30:41 without approval, Drive changes or another retry.

## Limits that remain explicit

- The historical long Asana hang has not been reproduced and conclusively repaired. The real-idle native-runtime probe connected with 76 tools, but did not return a usable completion receipt after the idle interval; its lingering local SSH test processes were stopped. Do not describe that test as passed. Short sessions and pre-armed continuation reduce reliance on one long-lived connection.
- A memory save succeeded, but full completion-record memory read-back remains partial. Exact task comments and private checkpoints are retained, so a missing memory entry must not cause repeat copying.
- Ruby's first pilot used the existing Gmail forwarding route and arrived after several minutes. A direct cPanel forward from ruby@agents.zbiz.ca to ruby@zbiz.ca was added and read back, preserving Jack's existing Gmail copy. Direct Asana mail was accepted by Ruby's existing authenticated intake.
- Creating a separate Amanda kickoff task was rejected by automatic approval review with "blocked by policy". No such task was created and no alternative route was used. Existing coordinator task 1218562186316309 remains assigned. A new Amanda wake-up/end-to-end exception delivery was not proven by this deployment.
- Approval/correction production behavior, the second real continuation and all ten accepted folder outcomes remain live operational acceptance work. Do not close the incident or the 52-item quality register based solely on these setup tests.
- Held credential document 1d6ADvC5OVsNQ_I50K944htnQP1dj7StP and protected Branding/Whiteboard areas remain protected.

## Rollback

Pause both named Asana rules first and inspect active worker/receipt state. Do not interrupt a Drive writer without preserving its checkpoint. Cancel only future unassigned sitting/check tasks, never mark a folder accepted to stop automation. Restore the connector compose backup and recreate only its service through the protected op run route. Preserve all receipts and shared evidence. Approval backups for the ten parents/subtasks are in Amanda's private edith-recovery-20260917 directory.

## Records

- Main incident: https://github.com/ZedBiz44/z-asana-procedures-Skill/issues/2
- Ruby email/review source: https://github.com/ZedBiz44/ZedBiz-hermes-ai-agents-vps3/pull/58
- Operating plan: https://app.notion.com/p/3dea3e33d58180b89f0dfb5e0081eeb5
