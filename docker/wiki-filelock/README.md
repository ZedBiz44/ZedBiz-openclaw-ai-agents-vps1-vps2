# Shared Wiki locking through Python filelock

This replaces the hand-written flock holder with the unmodified official Python `filelock` 4.2.1 package. The Node writer holds the descriptor for the whole Wiki mutation; Python only acquires its native Linux lock and exits. Killing a separate holder can no longer release protection while Node keeps writing.

## Integration

- All writers use the existing stable `.openclaw-wiki/zedbiz-mutation.flock` inode on the shared VPS1 filesystem. Never remove or replace it while writers exist.
- The existing OpenClaw in-process queue, nested mutation handling, and full lint transaction wrapper remain in place. A generic library cannot decide which Wiki operations form a transaction.
- `filelock.lock_descriptor` locks inherited descriptor 3. It must not explicitly unlock it; closing Python's duplicate leaves Node's descriptor locked. Closing Node's descriptor or killing Node releases it.
- Acquisition fails closed on missing Python/package, timeout, bad path or helper failure. No persistent Python holder remains after acquisition. The default wait is 300 seconds.
- Old Linux flock and new filelock writers coordinate on the same inode during rollout and rollback. OpenClaw's PID-based file-lock helper is not substituted: separate Docker PID namespaces invalidate its stale-owner assumptions.

## Package and build

Run `fetch-wheel.py` to fetch the pinned official wheel, then build this Dockerfile with `BASE_IMAGE` set to the verified current agent image and digest. The build runs offline, verifies SHA256, and retains the package's license and metadata in `vendor`. It does not install into the system Python environment or upgrade other dependencies.

Wheel SHA256: `7be2662e9e826b9bba28afc0f843a123280d799a2ea44bb5d35ccec67905ae44`.

`patch.py` accepts only the known v1 Wiki transaction integration and changes its version marker. Unknown upstream layouts fail the build. `verify.py` checks the package, transaction boundaries and installed helper/package hashes. The persisted post-start guard independently requires the v2 version before invoking that verifier, so an older image cannot pass using its older verifier.

## Verification and recovery

Host-side tests use independent containers and synthetic data: concurrent/nested writers, timeout without entry, exception and parent-crash release, old/new interoperability, absence of a persistent holder, actual Wiki ingest/compile/lint, and rejected old/tampered images. `test-worker.mjs` and `wiki-worker.mjs` intentionally bind to the tested 2026.10.6 bundle exports; reassess on OpenClaw upgrades.

`build-fleet.py` preserves each current image's layers and runtime configuration. `prepare-recovery.py` exports all gateway and Asana images before cutover. `cold-restore.py` imports that archive into an empty independent Docker/containerd store and runs each restored image. `deploy.py` checks for drift and active work, saves rollback files, replaces one gateway, then verifies readiness, authenticated Wiki search, channels and preservation of configuration/Asana. Failure restores that agent's previous files/image and stops the rollout.

This is a maintained locking primitive with a small OpenClaw integration. It does not automatically stay compatible with future OpenClaw releases; upgrades must rebuild and pass the gate/tests. It does not provide atomic rollback of interrupted multi-file writes, coordinate other hosts, or protect editors that bypass the shared lock.
