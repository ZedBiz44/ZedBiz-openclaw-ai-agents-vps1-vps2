# 2026-08-04 Hindsight Response-First Repair

Date: 2026-08-04 MST | Agent: Cody | Status: Implemented — 24-Hour Monitoring Open

## Why This Changed

Marsha's `Good Day` message triggered an unnecessary 25.104-second Hindsight recall on an otherwise idle server. OpenClaw stopped waiting after about 15 seconds but did not cancel the request. A second message then hit the active-run queue, and duplicate recalls used internal prompt text rather than Jack's message. Inga's three unique mental models added later background refresh load.

GitHub workstream: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/109

Notion diagnosis: https://app.notion.com/p/3b2a3e33d581813e9651e1b6fda2eefc

## Backups And Rollback

- Live backup: `/opt/openclaw/services/hindsight/backups/response-first-20260804-153434`
- Exported Inga models: `inga-mental-models-full.json` inside that protected backup
- Original stopped container: `hindsight-pre-response-first-20260804-153815`
- Intermediate stopped benchmark containers were retained temporarily for rollback comparison.
- No memory volume was deleted or replaced.

## Live Changes

### Hindsight

- Built `zedbiz/hindsight:0.8.4-flashrank-20260804` from the pinned upstream 0.8.4 digest.
- Installed the missing optional FlashRank package.
- Set provider to `flashrank`.
- Set model to `ms-marco-TinyBERT-L-2-v2`.
- Reduced rerank candidates from 300 to 50.
- Reduced total worker slots from 10 to 4.
- Reduced consolidation reservation from 3 to 1.
- Kept FP16 disabled because VPS1 is x86 Linux CPU-only.

### Inga Mental Models

- Exported `working-procedures`, `active-projects`, and `user-preferences`.
- Deleted all three from the `internet-marketing` bank.
- Verified the bank now reports zero mental models.

### Agent Memory Mode

- Marsha: `autoRecall=false`; `autoRetain=true` because her comment-only heartbeat does not run.
- Maggie, Inga, GohZed, Grogar: `autoRecall=false` and `autoRetain=false` during the response-first period.
- Explicit Hindsight recall and retain tools remain available.

### Heartbeats

- Marsha's comment-only heartbeat remains unchanged.
- Maggie, Inga, GohZed, and Grogar changed from the default 30-minute cadence to `6h`.
- Disabling automatic retention on these four prevents routine heartbeat chatter from polluting Hindsight.

### Telegram Queue

- Set Telegram queue mode to `followup` on all five Hindsight agents.
- Set Telegram debounce to 100 milliseconds, capacity to 20, and overflow policy to summarize.
- This avoids the unsupported active-run transcript steering path.

### Explicit Recall Tool Repair

- Found an SDK mapping bug where `max_results` was incorrectly sent to Hindsight as `maxTokens`.
- The default request for ten results therefore allowed only ten tokens and returned no memories.
- Patched all five agents to request a 1,024-token recall budget and then slice the returned list to the requested result count.
- Deployed the idempotent repair script at `/opt/openclaw/shared/scripts/patch-hindsight-agent-sdk-recall.mjs`.
- Backed up each agent's original SDK file before patching.

## Verification

- Hindsight health: healthy; database connected.
- All five affected OpenClaw containers: healthy after restart.
- Ten-recall TinyBERT/50 benchmark: 0.490-second minimum, 0.664-second average, 0.830-second P95, 1.190-second maximum.
- Known-fact checks returned matches for Mountain Time, Exshaw/Canmore, and GitHub/Notion source routing.
- Marsha `Good Day` pilot: normal reply, zero Hindsight calls.
- Marsha explicit recall after the SDK repair: exactly one recall returned 20 facts and completed in 0.514 seconds.
- Marsha two-message Telegram queue pilot: `FIRST_DONE`, then `SECOND_DONE`, with zero `transcript_commit_wait_unsupported` errors.
- Hindsight logs after deletion/restart: zero `refresh_mental_model` jobs observed.

## Remaining Monitoring

- Keep Issue #109 open for a 24-hour check confirming no mental-model refresh jobs return.
- Observe real Telegram response time. The no-memory Marsha pilot still took 11.33 seconds end to end because the model call itself took time; Hindsight was not involved.
- Automatic recall stays off until an upstream-safe raw-user-only, once-per-turn gate exists and passes a controlled pilot.

## Rollback Note

If relevance or stability falls, restore the protected `.env`, stop the exact new container, rename the original stopped container back to `hindsight`, and start it. Restore agent JSON from the protected backup if the response-first settings must be reverted. Recreate Inga's models only from the exported JSON and only after a new approval.
