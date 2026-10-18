# VPS1 component maintenance — 2026-10-18

Jack authorized Hindsight, installed tools, Docker and host maintenance across VPS1/VPS2/VPS4. This record covers VPS1. SOPs and prompt amendments remain in Notion. Protected evidence is under `/opt/openclaw/backups/components-20261018`.

## Components

- Gateway component images preserve each accepted OpenClaw 2026.10.4 cohort's customizations, while updating Node to 24.22.0, Codex to 0.163.0 and Gemini CLI to 0.64.0. No runtime npm overlay replaces the accepted core.
- Hindsight API 1.0.0 uses the pinned upstream digest with the existing FlashRank 0.2.10 customization. Existing PostgreSQL and bank routing are preserved. A restored database passed old-memory recall, new retention and persistence before activation. The encrypted database backup was copied off-host and checksum-verified.
- Official Hindsight plugin 1.0.0 replaces 0.13 for its existing cohort. The release removes the old `agent_knowledge_*` tools; automatic recall/capture is tested with valid channel and synthetic maintenance sender context. Existing provenance warnings remain documented; no trust bypass or bank merging is used.
- Shared tools: GOG 0.45.0, summarize 0.25.2, mcporter 0.15.0 and ntn 0.23.20. Existing GOG keyring loading and draft-only guard are retained. File-bound ntn requires container recreation to see the new inode.
- Shared services activated: Qdrant 1.19.2 (collection counts 618/3565/1 preserved), Caddy 2.11.7, Homepage 2.6, Dozzle 11.3.2, Portainer 2.45.2 and Uptime Kuma 2.5.6. Health/public-route checks passed; previous images/data retained.
- 1Password Connect API/sync updated 1.8.2 to 1.8.3 with pinned official image digests. Database and cached account-data checks passed. The old saved Connect test token returned 401 before the update; authenticated Connect reads are not claimed. Agent launchers use the separate existing service-account CLI route. File Browser 2.63.23 and Docker socket proxy 0.5.0 already matched current published images.
- Asana dependencies: SDK 1.32.1, Express 5.3.0, jsdom 30.1.3, esbuild 0.28.2 and scoped Babel CLI 8.0.6. Standard/Advanced/Edith variants passed build, catalog and audit checks. Isolated real-user comparisons preserved 76/126/76 tools and each identity. Edith's custom pagination remains intact.

## Recovery and failures

- The first component archive contains eight image identities and independently restored into an empty production-format Docker/containerd store. SHA-256: `2697b7fe25bb3f3ef0cc12e4b15b36b87bd7760a1e7724e2476ca16e92652c1e`.
- The expanded archive includes both new Asana variants: `/opt/openclaw/recovery/components-asana-20261018/images.tar`, SHA-256 `e2d88a7bada2f068f1cdd25ad83b70e88df614393af068142efd3f0cc760b722`. All ten image IDs and executable versions passed independent restore. Each deployment refreshes its protected recovery manifest.
- Wilma/Vivian initially hit fresh previous-owner heartbeat errors after replacement. Their shell launchers did not forward the stop signal to the gateway, and default Docker stop grace was too short. The rollout now uses `exec`, a 330-second container grace period and a bounded previous-owner lease wait. Host maintenance also aligns the outer systemd timeout to 360 seconds. Vivian's controlled graceful stop exited successfully in about 2.4 seconds.
- Terry's first startup spent several minutes recovering stale database ownership, temporarily using a CPU core and not answering health checks. Read-only syscall/CPU diagnostics were retained; the temporary localhost inspector was closed. He recovered without crash/OOM, then passed real Mem0, own Asana and Notion acceptance. The subsequent controlled restart must verify the corrected shutdown path.
- Inga's first Hindsight acceptance gate falsely failed because ANSI colour codes split a log marker. Stripping ANSI allowed verification against the already successful receipt; no repeat external action was needed.
- Inga/Maggie's initial plugin-only tar captured an empty mountpoint. The retained full pre-core archives were verified to contain the actual old plugin tree, and explicit rollback-reference receipts pair that tree with the new matched state backup. Later plugin backups use the real host `npm` directory. The empty tar is not represented as valid recovery.
- The Asana candidate first failed local tar extraction permissions and then Docker's absent default bridge. Candidate-only permissions and `--network host` fixed those build conditions. A production audit caught four transitive advisories; a non-force lock refresh resolved them before rollout. Isolated MCP probes initially omitted bearer authentication or used a disallowed hostname; final probes used the existing token and supported localhost route, without allowlist changes.
- Marsha's live prompt had one removed ingest-command instruction. A single-line compatibility amendment preserved all other bytes and remains below the configured prompt budget. The current Notion amendment supersedes older historical full-prompt directions; no prompt copy is published here.

## Rollout status

Implementation and first cohort acceptance are recorded. The sequential remainder, Docker/containerd host activation and final simultaneous fleet acceptance are still in progress at this commit. Do not treat this intermediate record as full completion. Final results will be appended after live verification.
