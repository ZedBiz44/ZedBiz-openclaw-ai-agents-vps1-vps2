# VPS1 host maintenance — 2026-10-24

Date:2026-10-24 | Agent:Cody | Status:Host maintenance accepted; one Ubuntu-phased update deferred

## Authority and result

Jack explicitly requested finishing VPS1 server updates and checking whether they help startup. Updated15 currently eligible host packages and completed a real activation reboot. Host acceptance passed at18:29:06UTC. All40 production containers recovered on their original image IDs; eleven managed agent units report Result=success. All eleven gateways and Asana sidecars are healthy, with zero post-boot automatic restarts or OOM flags. No shared memory schema, agent version/model, capability or credential change was part of this batch.

Installed versions: Docker29.9.2, Compose5.6.1, Buildx0.38.1, containerd2.4.2 packaging revision-3, Tailscale1.104.2,1Password CLI2.41.1. GLib2.80.0-6ubuntu3.10, Ubuntu Pro38 and tmux3.4-1ubuntu0.2 also installed. Current kernel6.8.0-147-generic was already current.

Fresh upgrade simulation has zero eligible pending updates and no held packages. cloud-init26.2 remains excluded by Ubuntu's50-percent phased rollout; installed26.1 is retained under normal vendor policy. No phasing override, release upgrade, autoremove or image/volume prune was performed.

## Maintenance sequence and failed gates

The initial41-container count included its own transient Alpine operator. Its exact identity was diagnosed and explicitly excluded;40 managed production containers then matched the baseline.

Saved host configuration and package inventory, downloaded target packages and old recovery packages. Validated Docker live-restore configuration and reloaded it without changing any production container process. However, the installation's strict no-interruption guard FAILED: OpenClaw units Require=docker.service, so systemd gracefully stopped/recreated all eleven gateway/Asana pairs when Docker's package restarted. Eighteen shared-service containers kept their processes through that package step. Cody missed that dependency in preflight and did not independently drain all agent work before this unexpected restart; absence of interrupted business work is not established. Original failure receipt and package log are retained.

Host services still using old binaries were restarted serially without another container restart. The unattended-upgrades shutdown helper briefly failed during that sequence. Remaining old shared-container shim executables had genuinely different hashes; old SSH/op processes also retained obsolete runtime code. A clean activation reboot was used rather than killing unidentified sessions, replacing live shims, suppressing warnings or rewriting systemd dependencies.

Terry had a prolonged plugin-services warm-up. A late pre-reboot RPC returned two root requests before managed stop, so no claim of zero admitted requests is made. Its managed graceful shutdown completed successfully. Refreshed checks found no active work or running schedules on the other ten agents; Terry was deliberately stopped. Recovery gates passed before reboot.

Old boot ID37e402a3-0394-4b7a-8c26-8f08bf74eabf changed to d9a68f32-b15f-4bba-96e7-11c531d3974f. Automatic managed startup recovered the fleet. After reboot, needrestart lists NO outdated services, kernel is current, unattended-upgrades is active and there are no failed systemd units. Docker/containerd/SSH/Tailscale active; Tailscale daemon1.104.2, BackendState=Running, Self.Online=true. No further reboot is required. Live-restore remains enabled, but systemd dependencies still mean a future Docker package restart can stop agents; future host maintenance must explicitly account for that.

## Recovery retained

Private root: /opt/openclaw/backups/host-20261024, owner-only.

- Host config archive/list verified, SHA2569d2c0e877e023eecabe7eb8e2139a6d6f5d1ce82bb712d11432871c18bf3851d. Covers Docker/containerd/APT/systemd/needrestart configuration and package inventory.
- Old Docker/containerd/Compose/Tailscale packages retained with hashes. Old tmux/op packages were unavailable upstream; do not claim exact old package recovery for those two.
- Consistent online backups of40 agent SQLite databases passed quick_check; configuration copies retained.
- PostgreSQL custom dump passed archive-list verification, SHA256baa2aca206fb23c6d34a4ef5370c6fae84c27a165418fd2c7314b779a64ded9a.
- Three Qdrant collection snapshots downloaded and hashed. Production snapshots and copied recovery files retained.
- Existing gateway/sidecar recovery manifests, exact images and protected wrapper hashes verified. This batch did not rebuild or replace them.
- These are per-database online checkpoints, not one simultaneous offline fleet transaction. No state restore was required. Local recovery does not independently protect against VPS-disk loss.

