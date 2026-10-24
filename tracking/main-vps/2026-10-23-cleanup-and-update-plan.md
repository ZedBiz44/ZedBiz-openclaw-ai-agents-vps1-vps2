# VPS1 cleanup and proposed update bundle

Verified October 23, 2026, America/Edmonton. Owner: Cody. Operating owner: Victor.
Workstream: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/480

## Scope and current state

Jack requested cleanup first, then a concrete list for OpenClaw 10.6, Node, Hindsight and other server/tool updates. This pass performs reversible cleanup and inventories proposed updates. No package upgrade, service restart, reboot, new schedule, access change or external test message is part of the cleanup.

Live host srv1404026 has eleven agents: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian and Wilma. All eleven run OpenClaw2026.10.4 and Node24.22.0. All eleven Asana sidecars also run Node24.22.0. Initial containers healthy with zero restarts. Baseline disk: about40GiB free,90% used. That is limited headroom for new images and offline backups, not an outage.

Current image families include the shared base plus Amanda, Grogar, Maggie, Marsha, Victor and Wilma variants. Today's deployed Wiki-lock layer is required for all eleven writers. Main branch does not contain all deployed changes; reconcile the maintenance stack and PR479 before building. Never rebuild from main alone and silently lose deployed fixes.

## Cleanup decisions

- Consolidate783 dated loose backup files from agent root/config/workspace into eleven protected archives. Verify each file's bytes, permissions and ownership; preserve exact restore manifests. Current files and rolling recovery files are excluded. All11 current config/instruction/startup/image checks passed afterward.
- Losslessly compress historical October 18 and October 3/17 uncompressed state archives. Verify the decompressed SHA256 equals the original archive, parse every tar entry and test extraction before unlinking the uncompressed duplicate. Every recovery point survives. New companion receipts map old .tar references to .tar.gz (October 18) or .tar.zst (older archives) and explain restoration.
- Archive two obsolete Amanda/Victor extracted rehearsal trees, preserving their actual post-rehearsal contents independently of the original state backup. Require no mounts/open files/process working directories; verify every file and symlink before removing the exact extracted tree.
- Retain live databases, session history, credentials, skills, active npm generations, business projects, media, model caches, current image archives and recovery manifests. Do not call these junk based on size.
- Retain Hindsight's existing encrypted scheduled backup set. Its14-day policy is already operating; do not add another job or impose an arbitrary shorter retention.
- Retain the unreferenced Docker volumes until their recovery role is established. Inspection found about 1.82 GB in an October 18 PostgreSQL 18 volume, 0.93 GB in legacy Hindsight data, and 48 MB in a Mem0 development PostgreSQL volume. These are database contents, not established disposable caches. Other unused volumes contain tiny Caddy/Filebrowser state or are empty. No broad system/volume prune.
- Edith has about12.8GiB in project folder-cleanup working material; Vivian has about14.8GiB of media projects. No asset deletion without source/duplicate/ongoing-use evidence. Whisper model cache is retained because it supports a tool.

Cleanup completed at 18:47 MDT on October 23 (00:47 UTC October 24). All 22 historical archives passed original-versus-decompressed SHA256 verification, full tar traversal and sample extraction. Their file sizes fell by 60,812,943,784 bytes (56.64 GiB). Both rehearsal archives passed every-file verification before their extracted folders were removed: 121,872 entries preserved, with a further 4.89 GiB reduction in regular-file bytes. All 783 dated loose files are preserved in eleven verified archives, reducing their file bytes by another 8,538,136 bytes. These file-size reductions are distinct from allocated filesystem blocks.

Final filesystem free space was 101.07 GiB, about 74% used, compared with approximately 40 GiB free and 90% used initially. Ordinary live activity can affect the exact free-space delta. All eleven agents passed container health, public HTTP 200 health endpoints, zero restarts, no OOM flag, unchanged running image and unchanged baseline configuration/instruction/startup-file hashes. Their recovery image identities, startup-wrapper hashes and archive paths also passed. This is cleanup acceptance, not an all-clear for unrelated incidents or a model/memory capability test. No software updates were installed.

Sanitized evidence: [cleanup verification](2026-10-23-cleanup-verification.json). Private per-file restore manifests and archives remain under `/opt/openclaw/backups/cleanup-20261023`; archive-compaction receipts also live beside each historical recovery point. Existing dated records are preserved; use the companion receipt to resolve a former raw `.tar` path. Restore into an empty private staging directory, never over live production state.

