# Inga Acknowledgement Turn Continuity Fix

Date: 2026-07-31 | Agent: Cody | Status: Pilot verification

## Change Record

- Guide or feature: Inga native channel acknowledgement and progress delivery
- Broken step: Inga sent a separate written acknowledgement through the `message` tool, then ended the turn without doing the assigned research.
- Old assumption: An LLM-written acknowledgement could safely be sent before substantive tool work while the same assignment continued.
- Tested correction: Rely on OpenClaw's platform acknowledgement reaction, begin substantive work immediately, and send written progress only after work has started. The controlled test performed a real `bash` tool call without an acknowledgement-message call and completed normally.
- Verified by: Cody
- Agent and system: Inga on VPS1, OpenClaw v2026.7.1, Discord and Telegram
- GitHub issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/104

## Live Files Changed

- `/opt/openclaw/agents/inga/workspace/AGENTS.md`
- `/opt/openclaw/agents/inga/config/openclaw.json`

The configuration retains the native acknowledgement reaction and progress delivery settings introduced by the earlier fleet rollout.

## Communication Rule

Inga now relies on the configured platform acknowledgement reaction. She must not send a separate "I'm on it" message. She begins the assignment immediately and sends written progress only after substantive work has started, continuing the same assignment afterward.

## Hindsight Prompt Delay Correction

The original configuration allowed a 60-second Hindsight automatic recall even though OpenClaw ends prompt-hook work after 15 seconds. Live Hindsight logs showed mid-budget recall reranking 300 candidates and taking approximately 43 to 47 seconds.

The Inga pilot now uses:

- Recall budget: `low`
- Maximum recalled context: 1,600 tokens
- Maximum injected memories: five
- Automatic-recall cutoff: 10 seconds

The cutoff is intentional. When automatic recall cannot finish promptly, the plugin skips injection and returns control before OpenClaw's hook ceiling. Inga may still use the provider-native recall tool during substantive work when memory is required.

## Deployment And Verification

- Backed up both live files before changing them.
- Validated `openclaw.json` successfully.
- Restarted only Inga using `/opt/openclaw/agents/inga/op-start-inga.sh restart`.
- Confirmed Inga and `inga-asana-mcp` healthy.
- Confirmed Discord and Telegram provider probes work.
- Ran a controlled fresh-session assignment requiring a `bash` tool call.
- Confirmed one `bash` call, zero `message` acknowledgement calls, no tool failures, and a normal final response.
- Confirmed a slow automatic Hindsight recall stopped at the configured 10-second cutoff without generating OpenClaw's 15-second hook-failure warning.

## Rollback

Restore these live backups and restart only Inga:

- `/home/node/.openclaw/workspace/AGENTS.md.bak-ack-turn-fix-20260731T1145MDT`
- `/home/node/.openclaw/openclaw.json.bak-ack-turn-fix-20260731T1145MDT`

## Remaining Acceptance Test

Jack should send Inga one real Discord research assignment. Acceptance requires the immediate platform reaction, substantive research tool activity, visible progress on a long run, and a completed final answer without a separate acknowledgement message ending the turn.
