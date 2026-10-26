# VPS1 monthly disk and RAM growth diagnosis

Date:2026-10-24 | Agent:Cody | Status:Diagnosis complete; no cleanup or configuration repair authorized in this pass

## Question and method

Jack supplied month-long Hostinger charts showing stepwise disk growth and a rising RAM baseline with restart dips. Read-only privileged measurements were taken at18:40UTC (12:40MDT), alongside dated GitHub maintenance records and local sysstat samples. No files deleted, service restarted, memory limit raised or configuration changed. Diagnostic receipts are owner-only under /opt/openclaw/backups/capacity-20261024.

Directory scans ran at nice19/idle IO priority. Memory capture preceded the filesystem walk, reducing scan-induced cache contamination. PSS was used for process attribution; summed process RSS would double-count shared mappings. Docker image/cache logical figures were not added to physical directory measurements.

## Disk: retained maintenance material dominates

Filesystem used373,079,207,936bytes (347.46GiB), available38.95GiB,90percent used.

Nonoverlapping measured categories:
- Main backup directory140.33GiB.
- Recovery image archives35.47GiB.
- Older home backup directory18.54GiB.
- Agent folders67.64GiB.
- Docker/containerd physical directories59.22GiB.
- OpenClaw shared services11.16GiB.
- Remaining host/shared/build/other data about15GiB.

Backup/recovery categories total194.34GiB, approximately56percent of all occupied filesystem bytes. This is occupied recovery material, not194GiB of approved disposable space.

Largest dated main backup sets: components-20261018=39.01GiB; fleet-20261018=35.95GiB; release-20261023=19.81GiB; Edith pre-9.8 October3=12.90GiB; Vivian equivalent=12.39GiB. Home September backup material totals18.54GiB. October18 recovery image archives add roughly27.6GiB under their separate dated directories.

The October3 GitHub completion record explicitly reports209GiB used after newly created recovery backups. The October17–18 release used both a core-fleet backup pass and a later component-maintenance pass; those two surviving backup sets alone total74.96GiB, in addition to recovery images, builds and rehearsals. These dated operations match the major chart steps. Exact allocation of every gigabyte in the earlier graph is not possible without historical filesystem inventories; this is not an exact additive reconstruction of the entire month.

Important multiplier: Vivian has14.80GiB under workspace/media; Edith has12.76GiB of project material under config/private/folder-cleanup. A full-agent archive includes those large trees again. Their business value/retention was not assessed, and neither area is approved for deletion.

The October23 cleanup did reclaim space: its verified manifest shows56.64GiB from compressing22 historical archives alone, with listing and decompressed hashes checked; later source reports additional rehearsal/cache cleanup. Its temporary101.07GiB free-space result was followed by new builds, restored test copies and recovery archives. The graph's drop/rebound is consistent with that sequence; do not quote the earlier free-space maximum as current.

Current Docker system df:41 image entries,44.97GB logical image size,13.97GB reported reclaimable; build-cache logical18.13GB includes17.73GB shared and only403MB private. These figures overlap image layers and do not promise corresponding physical recovery. Staged unused images are needed for unfinished rollout; broad pruning is not justified. Log storage is only0.42GiB and is not the main disk cause.

Docker uses io.containerd.snapshotter.v1. Its compressed and extracted image storage explains part of its physical overhead, but there is no verified backend-switch date attributing a specific chart jump to that feature.

## RAM: real application footprint, plus cache

At18:40UTC:
- Host anonymous application memory19.97GiB.
- Eleven agent containers:17.55GiB anonymous /20.29GiB working memory excluding inactive file cache.
- Their main OpenClaw gateway processes hold15.31GiB private resident memory within those totals.
- Other containers:2.03GiB anonymous /2.77GiB working memory. Shared Hindsight API about0.85GiB anonymous; PostgreSQL0.11GiB; eleven Asana sidecars about60MiB anonymous each.
- Host Cached8.39GiB plus reclaimable slab1.22GiB. These overlap mapped/container file memory and must not be added blindly.
- Host available9.78GiB, swap about0.5MiB, memory-pressure averages0.00 at capture.

