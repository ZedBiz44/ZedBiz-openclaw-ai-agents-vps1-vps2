# Victor execution references and verified evidence locations

Verified by Cody on October 9, 2026, Mountain Time. This is a technical command/path reference; Notion DSCA and SOPs own authority and operating policy. No new permissions or recurring jobs are created here.

## Daily check on a VPS1 agent

In the selected agent container, the verified installed runner is:

```sh
python3 /home/node/.openclaw/workspace/skills/z-agent-health-report/scripts/run-openclaw-checks.py --mode daily
```

Run in that agent's existing runtime context, one at a time. Do not bypass the guard or launch a second runner when the first is still running. On the approved VPS1 host route, wrap that exact command with `docker exec <agent>` using an agent from the register. A direct local probe consumes resources; inspect saved evidence first. Keep unlimited agent work; positive probe deadlines belong to individual network requests.

Full results: `/home/node/.openclaw/workspace/artifacts/health-checks/*.json` in that same agent. Host workspace mount: `/opt/openclaw/agents/<agent>/workspace`. Active state database: `/home/node/.openclaw/state/openclaw.sqlite`; transcript database: `/home/node/.openclaw/agents/main/agent/openclaw-agent.sqlite`. Do not substitute a HOME-derived database.

[Reviewed runner source](https://github.com/ZedBiz44/z-agent-health-report-Skill/blob/5f79627a3c9c60bed1f26d088e28e23df942dbda/scripts/run-openclaw-checks.py). Source review does not certify every remote deployment; record target hashes when changing a runner.

## Fleet collection in Victor

```sh
python3 /home/node/.openclaw/workspace/skills/z-agent-health-report/scripts/collect-discord-reports.py daily
```

The installed collector accepts daily or weekly (confirmed with --help). Use it inside Victor's existing runtime; it reads via the running gateway. Read its returned artifact locations, preserve the complete JSON and errors, and keep findings in `/home/node/.openclaw/workspace/artifacts/fleet-health/open-findings.json`.

[Collector source under review](https://github.com/ZedBiz44/z-agent-health-report-Skill/blob/fe5ea721da067788ee686484d75161bf5f9b3c41/scripts/collect-discord-reports.py); [PR 7](https://github.com/ZedBiz44/z-agent-health-report-Skill/pull/7) is currently draft/open. Do not redeploy older main as an update. The runner and collector are separate scripts with different purposes.

## Remote evidence from Victor

```sh
python3 /home/node/.openclaw/workspace/scripts/victor-fleet-inspect.py frank
```

Replace frank only with suzy, harry, ruby or rocky. The existing client uses Victor's injected credential and pinned host keys. It submits only `inspect <agent>` to `/usr/local/sbin/zedbiz-fleet-diagnostics` on the target host. It returns service/resource evidence and available saved check artifacts, not a fresh gateway/channel probe. It cannot launch a remote repair or arbitrary shell. An existing saved report is not proof of a new check.

Client existence and host route profiles were rechecked October 9. Five route reads were verified October 8; this documentation pass did not rerun all reads from Victor. Proposed kernel-reader and remote guarded-probe extensions remain separately approval-scoped. Do not confuse Cody's administrative inspection access with Victor's limited route.

## Memory and restart evidence on the approved VPS1 host route

```sh
# Set this to one exact registered container before using the commands.
agent=victor
docker inspect --format '{{.State.StartedAt}} {{.RestartCount}} {{.State.OOMKilled}} {{.HostConfig.Memory}} {{.HostConfig.MemorySwap}}' "$agent"
docker exec "$agent" cat /sys/fs/cgroup/memory.current /sys/fs/cgroup/memory.swap.current /sys/fs/cgroup/memory.stat /sys/fs/cgroup/memory.events
docker top "$agent" -eo pid,ppid,comm,rss
```

These commands inspect without restarting or writing application data. `memory.current` counts the whole container, including gateway, workers, Codex, connectors and charged cache. RSS helps attribution but summed RSS double-counts shared pages. Worker heaps inside the gateway are already included in gateway RSS. Use raw total as the target measure; show cache/working-set and swap separately.

Use `sar -r -f /var/log/sysstat/saDD` and `sar -u -f /var/log/sysstat/saDD` for the incident's existing daily archive (replace DD with the verified day; inspect its header/timezone). Record both Mountain and UTC timestamps. Archive existence and sampling interval constrain conclusions; a ten-minute sample can miss a short spike. Kernel history requires the approved kernel-reader route when available; do not mistake denied access or missing evidence for no OOM event.

Save the timestamped readings and workload description in Victor's private `workspace/artifacts/fleet-health/<incident>/` evidence directory, and link sanitized conclusions in the incident. Record baseline, during-work peak and post-work readings; never terminate work to meet a measurement interval.

## Monitoring identities and gaps

The separate model monitor has VPS1:<agent> keys for the eleven local agents and VPS2:<agent> for Harry, Suzy and Frank. Source/rollback: [PR 447](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/447). Host scripts are `/home/jackadmin/model-alerts/monitor.py` and `/opt/zedbiz-model-alerts/monitor.py`. State is adjacent `config.state.json`; sanitized events are in journal tag `zedbiz-model-alerts`. Do not publish config.json (credentials).

Uptime Kuma container `uptime-kuma` mounts `/opt/uptime-kuma/data` at `/app/data`. Its db-config.json selects SQLite. Read-only SELECT of id,name,active,type from monitor returned zero rows in kuma.db. There are no monitor IDs to map in this instance. A running Kuma container is not reachability coverage. Owner Victor must propose required endpoint checks and delivery verification; installing/enabling new checks requires applicable approval. No alert delivery or restore drill was performed here.

[Current maintained register](fleet-register-latest.json); [October 9 evidence snapshot](fleet-register-20261009.json). Update the stable register in reviewed changes and preserve dated evidence. Zero Docker memory limits mean no Docker limit configured, not zero usable memory. Systemd MemorySwapMax=infinity is a separate swap setting, not a Docker combined ceiling; parent/host constraints still apply.

## Working-link maintenance

PR 448 must be reviewed and merged before changing Notion working links to main. Until then, label the reviewed commit links as pending merge and include the verification date. After merge, use main/execution-reference.md and main/fleet-register-latest.json under this directory for daily use; keep commit-pinned links and dated registers in incident evidence. When changing an execution reference, verify its deployed target and refresh the Notion review date rather than treating source merge as deployment.
