# 2026-07-08 - Edith Discord Immediate Acknowledgement Repair

Date | Author | Status: 2026-07-08 | Cody | Live patch applied

## Summary

- Repaired Edith's Discord "silent work" behavior after Jack reported that Edith did not appear to respond to a plain message in `#edith`.
- Confirmed Edith did receive and complete the original request; the failure was missing immediate acknowledgement, not a sleeping bot, missing mention rule, or failed task execution.
- Reapplied the immediate acknowledgement hook to Edith's live Discord inbound handler.

## User-Facing Symptom

- Jack sent a plain Discord message in `#edith` at `2026-07-08T10:08:42 MDT`.
- Edith did not immediately confirm receipt.
- Jack later mentioned Edith at `2026-07-08T10:14:26 MDT`.
- Edith posted the completed task result at `2026-07-08T10:17:20 MDT`, then answered the later mention at `2026-07-08T10:17:30 MDT`.

## Root Cause

- Edith was not asleep and did not miss the original message.
- Discord API history for `#edith` showed the original message was from Jack, not a bot, and had no mention.
- Edith completed the requested Notion update, but the live Discord handler did not contain the immediate receipt helper recorded in the earlier `2026-06-28` acknowledgement rollout.
- The prior acknowledgement patch was documented against `/app/dist/message-handler-BpHrxp7V.js`, but Edith's current live file had no `sendImmediateAssignmentAck` helper or receipt text.

## Live Evidence

- VPS1 host: `srv1404026`
- Edith container: `edith`, healthy
- Edith public health: `{"ok":true,"status":"live"}`
- Edith bot identity: `edith-openclaw`, Discord user ID `1514850619494498334`
- Actual `#edith` channel ID: `1514852711885967464`
- Original user message ID: `1524447144113868830`
- Mention message ID: `1524448590855012382`
- Completion message ID: `1524449318634000506`

## Change Applied

- Patched live file inside Edith container:
  - `/app/dist/message-handler-BpHrxp7V.js`
- Added `sendImmediateAssignmentAck(ctx)` before both accepted `messageRunQueue.enqueue(...)` paths.
- Receipt text:
  - `Received, Jack. I'm starting now and will update you shortly.`
- Receipt behavior:
  - Replies to the triggering Discord message.
  - Uses `allowed_mentions: { parse: [] }` to avoid accidental pings.
  - Deduplicates message IDs in memory to avoid repeat receipts.

## Backup

- Backup created inside Edith container:
  - `/app/dist/message-handler-BpHrxp7V.js.bak-immediate-ack-20260708-2026-07-08-164514686Z`

## Verification

- `node --check /app/dist/message-handler-BpHrxp7V.js` passed.
- Restarted only Edith with `docker restart edith`.
- Edith returned healthy after restart.
- Discord startup logs confirmed:
  - channels resolved for `ZedBiz Agents`
  - client initialized as `1514850619494498334`
  - bot probe resolved `@edith-openclaw`
  - Message Content Intent reported as `limited`, which is expected for small bots.

## Remaining Verification

- A true end-to-end acknowledgement test requires a human-authored Discord message in `#edith`, because a bot-authored test message from Edith's own token would be ignored or would not represent Jack's user path.
- Test message to send:
  - `Edith receipt test - please confirm you received this and wait for my next instruction.`
- Expected result:
  - Edith should immediately reply with the receipt text before doing any deeper work.

## Rollback

- Restore the backup file inside the Edith container:
  - `/app/dist/message-handler-BpHrxp7V.js.bak-immediate-ack-20260708-2026-07-08-164514686Z`
- Restart only Edith after rollback.

## Durability Note

- This is a live container patch. If Edith is rebuilt or the OpenClaw bundle is upgraded, re-check whether the acknowledgement helper still exists in the active Discord handler and reapply or upstream the patch if needed.