Initial directory sizes were occupied bytes, not promised savings: backups 165.7 GiB, image recovery 30.0 GiB, agents 67.3 GiB, Hindsight service directory 10.9 GiB, mostly scheduled backups. Retained business assets and legacy database volumes require separate ownership/duplicate/recovery evidence before any further deletion.

## Proposed primary update bundle

| Component | Installed | Candidate | Decision and required proof |
|---|---|---|---|
| OpenClaw, all11 | 2026.10.4 | 2026.10.6 | Update in new immutable images, with restored-copy migration rehearsal and per-agent acceptance. |
| Node, gateways and11 Asana sidecars | 24.22.0 | 24.22.1 | Required security patch; remain on Node24. Verify running executable, not only package metadata. |
| Custom Asana MCP protocol SDK | 1.32.1 | 1.32.2 | Candidate patch alongside Node rebuild; preserve tool catalog, own-user identity and custom native-heading behavior. Express5.3.0 and jsdom30.1.3 already match latest. |
| Bundled/managed OpenClaw plugins | Mostly2026.10.4 | Core-matched2026.10.6 | Use supported core migration/convergence. Do not update arbitrary transitive dependencies independently. |
| Hindsight API, central shared service | 1.0.0 custom FlashRank image | 1.1.0 pinned digest with preserved FlashRank | Rehearse schema migration on restored PostgreSQL; preserve models, embeddings, bank ownership and routing. |
| Hindsight OpenClaw plugin, Gohzed/Grogar/Inga/Maggie/Marsha | 1.0.0 | 1.2.0 | Pilot direct recall/retain/reflect and knowledge tools, automatic capture and fresh-session persistence. Keep knowledge deletion disabled. |
| Codex executable, all11 | 0.163.0 | 0.164.0 | Candidate OAuth/model/tool proof before activation. |
| Gemini CLI, all11 | 0.64.0 | 0.65.0 | Verify installed and effective mounted wrapper; preserve credentials and request behavior. |
| GOG | 0.45.0 | 0.47.0 | Preserve draft-only safety wrappers; test argument handling and authenticated Drive read. |
| GitHub CLI | 2.102.0 | 2.103.2 | Verify pinned binary/checksum and existing authenticated read. |
| summarize | 0.25.2 | 0.25.3 | Harmless local-text/URL read test; preserve model/auth defaults. |
| mcporter | 0.15.0 | 0.16.0 | Verify existing configured MCP catalog/read; no new connector permissions. |
| yt-dlp | 2026.08.19 | 2026.10.21 | Metadata-only test against an appropriate existing media source. |
| rclone | 1.75.1 | 1.75.2 | Existing remote read/list only; no sync/delete test. |
| pandoc | 3.12 | 3.12.1 | Small local document conversion. |
| uv | 0.12.22 | 0.13.5 | Test existing Python tool environments; retain old tool environments until acceptance. |
| npm | 12.2.0 | 12.2.1 | Build-time tooling candidate; verify compatibility and lockfiles. |
| fzf / just | 0.74.4 / 1.58.0 | 0.74.5 / 1.59.0 | Low-priority image tool patches; local smoke tests. |
| camsnap / goplaces | 0.6.0 / 0.4.11 | 0.6.1 / 0.4.14 | Optional; confirm actual capability use and no paid-operation smoke test. |

The newer Hindsight plugin supplies the restored direct tools. A backend update alone does not expose them. Neither change grants broader memory-bank access or makes the unsupported Memory Wiki bridge work. Keep approved wiki-only search and the cross-container lock. Rocky's installed versions are useful evidence, but his latest record still leaves real-chat automatic memory acceptance pending; do not claim his upgrade is a fully passed pilot for VPS1.

## Host packages

Read-only simulation from existing apt catalogues lists17 upgrades, no additions or removals. Recheck refreshed metadata and exact transaction before installation. This inventory did not install packages.

