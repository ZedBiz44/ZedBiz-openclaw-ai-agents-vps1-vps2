# Four-agent memory comparison and stale-limit correction

Cody, October 12, 2026, Mountain Time. Continues fleet incident https://github.com/ZedBiz44/z-agent-health-report-Skill/issues/6.

## Confirmed differences

Same-method private proportional process memory samples: Gohzed gateway 1.22 GiB, Maggie 1.11 GiB, Marsha 2.01 GiB, Amanda 2.76 GiB. Gohzed and Maggie also have about 0.50 GiB each in swapped process memory; RAM alone understates their footprint. These were active-work snapshots, not controlled idle benchmarks. Amanda's additional Codex/tool processes are a small fraction of her total, so removing them cannot explain or recover the entire gap. Marsha has additional active Codex/tool processes, about several hundred MiB. Never kill them merely because they exist.

Gohzed, Maggie and Amanda use the same Docker image. Marsha's image differs, but all report OpenClaw 2026.9.8 and the sampled state-reader/reclamation worker source hashes match. Gohzed, Maggie and Marsha select Hindsight memory; Amanda selects LanceDB. This is a difference, not proof LanceDB causes the excess.

For the same log window starting 07:00 Mountain, Gohzed, Maggie and Marsha had no slow reclamation-worker messages; Amanda had 17 and 23 critical memory samples by about 08:50. Amanda's main JavaScript heap plus sampled worker heaps explain less than total resident memory; native allocation, unsampled memory and retention remain to be attributed. No proven leak.

## Reproduced code defect

The running diagnostic module captures process.constrainedMemory() once at import. Amanda started before her limit was increased from 3 GiB to 5 GiB. Her diagnostics continue reporting a 2.25 GiB critical RSS threshold (75% of the old 3 GiB allowance). The diagnostic code publishes openclaw.memory.critical on each critical sample. Worker pools subscribe and retire idle workers; later operations recreate them. Code and logs establish the trigger and worker churn, not that churn accounts for every excess byte.

Correction: obtain process.constrainedMemory() on each diagnostic memory sample. Keep explicit test overrides, growth detection, RSS/heap thresholds, warning logging and critical protection unchanged. Remove the unused startup snapshot constant.

## Tests

Disposable no-network container with no agent data: process starts at 256 MiB, Docker limit changes to 384 MiB. The same running Node process retains 256 MiB in a captured variable but process.constrainedMemory() returns 384 MiB afterward.

Six focused assertions execute the extracted installed diagnostic-memory region with controlled memory samples. Old code still emits critical and retires workers at 2.6 GiB after a 3-to-5-GiB increase; corrected code emits warning and does not invoke emergency retirement. Initial critical behavior and genuinely high 3.2 GiB behavior remain. A decrease to 2 GiB also updates protection correctly, whereas the old code misses the new critical threshold.

## Deployment status and proposed pilot

Source correction and tests prepared only. Amanda production module is unchanged. Jack was asked for one controlled Amanda restart after verifying no active work, to load the correction. Back up and hash-check the module first; validate syntax; preserve 5 GiB limit; check service and Discord afterward; compare memory and worker churn against this baseline. Restore the original module and restart once only if verification fails, with care for any new active work. Do not infer fleet rollout approval. A post-restart memory drop alone is not proof of a cure. Source is a version-specific patch; future image builds must incorporate or retire it through review rather than blindly apply it to different code.

## Setup refusal clarified

Victor recorded: delegated OpenClaw approval requires an active run authority. The rejected operation concerned original remote daily-runner integration and Rocky diagnostic-principal metadata. It was not missing Jack approval and not a demonstrated SSH credential failure. Supplemental remote recovery is already installed in Victor's daily summary, so that portion no longer waits on the original-runner deployment. Precise underlying authority lifecycle failure still needs its request trace; do not claim it is repaired or grant broad permissions as a guess.

## Approved deployment — October 12 evening Mountain

Jack approved: "sure get amanda done" and directed completing all four agents. Amanda's scheduled-job state showed no running jobs and Discord reported no active run immediately before the change. Backed up the original module, hash-checked it, applied the tested change, validated Node syntax and performed one graceful Docker restart with --timeout -1 (no forced kill deadline). Started at 17:37:22 Mountain. The initial health read hit normal startup before the listener was ready; later service health, Discord live/required-channel checks and Telegram checks all passed. CPU degradation cleared in the follow-up sample. The first syntax check used a temporary filename with an unrecognized extension and made no live change; changing the temporary suffix to .mjs resolved that validation error.

Private backup: /home/node/.openclaw/workspace/artifacts/health-checks/amanda-memory-pilot-20261012/diagnostic-before.mjs. Old SHA256 c305ab8b9e91a6c4ae4d2272ceb5ec14c05c98a5a04f5ba9e4a48b58b89ad06f; patched SHA256 8470e0b89e9188b565a2ca708974959b1002b050651ef5d9a3cc06e119fbdd49.

