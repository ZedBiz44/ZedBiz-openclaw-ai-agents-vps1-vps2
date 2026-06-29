# 2026-06-28 - VPS1 and VPS2 Immediate Discord Acknowledgement Fix

Date | Author | Status: 2026-06-28 | Cody | Completed

## Summary

- Added an immediate Discord text acknowledgement hook before OpenClaw queues long-running agent work.
- Updated live `AGENTS.md` communication rules so assignments and questions from Jack require a short text receipt first.
- Kept emoji reactions available only for lightweight acknowledgement, appreciation, or approval after the text receipt rule.

## Reason

Jack reported that agents often received research assignments and then went silent for several minutes while work was underway. Live logs showed agents were healthy but frequently queued behind active model/tool work, creating uncertainty about whether the assignment was received.

## Root Cause

- The Discord message handler accepted messages and then queued agent work without sending a guaranteed human-visible receipt first.
- Several agents were missing the explicit acknowledgement rule in `AGENTS.md`.
- The previous emoji acknowledgement rule allowed emoji-only acknowledgement, which was too easy to miss for assignments.

## Systems Updated

- VPS1 Docker agents:
  - Amanda
  - Edith
  - Gohzed
  - Grogar
  - Inga
  - Maggie
  - Marsha
  - Terry
  - Victor
  - Vivian
  - Wilma
- VPS2 native/systemd agents:
  - Frank
  - Harry
  - Suzy

## Runtime Change

- Patched OpenClaw Discord handler:
  - VPS1 container path: `/app/dist/message-handler-BpHrxp7V.js`
  - VPS2 path: `/opt/openclaw-{agent}/node_modules/openclaw/dist/message-handler-BpHrxp7V.js`
- Added `sendImmediateAssignmentAck(ctx)` before `messageRunQueue.enqueue(...)`.
- Receipt text:
  - `Received, Jack. I'm starting now and will update you shortly.`
- The receipt is sent to the same Discord channel with:
  - reply reference to the triggering message
  - `allowed_mentions: { parse: [] }`

## Backups

- VPS1 backup inside each patched container:
  - `/app/dist/message-handler-BpHrxp7V.js.bak-immediate-ack-20260628`
- VPS2 backup beside each patched handler:
  - `/opt/openclaw-{agent}/node_modules/openclaw/dist/message-handler-BpHrxp7V.js.bak-immediate-ack-20260628`
- Live `AGENTS.md` backup beside each patched workspace file:
  - `AGENTS.md.bak-immediate-ack-20260628`

## Verification

- Terry test lane patched first.
- `node --check` passed on all patched handlers.
- Terry no-network handler harness confirmed the handler sends the acknowledgement before queued work.
- Suzy no-network handler harness confirmed the same behavior on VPS2 native install.
- Restarted all patched agents.
- VPS1 Docker health after restart:
  - all 11 active agent containers healthy
- VPS2 health after restart:
  - `openclaw-harry.service`: active
  - `openclaw-suzy.service`: active
  - `openclaw-frank.service`: active
  - `/healthz` returned live on ports `4100`, `4200`, and `4300`

## Rollback

- Restore the matching `.bak-immediate-ack-20260628` handler backup.
- Restore `AGENTS.md.bak-immediate-ack-20260628` if the communication wording must be rolled back.
- Restart only the affected agent after rollback.

## Follow-Up

- If agents are rebuilt or OpenClaw is upgraded, re-apply or upstream this acknowledgement hook because the runtime patch lives inside the installed OpenClaw bundle.
