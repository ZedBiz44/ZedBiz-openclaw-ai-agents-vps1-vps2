# Startup root cause and repair experiments — 2026-10-24

Jack rejected the earlier component-only diagnosis. This follow-up traces the installed code and tests specific corrections. It identifies an old eagerly imported Mem0 SDK, unnecessary enabled channel code on Marsha, and expensive synchronous per-file custody checks as the mechanisms. Five further copied-state Gateway starts, four valid small-file comparisons and a real isolated memory save/recall test completed. Production is unchanged. The work produces tested repair candidates, not a claim that startup is fully fixed or that a durable production release is already packaged.

## Terry: actual defect and why the latest plugin did not fix it

The current official @mem0/openclaw-mem01.2.1 package explicitly pins mem0ai3.0.7. Fresh npm metadata confirms1.2.1 remains the latest plugin. That SDK's dist/oss/index.mjs statically imports adapters including Cloudflare, Anthropic, Mistral, Azure, Supabase, Redis and Ollama before Terry selects a backend. Its peer adapters are not marked optional. Terry actually configures OpenAI-compatible inference/embedding and Qdrant, with history disabled.

This old packaging causes unrelated provider implementations to be installed and loaded. The active Mem0 project has37,817 regular files/~304MiB. OpenClaw capturePluginDependencies in plugin-generation-source-lookup-CDeIIp1I.mjs enumerates dependency, optional-dependency and peer names and captures resolved installed packages; missing optional/peer packages are allowed. Therefore merely substituting a newer SDK inside the old complete node_modules is not enough to eliminate the installed-peer capture cost.

mem0ai3.3.1 has optional peer metadata and loadPeer-based on-demand adapters. Built a clean93-package candidate with direct pins mem0ai3.3.1, typebox0.34.47, Qdrant client1.18.0 and better-sqlite3 12.11.1. Preserved the actual customized plugin package bytes and copied its existing SQLite package; the existing disableHistory=true policy remains. Candidate has5,447 files/~50.5MiB; Cloudflare, Azure and Mistral packages absent. Candidate lock SHA256:79adcbe80e7827d4d271fdc056d7c252fa2257635ae1f56fbfc330fdcbdf29a1.

A reverse-order fresh comparison ran candidate first and stock second, using the same current Terry image, copied state, CPU profiling,2CPU/4GiB safety boundary and no network. Both kept Mem0 enabled and automatically recalled/captured nothing during startup. Candidate registered Mem0 without module-load failures.

| Terry | Stock SDK/install | Clean SDK3.3.1 candidate |
|---|---:|---:|
| Mem0 full-load span |160.756s|13.974s|
| Main plugin span |205.090s|57.957s|
| Startup recovery-ready marker |280.887s|133.223s|
| Main-session worker timeout |Present|Absent|

Candidate still logs a delayed heartbeat; it does not eliminate all blocking. The earlier stock run's Mem0 span123.79s and startup271.03s provide another slow stock observation, not an identical replication. Timing variance is real; the fresh comparison's order does not favor the candidate with a prior stock warm-up.

## Real memory functionality proof

Used SDK3.3.1 against a new temporary Qdrant container/database, without mounting production Qdrant data or publishing ports. Preserved the existing LLM and embedding settings and disableHistory policy; only the vector destination/collection changed for the fixture. Actual inferred save created one fictional memory. Search found it; a fresh Memory instance found it again; the exact fixture memory was deleted and the isolated database/container/network removed. Requested and effective extraction model both gpt-5.6-luna. No model substitution or production memory deletion.

This proves configured SDK inference, save, embedding/vector transport and fresh-instance persistence for this fixture. It is not a full live-plugin automatic capture/recall, channels, tools or production restore acceptance. The Gateway candidate test independently proves the retained customized plugin loads and registers with the candidate dependency tree.

## Marsha: unnecessary Slack is a real configuration fault

Fresh config read shows Marsha channels.discord.enabled=true and channels.telegram.enabled=true, with no Slack channel, while plugins.entries.slack.enabled=true. She therefore loads Slack implementation/dependencies despite having no configured Slack account/channel. Her configured Hindsight plugin is not the main cause; the prior on/off comparison left the main plugin span unchanged.

With stock fs-safe0.25.0 and Hindsight still enabled, changed only plugins.entries.slack.enabled=false in the copy. Slack's full-load span disappears; Discord, Telegram and Hindsight still load. The main plugin phase falls47.987->26.058seconds. Overall recovery-ready marker160.205->102.002seconds; do not attribute the entire58.2-second reduction to Slack because bootstrap/config phases and filesystem warmth differ. Earlier stock Marsha observations were141.95seconds with44.68seconds in the plugin span. Direct unnecessary Slack load is consistently16–17seconds; main-plugin reduction is the stronger component measure.

This is a specific reversible configuration repair candidate. Live Marsha's setting has not changed. No actual channel connection test is claimed from network-isolated starts.

## Shared mechanism: repeated synchronous guarded filesystem work

Installed source is concrete:

- plugin-generation-artifact-DaZTOl4k.mjs:createPluginGenerationFileCapture recursively captures dependency files and records source identities/content receipts.
- plugin-generation-source-lookup-CDeIIp1I.mjs:copyPluginSourceFile pins a source descriptor. Its small-file path calls copySmallPluginSourceFile.
- copySmallPluginSourceFile sets assertAdmission to check the destination parent and reopen/validate the named source. It invokes that guard around create/copy mutations and again at completion. Each call redoes path/inode/size validation rather than retaining only the initial descriptor identity. Those protections detect substitutions; they are not simply removable duplicate lines.
- This work runs synchronously on the main JavaScript thread. Worker completion messages and liveness callbacks wait behind it. Thus the overlapping main-session recovery duration is not an independent database scan time to add to plugin loading. Terry's worker timeout disappears with the lean SDK, while his unchanged copied session data remain.

