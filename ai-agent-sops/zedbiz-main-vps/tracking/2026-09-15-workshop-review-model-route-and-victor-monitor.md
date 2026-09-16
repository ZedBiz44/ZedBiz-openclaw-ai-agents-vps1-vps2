# Workshop Review Model Route And Victor Monitor

> 2026-09-15 | Cody | Status: Implemented with one separate Maggie empty-folder behavior awaiting decision

## Outcome

- Kept OpenClaw Skill Workshop in `auto` mode for all 15 OpenClaw agents.
- Corrected the scheduled Workshop model fallbacks on VPS1, VPS2, and Rocky on VPS4.
- Changed the host model-alert monitor to send as Victor and label alerts `ZedBiz Model Monitor — Automatic Fleet Notice`.
- Added 15 Victor-owned read-only follow-up jobs. Each runs 30 minutes after one agent's main weekly Workshop review.
- Victor posts to `#agent-health-report` only when a Workshop file changed. He compares that file with the agent's `workspace/skills` collection and never edits either collection.

## Authoritative folders

- VPS1 Workshop: `/opt/openclaw/agents/<agent>/agents/main/agent/workshop-skills`
- VPS1 workspace skills: `/opt/openclaw/agents/<agent>/workspace/skills`
- VPS2 Workshop: `/root/.openclaw-<agent>/agents/main/agent/workshop-skills`
- VPS2 workspace skills: `/root/.openclaw-<agent>/workspace/skills`
- Rocky Workshop: `/home/openclaw/.openclaw/agents/main/agent/workshop-skills`
- Rocky workspace skills: `/home/openclaw/.openclaw/workspace/skills`

## Exact model diagnosis

The saved runtime receipts showed three distinct outcomes:

- OpenAI Codex candidates were rejected only for scheduled Workshop collection reviews because those runtimes did not enforce the private Workshop root through OpenClaw's file tools. This was a Workshop safety rejection, not an OpenAI account outage.
- OpenRouter Gemini 3.1 Flash Lite succeeded on multiple earlier reviews, but some reviews failed with HTTP 402 because they requested up to 65,536 output tokens while the current balance allowed 26,633.
- The old free DeepSeek V4 Flash slug failed with HTTP 404 because OpenRouter retired the free route and directed callers to the paid slug.

The repair preserves every agent's primary model, caps Gemini 3.1 Flash Lite and paid DeepSeek V4 Flash at 8,192 output tokens, removes the obsolete free DeepSeek fallback, and adds the paid low-cost DeepSeek route. Rocky keeps DeepSeek first in his fallback order.

## Live verification

- All 15 configs passed the secret-free verifier: original primary retained, obsolete free DeepSeek absent, paid DeepSeek present, and both fallback caps set to 8,192.
- Paid `openrouter/deepseek/deepseek-v4-flash` returned `DEEPSEEK_ROUTE_OK` through Amanda, Harry, and Rocky's real running OpenClaw environments.
- Amanda's formerly failing mail-reader review completed successfully through Gemini after the repair.
- The formerly failing reviews for GoZed mail reader, Inga mail reader, Wilma mail reader, and Suzy main all completed successfully through Gemini after the repair.
- Rocky's formerly failing mail-reader review completed successfully through his primary Grok route after the config repair.
- Maggie's model route also succeeded through Gemini. Her run was then marked failed because the Workshop folder was empty and the model attempted to list its parent folder. OpenClaw correctly blocked that parent-folder request. This is separate from the model-route repair.

## Victor change monitor

- Victor stores a hash baseline for all 15 Workshop folders.
- VPS2 and VPS4 reads use a dedicated SSH key restricted to one forced read-only command, with no shell or port forwarding.
- All 15 jobs are enabled, use Victor's `main` identity, use the exact Mountain Time schedule, allow only the execution tool, announce only to Discord channel `1546640814573101128`, and use paid DeepSeek as the explicit fallback.
- Amanda's job was run manually after baselining. It returned `NO_REPLY` and Discord delivery was suppressed, proving that unchanged folders remain quiet.

## Schedule

| Agent | OpenClaw main review | Victor follow-up |
|---|---:|---:|
| Amanda | Sunday 23:15 | Sunday 23:45 |
| Edith | Friday 15:47 | Friday 16:17 |
| GoZed | Tuesday 17:38 | Tuesday 18:08 |
| Grogar | Thursday 18:35 | Thursday 19:05 |
| Inga | Wednesday 07:53 | Wednesday 08:23 |
| Maggie | Tuesday 00:29 | Tuesday 00:59 |
| Marsha | Sunday 19:08 | Sunday 19:38 |
| Terry | Saturday 16:21 | Saturday 16:51 |
| Victor | Wednesday 18:12 | Wednesday 18:42 |
| Vivian | Friday 09:42 | Friday 10:12 |
| Wilma | Saturday 04:45 | Saturday 05:15 |
| Harry | Wednesday 09:58 | Wednesday 10:28 |
| Suzy | Monday 10:29 | Monday 10:59 |
| Frank | Wednesday 18:36 | Wednesday 19:06 |
| Rocky | Monday 18:39 | Monday 19:09 |

## Email helper decision

The stock OpenClaw `auto` mode creates weekly collection reviews for each configured identity. It does not provide a supported per-identity setting that leaves `main` automatic while turning only `mail_reader` off. The chosen operating decision is to keep both enabled now that the model fallback errors are repaired.

## Rollback

- Each live config has a timestamped `.bak-workshop-route-*` backup.
- Victor jobs can be identified by declaration keys beginning `zedbiz:workshop-change-review:`.
- The model monitor source and tests live under `services/model-alerts`.
- The Workshop scanner, restricted reader, rollout helpers, verifiers, and schedule source live under `services/workshop-review-monitor`.
