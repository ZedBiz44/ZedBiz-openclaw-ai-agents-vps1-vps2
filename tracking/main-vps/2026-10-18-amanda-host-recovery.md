# Amanda host startup and image recovery repair

Date: 2026-10-18 MDT. Operator: Cody. Approved by Jack: "get er done".
Workstream: [issue 467](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/467).
Source: [draft PR 469](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/469), stacked on Amanda PR 464.

## Problem and implemented change

Amanda's recovered gateway was healthy, but `openclaw-amanda.service` remained
failed after its earlier missing-image boot failure. The existing unit runs a
oneshot startup wrapper and keeps its successful state with RemainAfterExit.

- Installed `/etc/systemd/system/openclaw-amanda.service.d/recovery.conf`.
- Its ExecStart calls `/usr/bin/python3 /opt/openclaw/recovery/amanda-20261018/amanda-host-start.py`.
- The helper verifies the protected wrapper hash and exact declared gateway/Asana
  image IDs, restores missing images from a checksum-verified archive, then invokes
  the original `op-start-amanda.sh up` at most three times with 30-second pauses.
- Unexpected image/Compose/wrapper changes or a corrupt archive fail before startup.
  A timed-out command is not automatically retried because its result is uncertain.
- Added Wants=network-online.target. The existing Docker dependency remains.
- Outer startup limit is 1,500 seconds, covering the 600-second archive-load limit,
  three 180-second startup attempts, pauses and verification overhead.
- Docker still owns runtime crash restarts. The host unit retains Restart=no;
  bounded startup retries are inside the helper, not a second continuous supervisor.
- ExecStop, the protected wrapper, restart-dashboard source and global image-prune
  schedule were not changed. Victor and other agents were not restarted.

Driver SHA256: `cbd22b14557638bf194cd139b940b6635a88f1944e64eed5fa2533edef61b58c`.
Archive, manifest and driver are root-owned in a mode-0700 directory.
Original unit, wrapper, Compose and configuration are saved under
`/opt/openclaw/recovery/amanda-20261018/before-service-repair`, with private file modes.

## Recovery artifacts and isolated proof

Image archive: `/opt/openclaw/recovery/amanda-20261018/images.tar`, 3,999,963,648 bytes.
SHA256: `c7dd367611b80fc2d57f4183d6007b79ee24bc50152d44e35043e408832c1eb9`.

The archive contains:

- Current gateway `zedbiz/openclaw-amanda:2026.10.4-pilot-20261017`, ID `4e5f5b8536785b8307d44e4e5ec1d83449976e149c5cd18e515880ec7336665a`.
- Custom Asana `zedbiz/asana-http-mcp:2.0.0-amanda-recovery-20261017`, ID `8d0560464a3b4f0f5dcc8de88f2549934582aa649aadcc2ccfc403ad19905b94`.
- Historical gateway `zedbiz/openclaw-amanda:2026.9.8-recovery-20261017`, ID `8a8089473585b40067eb617981fcc627b72f681eb6ee684be4fddde2627a2bf6`.

The 9.8 image is NOT an automatic fallback. It requires the corresponding
pre-migration state documented in the October 17 recovery record.

Eight behavioral tests passed: existing images, missing-image restore, corrupt
archive, changed image, changed wrapper, successful retry, exhausted retries and
uncertain timeout without retry.

Cold recovery used the actual helper against an empty Docker 29.8.2 daemon with
its own containerd process, socket, namespaces and disk storage. All three image
IDs matched; restored OpenClaw returned `2026.10.4 (383c124)`. Recovery took 175.6
seconds. Production images and agent state were not removed or mounted into the
test executable. Receipt: `restore-proof.json` beside the archive.

Earlier test setups were corrected: VFS was too slow; legacy overlay2 returned
image-config IDs rather than production containerd's manifest/index IDs, so the
strict identity check rejected it. The successful proof matches production's
overlayfs/containerd store. The first diagnostic daemon also shared the default
containerd event namespace; it was stopped and isolated before archive loading.
No kernel OOM event was found during the diagnostic period.

## Live service proof

At 01:17 MDT, zero active work was confirmed and actual service activation passed:
`active (exited)`, `Result=success`. It did not recreate the existing container.
No reset-failed-only shortcut was used.

The subsequent controlled service stop/start removed the old container and created
`b2773b48344c45331b91491248ee50e913e89a20f3b870e892e9b571645f70f8`, replacing
`cbd38aa2c07ec903103c9c8c575e78096b3df5d42dfe4a7d42515e2e9d26d558`.
Victor's container identity was unchanged. The startup command completed in 8.3 seconds.

Both Amanda core and main-agent databases passed offline SQLite quick_check.
Her agent directory and external LanceDB store were archived while stopped;
`.op.token` and `.env.resolved` were excluded. Archive listing and SHA256 passed.
Archive: `/opt/openclaw/recovery/amanda-20261018/amanda-offline-state-before-cycle.tar`.
SHA256: `eb33dbef8052759362d8227decb0140d70a673197629961938571f20e8a49310`.

Pre-cycle actual model receipt `ce375a66-21ed-4251-95a7-d57aaf387496` verified
GPT-6.1 Sol without rerouting, Amanda Asana identity, Notion page access and a
September 27 saved role/workflow fact through memory_recall.
Post-cycle receipt `d2f3f5a9-036e-4b12-8ff2-270418034277` passed on GPT-6.1 Sol
without rerouting. Actual successful tools were `memory_recall`,
`asana.asana_get_user` and `codex_apps.notion.fetch`. Amanda returned the same
September 27 role record, Asana identity `1213974002925107`, and Notion title
`Agent Restart Dashboard`.

Final acceptance passed: gateway and Asana containers healthy, public health HTTP
200, Discord and Telegram running/connected with no lastError, all 10 schedule
definitions unchanged, and the host service enabled/active-exited/Result=success.
Both recreated containers had zero automatic restarts and OOMKilled=false.
Early HTTP/RPC attempts occurred during normal startup before readiness; Docker's
existing three-minute health interval delayed its healthy label after HTTP recovered.

Wrapper, Compose, OpenClaw configuration and original unit bytes match their
pre-change backups. Only the new override and recovery files implement this change.
Temporary Docker/containerd proof processes and all three test-storage directories
were removed. The archives and receipts remain protected. Final sampled memory was
1.916 GiB gateway plus 62.86 MiB sidecar, not a sustained memory benchmark; disk had
153 GiB free. Protected RPC/model receipts are under
`/home/jackadmin/amanda-host-recovery-20261018`.

## Maintenance and rollback boundary

Future Amanda image or protected-wrapper changes must refresh the approved archive
and manifest as part of that release, then rerun recovery verification. This
helper intentionally refuses unreviewed image identities. Do not leave a new
Compose image paired with an old recovery manifest.

For this service repair's rollback, remove only `recovery.conf`, reload systemd,
and use the existing protected wrapper to recover the current approved images.
Retain recovery archives and current agent data. Do not restore historical state
or overwrite newer unrelated settings merely to undo the service override.

This is a service-lifecycle and image-recovery proof, not a whole-host reboot test,
an off-host disaster-recovery proof, or fleet rollout approval. Local archives
survive Docker pruning but not loss of the VPS disk. No clean source rebuild was
performed in this task; the recovery path uses verified saved images and retains
the build sources from the previous release.

