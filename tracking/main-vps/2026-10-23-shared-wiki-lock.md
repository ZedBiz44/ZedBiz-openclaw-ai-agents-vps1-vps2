# VPS1 shared Wiki lock

Date: 2026-10-23 America/Edmonton | Agent: Cody | Status: Deployed and verified; source PR open

## Purpose and authorization

Jack approved a durable Wiki-lock implementation after asking whether it survives restarts and upgrades. Scope: the eleven VPS1 OpenClaw containers sharing `/opt/openclaw/shared/knowledge/wiki`. No OpenClaw version upgrade, provider replacement, credential change or manual business-page edit.

Workstream: [476](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/476). Source: [479](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/479). Daily Tech Updates: [Cody journal](https://app.notion.com/p/402a3e33d5818190ac79e7014ec55e2d).

## Diagnosis and implementation

The old coordinator serialized only calls inside one process. Earlier history showed 86 successful refresh/publication pairs without overlap; that history did not establish a persistent fleet-wide failure. On October 23, actual research produced Edith lint failures at 22:16:49 and 22:17:32 UTC while Marsha wrote the shared Wiki. Saved-page read-backs succeeded; no page loss was demonstrated.

Upstream #176839 introduced a shared lock but was absent from the inspected 2026.10.6 stable package. Its PID-based owner recovery was unsuitable for these separate container PID namespaces in an isolated test. The installed compatibility layer instead uses Linux flock on one stable shared inode, with a pipe from the Node owner to release ownership on process exit. It extends the original canonical-path queue and reentrant transaction scope. The full lint operation is wrapped because it writes a report after its internal compile returns.

Seven replacement image variants retain the actual customized 2026.10.4 image contents. All use the tag suffix `2026.10.4-wikilock-20261023`. The base-image variant serves Gohzed, Inga, Edith, Terry and Vivian; Grogar, Marsha, Victor, Amanda, Maggie and Wilma retain their named variants. Startup scripts run the baked-in verifier. An unsupported or missing patch prevents startup rather than silently dropping coordination.

## Tests and attempts

- Four independent containers incremented the same counter with no lost increments and non-overlapping critical sections.
- Nested coordinator calls completed; thrown mutation released the lock.
- Acquisition timeout was bounded and failed as expected.
- Killing the holder container released a waiting writer.
- Killing only the Node holder inside a still-running container released a waiting writer through pipe EOF.
- A restarted test container passed the installed guard.
- Three independent processes with separate caches performed actual imports and catalogue builds against a separate copy of the roughly 981-page Wiki.
- After adding the lint report wrapper, three concurrent actual import/compile/lint jobs all completed. Existing lint findings remained; this is not a content-cleanup claim.
- The unpatched image failed the upgrade guard as intended.
- JavaScript syntax checks passed locally. Windows' `python` alias was unavailable; Python syntax checks passed on VPS1.
- The rollout runner's initial host-side readiness request received HTTP 403. The check was corrected to the container-local route; this was a probe-access issue, not a failed Wiki lock.
- Ordinary Git commit succeeded; HTTPS push lacked noninteractive credentials. Identical source files were published through the connected GitHub app. No credentials were printed or changed.

## Persistence and recovery

Installation: `/opt/openclaw/recovery/wiki-lock-20261023`.

Recovery archive: `images.tar.gz`, 2,515,892,917 bytes; SHA-256 `cc7fec0088a2aa96d217732550fca2a3a51f8c2647dba8dbee48c5fca42bfc55`. Contains all seven new images and the unchanged Asana sidecar image. A full `docker load` succeeded.

Per-agent Compose, post-start and host-start recovery manifests are backed up under `rollback/AGENT`. The existing secret-aware startup wrappers are reused unchanged. Amanda, Maggie and Wilma had stale recovery-image references predating their workshop customizations; deployment corrects those references while preserving the actual running image customizations.

Rollback implementation restores the exact three original files and recreates the original image. Old images and archives are retained. For the three pre-existing stale manifests, exact rollback also restores that known prior manifest mismatch; repair it before relying on automatic missing-image recovery after rollback.

The stable lock file is `.openclaw-wiki/zedbiz-mutation.flock`; do not unlink it while writers may be running. External editing, file synchronization and writers on other servers are outside this same-host mechanism. Future OpenClaw upgrades require rebuilding and testing the layer or replacing it deliberately with a compatible official fix.

## Live rollout

All eleven agents (Gohzed, Grogar, Inga, Maggie, Marsha, Edith, Terry, Victor, Vivian, Wilma and Amanda) passed installed guard, default Wiki-only search returning a real page, and Discord connected/ready. The final fleet audit returned readiness HTTP 200 and Docker healthy for all eleven, with zero container restarts since their replacements.

Marsha and Victor initially returned the five-second foreground database-preparation warning. Their logs then confirmed background recovery, and subsequent live Wiki calls passed without database repair. Edith's mail_reader preparation likewise recovered. Mem0 agents took several minutes to load their existing plugin stack.

Direct `mem0_search` on Edith and Terry returned existing memories. Amanda, Victor, Vivian and Wilma's `memory_recall` returned existing LanceDB memories. Hindsight initialization logs on Gohzed, Grogar, Inga and Maggie retained their configured banks with automatic recall and retain enabled; this initialization check is not a separate Hindsight write test.

The final audit confirmed the same device/inode (2049/1059413) for the lock in all eleven containers, the correct patched image references, valid recovery-image IDs, unchanged credential-wrapper hashes, installed startup guards, and `search.corpus=wiki` everywhere. One initial Vivian readiness probe timed out during an actual Discord turn. Her work was not interrupted; the subsequent full audit returned 200 and healthy.

## Production concurrency verification

After all eleven images had been replaced, simultaneous actual `wiki_lint` calls through Maggie, Marsha and Edith all returned HTTP 200 and `ok=true`. Completion times were 26.20, 37.53 and 16.37 seconds respectively. No "changed while generating" collision occurred. Each reported the same 1,071 content warnings and zero lint errors, with its report saved to `reports/lint.md`. This verifies coordinated execution; it does not claim those content warnings were cleaned up. The isolated-copy tests separately exercised actual imports and catalogue builds without adding synthetic research pages to production.

Amanda's pre-deployment readiness HTTP 503 reported `agent-database:openclaw`, an unused-agent startup inspection issue. Her first post-replacement probe also returned 503 while Wiki search and Discord worked. Her subsequent readiness check and final audit returned 200 with no failing entries. The warning cleared during this restart; the underlying 2026.10.4 startup behavior was not patched or claimed permanently repaired.