## Live verification and limitations

All111 schedule definitions match pre-reboot copies. All11 public HTTPS /healthz links returned200. Every configured Discord/Telegram/Slack connection reported connected; unconfigured channels were not counted as failures.

Marsha receipt31873417-e72e-4b7e-be29-a684ec3115c2 used the preserved GPT-6 Astra route without rerouting. Her actual Notion fetch, native Asana own-user identity, Hindsight recall and authenticated Google Drive read passed.

Terry's all-tools gate did NOT pass as originally specified. His saved main chat has a user-selected OpenRouter DeepSeek-V4-Pro override, proven in the pre-reboot SQLite checkpoint; default configuration remains GPT-6.1 Sol. Receipt6e58cf11-925e-44cd-b44d-e423218fd027 matched that saved override without rerouting. Actual Mem0 recall and Asana identity passed; independent authenticated Drive read passed. The requested Codex-to-Notion route was blocked by existing supervision settings. The model reported an ntn fallback read, which is not substituted for the requested Codex-route proof. No override, supervision setting or OAuth lane was changed. Any routing repair is a separate user decision.

The first resource-read helper used a private cgroup namespace and could not find host memory counters; rerunning with --cgroupns=host passed. This was an observation-helper failure, not an application failure.

## Startup result

Cold full-fleet reboot wall times from container start to internal ready:
Marsha224.2s, Terry347.5s, Edith318.6s. Other agents ranged146.7–205.1s. Marsha internal ready214.9s; Terry316.9s. Marsha's prior individual start was101.7s wall time. Simultaneous boot, cold filesystem cache and unequal load prevent attributing the difference to the package update.

The updates did NOT demonstrate a startup fix. Plugin preparation remains the expensive phase: post-reboot Marsha93.9s, Terry249.3s. Ready markers also are not proof of sustained response; public health, gateway/channel checks and model receipts were separately collected.

At18:27:17UTC, Marsha working memory2848.8MiB, anonymous2328.7MiB, swap0. Terry2722.6MiB working was sampled during acceptance activity. These are point-in-time samples, not controlled long-idle or leak tests; the roughly2GB goal is not achieved. At18:29 host available memory was about10.1GiB, swap0 and disk free39GiB. Reboot cleared swap, not proof of a permanent RAM repair.

## Records and remaining scope

Private receipts: before.json, plan.json, prepared.json, failure.json, package-upgrade.log, managed-restart-reconciliation.json, applied.json, reboot-checkpoint.json, reboot-intent.json, reboot-verified.json, verified.json, before-reboot/after-reboot fleet RPC copies, final-readback.json, live-model-proof.json, terry-route-check.json, terry-acceptance-readback.json. Technical helper source: docker/host-20261024/ on this branch.

VPS1 host maintenance is complete subject to the normal cloud-init phasing deferral. Nine other VPS1 OpenClaw upgrades, shared application-image upgrades and the startup/RAM investigation remain separate unfinished work. Edith's Mem0 model repair stays deferred; Harry's separately completed repair was untouched. Issue480 and draft PR482 remain open for the broader rollout. SOP remains in Notion.

Upstream references: [Docker29 release notes](https://docs.docker.com/engine/release-notes/29/), [live-restore scope](https://docs.docker.com/engine/daemon/live-restore/), [Ubuntu phased updates](https://documentation.ubuntu.com/server/explanation/software/about-apt-upgrade-and-phased-updates/index.html).