Persistence: built zedbiz-openclaw:amanda-memory-limit-20261012 from the exact existing base image, adding only the patched diagnostic module. No credentials or agent data copied into the build. Current running module and image module hashes match. Amanda Compose now references that image; semantic comparison confirmed only services.amanda.image changed and compose config --quiet passed. Backup: /opt/openclaw/agents/amanda/docker-compose.yml.before-memory-patch-20261012. No additional restart/recreate occurred. A first build using a bare sha256 FROM was interpreted as a registry name and failed; the verified existing local base tag built successfully. Build context retained at /home/jackadmin/amanda-memory-image-20261012. The running container's image metadata still identifies its original image; its patched file matches the replacement selected for future recreation.

Rollback: restore the exact backed-up module and prior Compose image field, preserving any newer unrelated edits; an approved graceful restart is needed to load restored code. Do not blindly restore entire configurations after concurrent changes. Future image upgrades must incorporate or retire this version-specific patch through review.

## Idle tool retention corrected on all four

Marsha's extra video-tool process groups were session-owned MCP connections, not proof of rogue processes. The installed default retains them indefinitely (mcp.sessionIdleTtlMs omitted/zero). Enabled the supported 600000-ms idle retention setting on Marsha first, then Amanda, Gohzed and Maggie after the pilot config reload and video-tool reconnect tests. Configuration hot reload applied without further restarts. No tool removed, model changed, active-work timeout added, or arbitrary process killed.

Safety test executes the installed idle-sweep function with expired, active, queued, recent and disabled-cleanup cases: six assertions pass; only the expired idle runtime is disposed. Active leases and pending work chains are explicitly protected. Direct read-only video-server connection/list-tools/close/reconnection passed twice, returning both expected tool names without running video analysis. Old Gohzed and Maggie video-server processes disappeared after cleanup; Marsha's oldest group also disappeared while new groups appeared during current work. Thus retention cleanup is functioning; do not claim every currently running tool is unnecessary or that Marsha's active-work RAM is an idle leak.

Each agent backup: workspace/artifacts/health-checks/idle-tool-retention-20261012/openclaw-before.json (0600), plus change.json. Roll back only mcp.sessionIdleTtlMs to its prior value/absence and verify hot reload. The ten-minute value controls UNUSED CONNECTION RETENTION, not agent work duration. This is not a recurring restart or a deadline on tool calls.

Memory snapshots excluding reclaimable inactive file cache: Amanda 1.04 GiB just after restart, 1.96 GiB after services warmed; do not credit the entire initial drop to the code change. At 17:48 Mountain, Marsha 2.85 GiB RAM plus 0.065 GiB swap during ongoing work; Gohzed 1.32 + 0.44; Maggie 1.44 + 0.45. These are observations, not certification of the under-2-GB simple-use target. Sustained post-work behavior remains Victor's normal follow-through.

## Normal-model and channel verification

Serial reply tests through the existing gateway RPC (no heavyweight OpenClaw CLI) completed successfully for Amanda, Marsha, Gohzed and Maggie. Each returned Memory check OK, with no tool calls and no Discord/external delivery. All runs used timeout=0; repeated bounded agent.wait requests only observed completion. No model/provider was changed. At17:52 Mountain all four reported health true and no event-loop degradation; Discord live probes and configured-channel audits passed for all four, plus Telegram probes for Amanda/Marsha. Marsha's unconfigured Slack remains optional, not a failed required channel. Working RAM/swap GiB after those replies: Amanda2.172/0, Marsha2.586/.065, Gohzed1.620/.439, Maggie1.692/.450. New reply sessions temporarily reopen tool connections, so these are not post-expiry idle values.

Victor received the exact deployment/rollback handoff in repair-20261012/cody-four-agent-memory-completed.md and an authorized gateway coordination turn. He retains next scheduled-cycle and idle-retention follow-through. Do not duplicate the changes, infer rollout of the diagnostic patch to other agents, erase historical warnings, or declare the overall memory target achieved from these samples.


## Post-expiry verification and concurrent Marsha maintenance

At 18:02 Mountain, Amanda working RAM was 2.106 GiB with no swap and no video-server processes; Gohzed 1.549 GiB plus 0.439 GiB swap, Maggie 1.582 GiB plus 0.450 GiB swap. These remain workload observations, not proof of an under-2-GB steady-state target. Gohzed/Maggie each still had a newer video-server process; active/recent sessions can legitimately retain connections.

The final measurement caught Marsha stopped at 17:58:09 (exit143; Docker OOMKilled=false). A separate marsha-monitor-maintenance container was running update repair --no-restart --yes --json against her data. Cody did not launch or interrupt it. Victor's coordination turn could not identify its owner. It completed exit0 and was removed at18:03:41; Marsha restarted at18:03:41.481. At18:06 fresh gateway health, Discord connection/probe/required-channel audit and Telegram connection/probe all passed. Her post-restart reading is not comparable to the other three idle samples. Record the separate repair owner/purpose as unverified; do not attribute this stop or recovery to the idle-retention change.

Cody independently verified replacement-image and current module hashes match and the Compose image selection is correct. Proof saved in Victor's repair-20261012/cody-amanda-image-provenance.json. Victor's restricted image-inspection route cannot independently inspect that image; this does not mean the image or persistence work is missing.
