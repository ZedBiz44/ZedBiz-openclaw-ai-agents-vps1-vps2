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
- Staged Doctor migration in progress. Legacy webhooks migration warning retained, not hidden. Live gateway migration and functional verification remain pending.

## Rollback

Stop only Amanda if activation fails, preserve post-change evidence/state outside her live tree, and restore the complete pre-update archive into an empty Amanda tree; do not overlay9.8 onto migrated10.4 databases. Use the9.8 recovery gateway and recovered Asana image with the saved pre-change Compose and OP launcher. Preserve original startup repair and timeout0. Verify database integrity, gateway health, model/tools/memory, Asana and channels after rollback. Do not restart other agents.
