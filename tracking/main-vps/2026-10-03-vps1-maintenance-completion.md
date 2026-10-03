# VPS1 maintenance and cleanup

Date: 2026-10-03 | Agent: Cody | Status: Live maintenance verified, compatibility holds retained

## Scope and result

Jack authorized completing VPS1 updates and reviewed cleanup. Other hosts were excluded. All eleven agents run OpenClaw 2026.9.8 and Codex 0.160.0. Terry, Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Victor, Vivian and Wilma select GPT 6.1 Sol through their existing Codex OAuth profile. Marsha selects GPT 6 Astra through the same OAuth route. Each passed a fresh exact-model run with shell and external-memory tools, no fallback and zero tool failures. Paid API defaults remain prohibited without Jack's explicit approval. Existing non-agent services and background-provider settings were preserved; this is not a claim that every integration is free.

The host runs kernel 6.8.0-146-generic, Docker 29.8.2 and containerd 2.3.6. A fresh apt index check returned no pending upgrades. No failed systemd units, dpkg audit problems or reboot-required flag remain. Services affected by maintenance were restarted and verified.

## Updated applications and connectors

| Component | Verified version/result |
| --- | --- |
| OpenClaw | 2026.9.8, all eleven agents |
| Codex | 0.160.0, supported executable override and OAuth-only OpenAI agent profile order |
| Official OpenClaw external plugins | 2026.9.8; native update dry-runs report no pending updates |
| Mem0 plugin | Terry and Edith 1.2.1; explicit retention and distinct recall aliases preserved |
| Hindsight plugin | 0.13.0 on Marsha, Gohzed, Grogar, Inga and Maggie |
| Hindsight service | 0.10.2, FlashRank 0.2.10; external database connected |
| Qdrant server | 1.19.1; authenticated collection queries pass |
| PostgreSQL / pgvector | PostgreSQL 18.6, refreshed image; vector extension upgraded to 0.8.7 |
| Portainer | 2.45.1 |
| Dozzle | 11.2.0 |
| Homepage | 2.4.0 |
| File Browser | 2.63.23 |
| Docker socket proxy | 0.5.0 |
| Uptime Kuma | 2.5.5, database migration passed; prior database had no monitors or notifications |
| Caddy | 2.11.6, latest published official Docker image at verification |
| 1Password Connect | Existing API and sync images match latest pulled images |
| 1Password CLI | 2.40.0 |

Shared global npm tools return no outdated packages. The base includes Gemini CLI 0.62.0, Notion MCP 2.5.2, Asana MCP 1.8.0, Codex 0.160.0, xurl 1.3.4, ClawHub 0.23.3, Corepack 0.36.0, npm 12.2.0 and Node 24.21.0. Custom Asana servers, Z-Code services and restart/tunnel bridges retain their deployed custom versions and are running; they do not have a universal upstream release to install. Historical project lockfiles were not bulk-upgraded.

## Skills and video tooling

- Verified 26 ZedBiz source repository heads. Deployed 213 reviewed file changes across eleven agents, covering nine skills. Amanda's pilot passed native and central runtime validation plus a fresh live model test before the fleet rollout.
- Preserved Edith's approved project-specific file rules. Retained newer local knowledge retention and routing instructions where upstream would regress them.
- Updated Vivian's twelve official Remotion skill packages to 4.0.532, commit `e385a83dbde54179c0457ad90b7d7c3a4b6ab44a`. All passed runtime validation. A fresh Vivian run read the installed files and correctly confirmed finished-video delivery and permission boundaries.
- A thirty-frame local H.264/AAC render at 720×1280 and full FFmpeg decode passed. The first attempt used an incorrect entrypoint; retry used the existing `src/index.jsx`. Existing production project dependencies remain consistently pinned to their project versions.
- Moved eleven dated skill backup directories out of active skill discovery into each workspace's backup area, retaining their contents.

## Cleanup and recovery

- Verified retained full agent backup checksums and the older Marsha archive before deleting the reviewed September 1 backup set. That deletion recovered 12,913,668,096 filesystem bytes, about 12.0 GiB.
- Removed thirteen specifically reviewed retired containers and seven unused image IDs. Preserved every Docker data volume and current rollback images.
- Retained fresh offline Marsha state, agent recovery archives, application config/data backups and a full PostgreSQL volume backup. Database backups and raw configurations stay protected on VPS1; published evidence excludes credentials.
- Final disk snapshot: 209 GiB used, 179 GiB available, 54% used. This includes newly created recovery backups; it is not a net-cleanup calculation.

## Resolved maintenance failures

- Marsha's old startup helper referenced a renamed OpenClaw module and caused a restart loop. Updated the exact module reference for 9.8; preserved the existing Workshop model setting and tested owner scheduling predicates. Marsha's final Astra, shell and Hindsight recall proof passed.
- Native plugin updates saved new generations but some runtime applies failed because the managed package lacked the OpenClaw host peer. Linked the supported host peer and verified the installed plugin versions.
- Edith's Mem0 update required reapplying the reviewed explicit-retention patch, restoring the compatible Qdrant client and accepting the alias tool contracts. Online activation encountered a stale lifecycle lease. Stopped the temporary helper, allowed lease expiry, accepted the contract with the gateway offline and restarted. Final live `mem0_search` passed on Sol.
- Hindsight's first Compose activation used the wrong project name and hit a container-name conflict. Restored service, then activated using its existing `hindsight-central` project. Database-connected health and all five agent recalls passed.
- Requested Caddy 2.11.7 and an unprefixed socket-proxy tag were not published. Used the verified published Caddy 2 image and socket-proxy v0.5.0.
- Local repository-mode skill lint encountered a missing YAML library and pre-existing documentation layout warnings. Target runtime validation with the correct dependencies passed; this record does not claim repository-documentation lint passed.

## Explicit compatibility holds

- Himalaya remains 1.2.0. Version 2.2.1 is staged but changes command, mailbox, configuration, authentication and draft interfaces. VPS1 email integrations require a separate migration and live account verification before replacing it.
- Mem0's Qdrant JavaScript client remains 1.18.0 because the newer client removes the `search()` interface used by the installed SDK. This does not block the Qdrant server upgrade.
- Caddy source release 2.11.7 exists but its official Docker tag was unavailable; the deployed published image is 2.11.6.
- Local `z-record-knowledge`, `z-knowledge-routing` and `z-code-allocation` changes are retained where current upstream conflicts with Jack's retention, Notion prompt routing or working shell formatting. The deployment manifest records the exact held files.
- Frozen creative project lockfiles and custom service dependencies are not asserted to be the newest available transitive releases. Their working versions were preserved.

## Source and evidence

Sanitized evidence is in [the maintenance evidence folder](2026-10-03-maintenance-evidence/). Application image digests, backup locations, plugin inventory, source heads, deployment hashes and individual model/tool run IDs are recorded there. Marsha's image recipe and scheduling patch, Hindsight's current external-database Compose definition, maintenance scripts and official Remotion sources are included in this change.

- [Host maintenance issue](https://github.com/ZedBiz44/ZedBiz-general-tech-issues-updates/issues/94)
- [OpenClaw and OAuth issue](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/436)
- [Implementation PR](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/437)
- [Cody daily journal](https://www.notion.so/3eea3e33d581814bb8a5faa6ae82ef9e)

No additional VPS1 host restart is required. This is a verified maintenance pass with the listed compatibility holds, not a claim that every stored project and dependency is on its newest upstream version.
