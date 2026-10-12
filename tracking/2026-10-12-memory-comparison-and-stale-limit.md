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