Marsha's working footprint was2.71GiB; Terry2.39GiB. Agent main processes, their worker threads and smaller Codex/MCP helpers dominate. This is not explained solely by Mem0 or by reclaimable Linux page cache. Prior controlled Mem0 A/B reduced anonymous memory by only about169MiB on one agent; it does not account for the fleet-wide multi-gigabyte difference.

Saved sysstat daily UTC averages (anonymous application memory / file cache):
- Oct16:22.21GiB /4.49GiB.
- Oct17:17.31GiB /7.74GiB.
- Oct18:19.94GiB /6.16GiB.
- Oct19:19.85GiB /5.81GiB.
- Oct20:21.11GiB /5.27GiB.
- Oct21:20.85GiB /5.56GiB.
- Oct22:21.03GiB /5.29GiB.
- Oct23:20.48GiB /5.50GiB.
- Oct24 partial day:21.00GiB /4.62GiB.

The Oct17-to-Oct20 rise includes real application allocation while file cache fell. Therefore “just cache” is not an adequate explanation. But the series also settles around21GiB and Oct16 was already higher; it is not a continuous post-update climb.

Restart dips followed by recovery to a higher warm footprint fit runtime initialization and retained application state/connection workers. They are not sufficient proof of an unbounded memory leak. Old per-process samples are unavailable for the September24 baseline; local sysstat retained only Oct16 onward, so the exact causes of the full month's initial step cannot be apportioned between code changes, workload and retained runtime state. No heap/object retention repair is claimed.

Hostinger's current support article says its chart includes used plus buff/cache. Exact exported panel-series accounting was not accessible in this pass; live Linux/cgroup readings above are the authoritative breakdown here. Do not subtract one current cache reading from the whole historical chart or treat every displayed gigabyte as unreclaimable process RAM.

## Diagnosis and practical solution

Disk growth is largely the upgrade/recovery workflow accumulating full archives, retained old/new image versions and restored test data on the same production disk. Cody's upgrade work contributed. Large media/staged project trees multiply the size of every full backup. This is a retention/storage problem requiring a concrete keep/delete/off-host decision, not a reason to delete live business data.

RAM growth is dominated by the loaded OpenClaw framework/processes and their workers, with additional cache. Warm-up/retention explains the reset-and-rebuild pattern, but an exact whole-month causal breakdown and leak verdict remain unproven. Disk archive deletion would not reduce these running processes' anonymous memory.

Recommended next work:
- Build a path-specific retention manifest against current mounts, recovery manifests, accepted versions and pending rollouts; separate unique business assets from repeatable runtime/test copies.
- Verify current off-host recovery and the required rollback set before proposing dated archive retirement. Review old rehearsals and duplicate generations first; no broad Docker/image/volume prune or unverified claim that all194GiB is reclaimable.
- Do not launch the next full fleet backup/build wave without sufficient reserve.
- Investigate steady application retention separately using comparable quiet/task/post-idle samples and targeted worker/heap attribution. Preserve required tools, settings and budgets; no forced cache drop or memory-limit increase.

Evidence: ram.json, disk.json, du-openclaw/varlib/home/varlog.txt, memory-history.json, agent-largest-dirs.txt, edith-private-sizes.txt, backup-detail.txt. Inspection helper published under docker/capacity-20261024/inspect.py.

Sources: [October3 maintenance](../main-vps/2026-10-03-vps1-maintenance-completion.md), [October18 maintenance](../main-vps/2026-10-18-component-maintenance.md), [October24 host maintenance](2026-10-24-host-maintenance.md), [Hostinger memory accounting](https://www.hostinger.com/support/6867460-how-to-check-detailed-ram-usage-on-your-vps-at-hostinger/), [Docker image-store storage](https://docs.docker.com/engine/storage/containerd/).