| Group | Installed to candidate | Proposed treatment |
|---|---|---|
| Docker engine/CLI/rootless extras | 29.9.1 to29.9.2 | Separate controlled host-service window; cold image recovery and all-agent idle checks first. |
| containerd.io | 2.4.2-2 to2.4.2-3 | Same package family; accompany Docker maintenance after compatibility review. |
| Buildx / Compose | 0.38.0 to0.38.1 /5.6.0 to5.6.1 | Include with tested Docker tooling. |
| zlib1g | Ubuntu1.3.dfsg-3.1ubuntu2.2 to2.3 | Security patch candidate. |
| GLib group,4 packages | 2.80.0-6ubuntu3.9 to3.10 | Keep matching versions together; review restart requirements. |
| 1Password CLI | 2.41.0 to2.41.1 | Test actual existing CLI service-account route and managed startup. Do not send its CLI token to Connect API. |
| Tailscale | 1.104.1 to1.104.2 | Verify existing administrative path before/after; no ACL or network-policy changes. |
| tmux | 3.4-1ubuntu0.1 to0.2 | Optional maintenance patch. |
| Ubuntu Pro client/l10n | 37.2 to38 | Optional; no subscription change. |
| cloud-init | 26.1 to26.2 | Defer from core bundle unless reviewed need; do not force phasing. |

No reboot-required marker at preflight. This does not prove no process will need restarting after future package updates. A reboot is a separate decision, not part of cleanup.

## Keep or defer

| Component | Finding | Decision |
|---|---|---|
| Mem0 plugin, Edith/Terry | 1.2.1 equals npm latest | Retain pinned package and compatibility patches; verify against10.6. The misleading timeout warning is a separate known bug, not proof of failed recall. |
| Notion MCP / Asana npm MCP | 2.5.2 /1.8.0 equal latest | Retain; test actual integrations. Custom Asana sidecars still need Node patch and native-heading/identity regression tests. |
| Asana API SDK inside custom sidecars | 3.0.12; latest3.3.0 | Separate candidate compatibility test before choosing upgrade. Do not confuse this with the unchanged Asana MCP package or protocol SDK. |
| Himalaya / ClawHub / xurl | 2.2.1 /0.23.3 /1.3.4 equal latest | Retain existing safeguards/configuration. |
| yq, glow, eza, duf, freeze, vhs, git-cliff, grex, blogwatcher | Installed versions match queried releases | Retain. gron reports dev; verify artifact checksum before calling its provenance confirmed. |
| debugpy / nano-pdf | Source pins1.8.22 /0.2.1 match latest | Retain; effective environment selection still belongs to build acceptance. |
| Corepack | 0.36.0 equals latest | Retain. |
| FFmpeg | Existing custom August19 build | Retain pending capability-specific review; do not replace a custom build based only on version age. |
| Marsha voice-call package | Retained 2026.9.8 generation found; current config explicitly disables voice-call and excludes it from the allow list | Inactive package, not an active plugin outage. Leave capability disabled; let supported plugin convergence handle retained generations during the core update. |
| PostgreSQL | Live18.6, pg18 image | Retain major/image through Hindsight migration; no database-major upgrade. |
| Qdrant | 1.19.2; newer1.20.0 available | Separate Mem0/client compatibility pilot. Do not bundle an untested memory database change. |
| Caddy / Filebrowser / Docker socket proxy | 2.11.7 /2.63.23 /0.5.0 match latest | Retain. |
| Portainer | 2.45.2 to2.45.3 available | Optional separate dashboard patch. |
| Uptime Kuma | 2.5.6 to2.5.7 available | Optional; upgrading it does not fix the separately recorded missing-monitor coverage. |
| Dozzle / Homepage | 11.3.2 to11.3.4 /2.6.0 to2.7.0 | Optional separate dashboard changes. |
| 1Password Connect | Installed1.8.3 digest confirmed against vendor registry;1.8.4 available | Separate API/sync pair patch candidate. Require vendor-note review, preserved data/config and actual authenticated Connect proof; the working op CLI token is not a Connect token. No credential or account changes. |
| Shared allocator/mirror/restart bridges | Custom deployments | No automatic dependency upgrade; preserve existing source and service behavior. |

## Release gates and order

### Jack's Terry-first planning decision

Jack selected Terry as the first OpenClaw 2026.10.6 pilot and requested a plan before authorizing execution. No upgrade is authorized by this planning request. Fresh registry checks confirm Mem0 1.2.1 remains current, Hindsight plugin 1.2.0, LanceDB plugin 2026.10.6, Codex 0.164.0, Gemini 0.65.0, Notion MCP 2.5.2, Asana MCP 1.8.0, MCP protocol SDK 1.32.2 and Asana API SDK 3.3.0. Installed versions above are from the completed live cleanup inventory. A subsequent read-only SSH attempt could not use the temporary key because that file is now absent; do not infer failed server health or credential rotation from that result. Revalidate approved access, live versions and refreshed package candidates before execution.