A real installed-function harness copying160 ordinary3,800-byte files counted6,240lstat calls (39/file),800opens (5/file),640realpath calls and3,040fstats. The same source folder was lstatted1,920times and destination folder1,280times. Captured bytes matched. This is a representative micro measurement, not a full-Gateway syscall count. With tens of thousands of SDK files, this per-operation overhead amplifies poor dependency packaging. Existing profiles independently attribute most startup work to file capture/copy/validation.

Both agents successfully load fs-safe's existing Linux native addon in auto mode. A missing native helper is ruled out; forcing native policy is not the proposed fix.

## Rejected correction and filesystem-library candidate

The installed code already contains upstream batching from PR167516 and the small-file copy path. Hypothesis: route small files through the supplied guarded batch instead. Experimental one-condition patch did not remove source checks but worsened measured behavior:6,240->9,462lstats;373.57->430.17ms. Rejected. The small-file path bypassing the batch is therefore not by itself proof that using the batch is the repair.

Downloaded official fs-safe0.26.13 and matching Linux native package, verifying npm SHA512 integrity before extraction. Stock OpenClaw module with the newer library copied the same bytes in262.10ms, reducing some realpath/fstat work but leaving6,240lstats/800opens. Both stock and candidates rejected a source symlink escape and source replacement during open. These two negative tests are not comprehensive security equivalence proof.

A separate Marsha pair with memory/Slack enabled showed stock160.205s versus fs-safe0.26.13 125.121s; plugin phase47.987->43.585s. This is partial and order/cache-sensitive. No combined SDK+Slack+library result is claimed. A broad transitive library override is not the first production recommendation on this evidence.

## Attempts, failures and final cleanup

- First micro guard tried replacing source in the supplied copy callback. Stock small-file code never invokes that callback, so the test did not exercise the intended attack. This was a harness failure, not a discovered stock security bypass. Corrected to replace source during open; all four valid comparisons rejected it.
- Candidate preparation initially assumed an existing native SQLite addon file. None was present in that package. Copied the actual existing SQLite package instead and retained disableHistory=true; the functional test passed without invoking an unproven native-history path.
- Memory functional test passed before cleanup hit Docker inspect name ambiguity: test container and network shared a name, and inspect found the network after the --rm container exited. Corrected helper to inspect --type container, explicitly removed the labeled Qdrant/container/network, and verified absence. No production resources were removed. Test pass is retained separately from this cleanup failure.
- A local PowerShell report-display expression had a parse error before executing its remote command; corrected and reran the readback.
- All five Gateway starts reached the selected marker and preserved production IDs/PIDs/images/restart counts. Clone configs restored byte-for-byte. Final40 production containers running, configured health checks healthy, Marsha/Terry healthy with zero current restarts/OOM. No remaining mechanism-fixture containers or networks. Private raw logs/profiles/receipts remain under /opt/openclaw/backups/startup-mechanism-20261024; sanitized results/source under docker/startup-mechanism-20261024.

## Recommended treatment and remaining boundary

For Terry, use a clean dependency build with SDK3.3.1 and only his configured adapters, retaining customized plugin code, existing model/embedding routes, memory namespaces/Qdrant collections and history policy. A normal update of the unchanged latest plugin1.2.1 would reinstall its3.0.7 pin and is not this repair. The diagnostic mount override is not a durable deployment mechanism: prepare a consistent plugin project/package/lock and verify supported installation/recovery before live cutover. Never ship a stale package-lock or allow the next Doctor/update to silently restore the old SDK.

For Marsha, disable only the unused OpenClaw Slack plugin after the normal configuration/lifecycle acceptance gate; preserve her configured Discord/Telegram/Hindsight. Do not disable Terry's configured Slack channel.

For both, the shared source-custody/file-check cost remains. Native addon absence, a corrupt session database and extraction-model latency are not supported root diagnoses here. Dependency trimming and eliminating unused plugin admission treat proven amplification. A complete shared-loader fix still needs integrity-preserving implementation and broader compatibility tests; neither candidate gets startup down to the minimal-core baseline or proves the RAM target.

No production deployment authorized or performed by this diagnostic pass. Before live SDK repair: consistent supported package/lock installation, exact candidate archive/checksum, tested rollback inputs, idle gate, fresh backup, one-agent managed activation and actual plugin automatic save/recall/channel/tool acceptance. These deployment tasks are not represented as already completed by the SDK fixture. No permission request is made for an unprepared production release.

## Primary-source context

[Mem0 plugin1.2.1 metadata](https://registry.npmjs.org/@mem0%2fopenclaw-mem0/1.2.1) pins3.0.7; [SDK3.0.7](https://registry.npmjs.org/mem0ai/3.0.7) and [SDK3.3.1](https://registry.npmjs.org/mem0ai/3.3.1) package metadata and tarballs were inspected directly. [fs-safe changelog](https://github.com/openclaw/fs-safe/blob/main/CHANGELOG.md) records newer read/metadata optimizations. [OpenClaw167516](https://github.com/openclaw/openclaw/pull/167516) is already represented by installed batching; [168313](https://github.com/openclaw/openclaw/pull/168313) describes the small-file copy path. Their existence is not proof of a missing fix locally. [166020](https://github.com/openclaw/openclaw/issues/166020) corroborates the remaining broader source-validation problem.
