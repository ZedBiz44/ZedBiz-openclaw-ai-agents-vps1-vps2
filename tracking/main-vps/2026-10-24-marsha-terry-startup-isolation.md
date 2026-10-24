# Marsha and Terry startup isolation — 2026-10-24

Jack requested diagnosis of their long startups after VPS1 host maintenance. Four bounded serial copied-state starts reproduced the delay and separated the common plugin loader cost from Terry's additional Mem0 package cost. Production was not restarted or reconfigured. No safe production performance repair is claimed.

## Main diagnosis

Both agents spend substantial time in OpenClaw's local plugin-generation artifact capture: inspecting paths, opening/reading files and materializing/checking plugin dependencies. This is a specific code path, not simply a slow model or generic server-health warning. Marsha's Discord and Slack full-load spans take17.91/16.19seconds; with Hindsight disabled they still take18.56/17.11seconds. Terry's Mem0 full-load span takes123.79seconds, plus Discord20.41 and Slack16.39seconds. The SDK installation/package size amplifies repeated guarded filesystem operations.

Terry's active installed Mem0 project contains37,817 regular files and318,865,533 logical bytes. Marsha's active Hindsight project contains98 regular files and2,578,712 logical bytes. These are active project-tree inventories, not counts of every dependency used anywhere in the runtime or proof that arbitrary files are removable. Terry's tree includes Cloudflare8964files, Mistral3260, natural2666, LangChain core2046, Anthropic1753 and Azure SDK trees. @mem0/openclaw-mem0 is1.2.1 and its selected mem0ai dependency is3.0.7. A slim/bundled package for the actual configured integrations is a concrete test candidate, not a validated repair; do not manually delete dependencies from production.

## Controlled results

| Agent / copied-state condition | Startup recovery-ready marker | Main plugin phase | Main-session recovery phase |
|---|---:|---:|---:|
| Marsha / Hindsight enabled |141.95s|44.68s|45.28s|
| Marsha / Hindsight disabled only in clone |116.63s|44.75s|45.14s|
| Terry / Mem0 enabled |271.03s|169.80s|173.10s|
| Terry / Mem0 disabled only in clone |114.26s|44.11s|44.63s|

The plugin and main-session phases overlap and must not be added. Marsha's unchanged plugin span does not support Hindsight as her main startup bottleneck. Her25.3-second overall difference includes other phase variation, including bootstrap/config preparation and cache/order effects; do not attribute all of it to Hindsight. Terry's157-second overall difference and125.7-second plugin-span reduction strongly implicate Mem0 admission/dependency loading. The unchanged copied sessions and disappearance of the worker timeout in the Mem0-disabled run argue against treating the timeout as independent proof of a corrupted session database.

## Sampled call-stack evidence

| Run | Recorded profile duration | Inclusive plugin artifact creation | Nested dependency package copy |
|---|---:|---:|---:|
| Marsha enabled |153.18s|88.23s|68.39s|
| Marsha disabled |127.47s|79.35s|58.75s|
| Terry enabled |291.97s|218.82s|172.08s|
| Terry disabled |133.47s|77.87s|57.54s|

These inclusive costs overlap and are sampled time attributed to stacks, not additive CPU seconds. Profiles include settling and graceful shutdown, so their duration is not the startup-ready marker. Terry-enabled self samples include lstat67.42s, read37.21s and realpath36.73s. The common remaining filesystem cost is still substantial without either memory connector. Most of this measured bottleneck precedes normal model inference.

Terry-enabled logs show a173.25-second delayed liveness interval and a startup orphan-marking WorkerTaskError timeout. Both disappear in his disabled control. Marsha has neither marker in either run. This supports blocked event-loop/worker responsiveness as a secondary effect of synchronous loading; it does not prove every historical worker timeout has this cause.

## Live reboot evidence and host context

The earlier current production startup logs show Marsha93.94seconds plugins.runtime-post-bind and Terry249.28seconds; main-session recovery94.23/249.36seconds overlaps those spans. Earlier recorded full cold-fleet wall-to-ready was224.2/347.5seconds. These are different starts under simultaneous fleet/cold-cache load, not directly comparable speed benchmarks against the serial tests. Current sampled host available memory10.9GiB, swap233MiB with no sample swap-in/out, idle87–89percent and CPU steal5–6percent. Host contention remains a contributor, but the fresh local stack attribution and serial reproduction show it is not an adequate sole explanation. Neither capacity cleanup nor host patching removed this code path.

## Method, controls and limits

Used the existing protected Marsha and Terry rehearsal directories and their real currently selected production image IDs. Four starts ran serially, each with2CPUs,4GiB RAM/no extra swap, no network, no Docker socket, skipped inbound channels/cron/Gmail/heartbeat and automatic memory reads/writes disabled. The memory plugin remained enabled for the baseline and was disabled only in its control. Production agent mounts were replaced by copied-state mounts; remaining shared mounts read-only. No model/tool turns were submitted. Native Node CPU sampling and OpenClaw plugin.load-profile were enabled in all four runs.

This is one profiled serial pair per agent, in enabled-then-disabled order. Filesystem warmth, profiling overhead,2CPU safety quota, differing clone histories and normal host variation limit exact wall-time promises. The serial controls establish component attribution, not full functional acceptance or a cold-start SLA. Readiness is the startup sidecars.subagent-recovery log marker, not30seconds of continuous responsiveness or first conversational-answer latency. One Marsha localhost readyz probe returned200 during the run; it is not a sustained-availability benchmark.

All four reached the selected marker without OOM. Both production container IDs/PIDs/images/restart counts remained unchanged. Both clone configs restored byte-for-byte; all four test containers stopped and removed. Final Marsha/Terry production healthy, zero current restart counts and no OOM. Original logs, profiles, baseline and receipts remain private under /opt/openclaw/backups/startup-isolation-20261024. Published executor/results/profile summaries under docker/startup-isolation-20261024.

## Repair proposal and upstream check

Prioritize the shared OpenClaw loader's repeated safe path/file preparation; retain provenance/source-integrity guarantees. Separately test a smaller bundled Mem0 dependency package on a clone, preserving Terry's configured model/provider, Qdrant collections, memory scopes and automatic/manual memory behavior. Neither removing memory nor switching its extraction LLM is a demonstrated production performance repair. Any candidate must pass repeated starts plus real save/recall/fresh-session and channel/tool checks before a one-agent deployment decision.

[OpenClaw166020](https://github.com/openclaw/openclaw/issues/166020) remains open and describes the same repeated guarded source-tree validation/capture family. This is corroborating upstream evidence; our local profiles establish applicability. [PR168391](https://github.com/openclaw/openclaw/pull/168391) concerns external TypeScript resolution; its published synthetic improvement is not evidence that it fixes these compiled JavaScript package trees. No unreviewed patch, trust-check bypass, version change, package deletion or live restart was applied. A ready-to-deploy repair remains unproven.
