# VPS1 shared Wiki filelock rollout — October 26, 2026

Author: Cody. Status: live deployment and recovery publication complete. Jack authorized the implementation after the library comparison. Source: [PR 499](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/499), stacked on PR 482; no merge is claimed. Tracking: [issue 476](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/476).

## Result

All eleven VPS1 agents now use the official, unmodified Python `filelock` 4.2.1 package for shared Wiki lock acquisition. Node retains the descriptor for the entire mutation; Python exits after acquisition. A separate holder can no longer disappear while Node continues writing without its lock. The existing transaction queue, nested operations and full lint wrapper remain necessary integration code.

Each image was built on its exact current customized base, preserving the October 26 MCP/Asana fixes and original runtime configuration. The final audit confirmed all eleven healthy, all configured channels running/connected, unchanged agent configurations and startup wrappers, correct image/recovery pins, and the original shared lock inode: device 2049, inode 1059413. Every actual gateway command requires post-start success before launch. Persistent gates reject old or altered integrations.

Marsha's Slack plugin remains enabled. Her Slack channel was unconfigured on the previous image and remains unconfigured; Discord and Telegram are connected. Terry's configured Slack connection passed. Every agent's Asana container was preserved during its accepted cutover.

## Verification

- [Packaged lock tests](test-proof.json): four containers, nested operations, timeout without entry, exception release, parent-crash recovery, interoperability with v1 in both directions, and no persistent holder helper.
- [Acquisition failures](acquisition-failure-proof.json): failed and killed helpers reject the writer before entry.
- [Upgrade gates](gate-proof.json): v2 accepted; v1 and altered acquisition code rejected.
- [Synthetic Wiki workload](wiki-proof.json): three containers completed nine ingest/compile/lint rounds and retained all nine source pages.
- [Mixed-generation live pilot](pilot-live-lint-proof.json) and [final live calls](live-lint-proof.json): three simultaneous gateway lint requests succeeded in each round. All returned 1,093 content warnings; this work did not repair those warnings.
- [Final fleet audit](final-audit.json), individual acceptance receipts, and [image identities](images.json) record the deployed result.

## Recovery

The complete local image archive contains eleven gateway images and two Asana image variants. Its size is 5,746,986,387 bytes; [archive.json](archive.json) records its SHA256 and exact host path. [Cold restore](cold-restore-proof.json) imported it into an initially empty independent Docker/containerd store and verified all thirteen image identities and runtimes. The private restore stores were removed after success. Original images, earlier archives and exact per-agent rollback files remain available.

The [encrypted Wiki overlay](https://drive.google.com/file/d/1GlLkXPMWEyhu60awhZP-UcLiUvQg9GZk/view) is 5,748,828,648 bytes. Cloud size and MD5 matched the local ciphertext. It includes the archive at the exact path referenced by the restored manifests, plus current Compose, post-start, agent configuration, wrapper and manifest files, preserving file/directory ownership and modes. See [offsite proof](offsite-proof.json).

The existing [backup index](https://drive.google.com/file/d/1AxObfW_mSsJrHbTBoqEO6MTxsUngPsKO/view) and key-reference record were updated with version preconditions and checksum read-back; the index now lists fifteen files. This overlay is applied after the prior shared-service overlay. Earlier agent-state/service backups remain required; this is not a new full agent-history or OS snapshot. Encryption uses the existing verified recipient. A fresh decryption roundtrip was not performed for this overlay; plaintext image cold restore and cloud ciphertext checks are separate verified facts.

## Corrections during execution

- BuildKit interpreted a bare image SHA as a repository; the fleet builds use the verified tag plus digest. The missing default Docker bridge was avoided with isolated `none` networking; production networking was not repaired or changed.
- Test harness fixes covered sufficient contention time, vault-relative source paths and the PID column required by `docker top`.
- The cold-restore harness required host PID/cgroup namespaces and umask 022 for its private daemons. Runtime verification resumed from the already imported archive after those harness fixes; the receipt explicitly records this continuation.
- Grogar's first acceptance check saw successful Wiki search but readiness HTTP 503 and rolled back. The corrected check waits for both health and readiness; retry passed.
- Marsha's first acceptance rule incorrectly required an unconfigured Slack channel to run. It rolled back. The original-image [channel baseline](marsha-original-channel-baseline.json) confirmed the existing state; the corrected rule preserves the enabled plugin and checks configured channels. Retry passed.
- A transient SCP timeout was retried. Desktop Git push lacked credentials, so commits were published through the connected GitHub API. Private startup logs and credentials were excluded from repository receipts.

## Operating limits

The maintained package supplies the native locking primitive. The small OpenClaw integration still needs rebuilding and verification on upgrades; this is not an automatic dependency-update service. Protection applies to cooperating Wiki operations on the shared VPS1 filesystem. It does not provide multi-file rollback after interruption, coordinate other servers, or protect editors that bypass the lock. Never remove or replace the stable lock file while writers are active.