Proposed execution batches, after Jack starts the work:

1. **Prepare Terry.** Record current image, effective settings, Mem0 routing, jobs, active work and resource baseline. Preserve deployed Wiki locking, memory-limit fixes, startup secret handling, model selections and communication safeguards. Back up Terry and his Asana sidecar configuration; preserve exact old images and prove recovery in an isolated restored copy. Build pinned candidate images, not live npm overlays.
2. **Terry core/runtime pilot.** Upgrade OpenClaw 2026.10.4 to 2026.10.6, Node 24.22.0 to 24.22.1 and selected core-managed plugins together. Keep Mem0 1.2.1 and shared Qdrant 1.19.2 initially. Patch Node in Terry's Asana sidecar separately with its own before/after checks. Do not change the shared Hindsight service in this batch.
3. **Terry tools pilot.** Once core/runtime passes, test and apply the proposed CLI/tool updates in a separately identifiable image revision. Test MCP protocol SDK 1.32.2; treat Asana API SDK 3.3.0 as a separate compatibility decision. Check actual model response, tool availability, existing-memory recall, approved test-memory persistence across a new session, Asana own-user identity, Notion/Drive read, channel connectivity, startup and schedules. No outbound test messages without authorization. Compare gateway, workers, connectors and sidecar RAM under the same workload; a healthy container alone is insufficient.
4. **Other memory families.** Propose Amanda as the LanceDB pilot, updating its managed plugin with core 10.6 and validating existing indexes/recall. Propose Gohzed as the Hindsight pilot, subject to current workload. First rehearse Hindsight 1.1.0 on a restored, isolated database with plugin 1.2.0. Prove existing memories, new memory, automatic capture in genuine sender context, routing, and permissions. Preserve PostgreSQL 18.6 and the custom FlashRank integration. Shared Hindsight activation needs compatibility checks for all VPS1/VPS2 consumers, including those still on old plugins; if mixed versions fail, prepare a coordinated service/plugin transition. Preserve an isolated rollback route for both database and image, not just the old image.
5. **Controlled agent rollout.** Present pilot evidence and obtain the rollout decision. Update remaining agents sequentially, covering every custom image family and each memory provider. Keep failed or skipped capability checks open; revert the affected agent on material regression rather than continuing the rollout.
6. **Shared services and host maintenance.** After application acceptance, handle Qdrant 1.20.0 as a separate Mem0 compatibility/migration test with snapshot restoration. Patch 1Password Connect API/sync together in their own tested window. Apply reviewed host security/library packages, 1Password CLI and Tailscale with access checks. Docker/containerd/Buildx/Compose need a separate planned interruption: live restore was false at inventory, so do not assume agents survive a daemon restart. Optional dashboards follow individually. Reassess reboot need from the actual transaction; do not reboot by default.

Every batch records exact versions, backup/restore evidence, behavior tests, resource comparisons and unresolved findings in GitHub, with a concise Notion journal update. Existing health issues are not closed merely because an update succeeds. The prior key-exposure review remains separate and unresolved; absence of a temporary file does not establish that keys were rotated.


## Evidence and sources

- Current VPS1 procedure: https://app.notion.com/p/37ba3e33d581816584cdf6b622a0d944
- Wiki lock implementation and upgrade gate: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/479
- Health follow-through remains open: https://github.com/ZedBiz44/z-agent-health-report-Skill/issues/6
- Prior VPS1 components: PR470; VPS2 10.6: PR478; Rocky: ZedBiz-openclaw-vps4 issue63/comments.
- OpenClaw release: https://github.com/openclaw/openclaw/releases/tag/v2026.10.6
- Node security release: https://nodejs.org/en/blog/release/v24.22.1
- Hindsight backend: https://github.com/vectorize-io/hindsight/releases/tag/v1.1.0
- Plugin behavior: https://hindsight.vectorize.io/sdks/integrations/openclaw
- npm registry latest metadata and official GitHub release APIs were queried October23 for every listed candidate. Candidate availability does not itself establish compatibility.

The operator accidentally printed SSH key material from the access file during initial discovery and disclosed this in chat. No keys were committed here. Credential rotation remains a separate unresolved security action; it was not performed during cleanup.


