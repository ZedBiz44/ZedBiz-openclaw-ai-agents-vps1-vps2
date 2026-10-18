# Amanda 10.4 update and recovery

Parent: [issue459](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/459). Source: [draft PR464](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/464), stacked on Victor PR460. Jack explicitly authorized Amanda after Victor's pilot. No further rollout is authorized.

## Recovery point and provenance

- VPS1 `srv1404026`, `/opt/openclaw/agents/amanda`. Gateway and custom Asana container/images were absent. Saved state remained. Removal cause is unproved.
- Full offline archive `/opt/openclaw/backups/amanda-20261017-pre-10.4/amanda-offline-state.tar`, SHA256 `d2aad38a37f3b61d5b4e0edbaf338f75d611951a1874a6830de1dc55f69b7f86`. Archive listing passed; extracted core and main databases both passed SQLite quick_check (schemas19 and24).
- Remote protected work directory `/home/jackadmin/amanda-10.4-20261017`; private logs and migration captures stay there. No resolved secrets committed.
- Gateway candidate `zedbiz/openclaw-amanda:2026.10.4-pilot-20261017`, image `sha256:4e5f5b8536785b8307d44e4e5ec1d83449976e149c5cd18e515880ec7336665a`. Built from Victor's tested shared10.4 base, without Victor-specific Docker/SSH privileges.
- Recovery gateway `zedbiz/openclaw-amanda:2026.9.8-recovery-20261017`, image `sha256:8a8089473585b40067eb617981fcc627b72f681eb6ee684be4fddde2627a2bf6`, rebuilt from Amanda's retained October12 Dockerfile and dynamic-memory module.
- Custom Asana source recovered from Amanda's saved source tree; `recovery-sources/amanda-asana` includes package lock, advanced tools, session recovery, and September29 native-heading schemas. Image `zedbiz/asana-http-mcp:2.0.0-amanda-recovery-20261017`, ID `sha256:8d0560464a3b4f0f5dcc8de88f2549934582aa649aadcc2ccfc403ad19905b94`.

## Completed gates

- Dynamic container memory-limit patch retained; six behavioral tests in its build passed.
- Amanda's live-owner protection ported to10.4. Six tests passed against the actual module: live handle, embedded run, active lane, stale generation, terminal worker, ownerless stale session. No arbitrary elapsed cutoff introduced. Configured timeout remains0.
- Asana build typecheck and catalog passed:76 standard tools,126 advanced tools. Live sidecar restored. Authenticated MCP read verified Amanda user1213974002925107, all126 tools, three native-heading schemas. No external writes. An initial connection attempt preceded listener readiness; retry after startup passed.
- Staged and live Doctor migrations completed. Core schema19→20, main schema24 unchanged. Both databases passed quick_check. All10 cron rows exactly equal before migration, after rehearsal, and after live migration. This verifies preservation, not future scheduled-run results.
- Actual stage OAuth GPT6.1Sol receipt `ac356c85-70cf-41b5-bdc8-6860012d8e6a` passed shell and memory with no fallback or tool failures. Stage bridge deliberately had no live-sidecar DNS; independent sidecar and integrated live tests cover that route. Stage one-shot Codex cleanup warning retained; no such failure was reported by the successful live proof.
- Live receipt `1f11b41d-bbf8-44b0-a753-3fe4a6aadfb4` passed OAuth GPT6.1Sol, bash, memory_recall and `asana.asana_get_user` (Amanda1213974002925107), zero tool failures/no fallback. No external test messages or Asana writes. Existing channels resumed naturally on startup.
- Both containers Docker healthy, zero restarts/OOM. Local and public `https://amanda.zbiz.ca/healthz` passed. Discord and Telegram report running and connected. OpenClaw2026.10.4(383c124), Codex0.160.0. Nine official external plugins upgraded to10.4: deepseek, discord, gradium, memory-lancedb, moonshot, parallel, perplexity, qwen, tavily; bundled Codex/OpenAI10.4 loaded.
- Original OAuth profile, fallback chain, thinking, timeout0, memory slot and schedule records retained. Live merged AGENTS17,216 characters fits the original20,000-character budget (rehearsal initially used24,000 from Victor's helper; Amanda did not need that increase). TOOLS migrated by Doctor with dedicated backup directory owned1000:1000 mode0700. Original startup script saved;9.8-only runtime patch replaced with10.4 verification and image-baked safeguard.
- Gateway readiness took96seconds; an early HTTP check timed out during startup and then passed. Docker's existing3-minute health interval delayed its healthy label until the next check; no health settings changed. Initial Windows tar directory-mode extraction failed, corrected only inside the new build directories; no live data was affected.

## Memory and remaining follow-up

At22:41:53MDT, whole gateway container working set2.005GiB plus70.5MiB Asana, with0 swap/OOM. At22:42:22 it was1.939GiB plus70.5MiB, approximately2.01GiB combined (about2.16decimalGB). Raw cgroup usage2.252GiB included0.314GiB inactive file cache. Live allowance remains5GiB RAM/6GiB RAM+swap; sidecar384MiB RAM. These are post-proof snapshots with Codex and worker processes present, not a sustained idle benchmark. Startup gateway RSS1.79GiB crossed its existing1.5GiB warning threshold. Do not suppress the warning, claim a leak repaired, or raise limits as a substitute for diagnosis. Victor owns continued fleet-health follow-through under issue6.

Legacy webhooks migration remains pending with no plugin state/blob rows. Doctor's account-suffixed model inspection warning is contradicted by the actual successful model tests; retain it as a diagnostic limitation. Existing missing policy.jsonc, LAN bind, legacy browser relay and credential-storage maintenance are not fixed by this update. Image/container removal cause remains unproved. No security/credential changes or wider rollout performed.

Shared Technical Journal, Amanda Registry, deployment and container records are reconciled to this result. PR464 contains source/evidence, remains draft and is stacked on Victor PR460; this does not claim the deployed source is merged to main. Parent459 and health6 stay open for unresolved follow-ups.

## Rollback

Stop only Amanda if activation fails, preserve post-change evidence/state outside her live tree, and restore the complete pre-update archive into an empty Amanda tree; do not overlay9.8 onto migrated10.4 databases. Use the9.8 recovery gateway and recovered Asana image with the saved pre-change Compose and OP launcher. Preserve original startup repair and timeout0. Verify database integrity, gateway health, model/tools/memory, Asana and channels after rollback. Do not restart other agents.
