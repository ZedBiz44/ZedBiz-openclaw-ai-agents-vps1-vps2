# Shared Wiki lock implementation

Added by Cody, 2026-10-23, for the eleven VPS1 OpenClaw containers sharing `/opt/openclaw/shared/knowledge/wiki`. Tracking: [issue 476](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/476).

## Code boundary

OpenClaw 2026.10.4 serializes Wiki mutations inside one process. This image layer extends that coordinator across containers using Linux `flock` on a stable file in the shared Wiki. It preserves the original canonical path, queue and reentrant transaction handling. The full lint operation is also covered because its final report write occurs after its internal compile completes.

The helper owns the file descriptor until the Node parent closes its pipe. Parent exit and container exit release it without inspecting process IDs in other containers. Acquisition waits at most 300 seconds and then fails. Never delete or replace the lock file while any writer might be running.

This is a compatibility patch for the audited 2026.10.4 bundle, not an OpenClaw upgrade. It covers cooperating processes on one Linux host and shared filesystem. External editors, file synchronization and another server do not participate.

## Build and upgrade gate

Build from each agent's existing customized image:

```sh
docker build --build-arg BASE_IMAGE=EXISTING_IMAGE -t NEW_IMAGE docker/wiki-lock
```

`patch.py` rejects an unknown coordinator shape. `verify.py` runs during the image build and through each agent's persistent `post-start.sh`. A replacement image without the patch stops with an actionable error. Upgrades therefore require rebuilding and retesting this layer, or deliberately replacing it with a proven compatible upstream solution.

The image preserves the base entrypoint and command and returns to user `node`. It requires the existing Python 3 runtime. No provider, model, credential or Wiki search settings are changed.

## Deployment and recovery implementation

The dated installation is `/opt/openclaw/recovery/wiki-lock-20261023`. `images.json` records original and replacement image references. `archive.json` records the SHA-256 and path of the compressed Docker image recovery archive. Existing host startup manifests receive the new image ID and archive reference, retaining their existing credential wrapper and integrity checks.

`deploy.py AGENT stage` saves exact Compose, post-start and recovery-manifest backups before editing. `activate` drains/stops the old container and invokes its existing secret-aware startup wrapper. `rollback` restores those three backups and recreates the original image. Old images and recovery archives are retained. Wrapper output is captured rather than printed because credential-resolution failures can include secrets.

## Verification tools

- `probe.mjs`: actual bundled coordinator; nested calls, shared counter, exception release and holder termination.
- `wiki-probe.mjs`: actual ingest, compile and lint on a separate Wiki copy, with an independent compiled cache per process. Never use this fixture against the production Wiki.
- `check-live.py AGENT`: installed guard, live default Wiki search, readiness and Discord state without printing credentials.

The dated technical record contains the observed test results and rollout status.
