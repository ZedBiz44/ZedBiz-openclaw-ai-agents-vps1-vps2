# 2026-07-17 - VPS Change - OOM Safeguards

Date: 2026-07-17 | Agent: Cody | Status: Final

## Summary

- **Date:** 2026-07-17 Mountain Time
- **Changed By:** Cody
- **VPS:** main-vps, hostname `srv1404026`
- **Affected Agent:** Marsha, Hindsight, and all VPS1 OpenClaw agents
- **Status:** done and live-verified

## Change Reason

- Marsha's twelve simultaneous Notion connector calls created twelve `openclaw-hooks` workers and triggered a server-wide out-of-memory cascade.
- VPS1 had no swap and no container memory, swap, or process limits.

## Change Details

- Created a 4 GB `/swapfile`, persisted it in `/etc/fstab`, and set `vm.swappiness=10` through `/etc/sysctl.d/99-zedbiz-swap.conf`.
- Confirmed Docker log rotation already existed at `10m` with three files on the agents and Hindsight; no replacement was needed.
- Set Hindsight to 3 GB RAM and 3.5 GB combined RAM-plus-swap.
- Added a permanent Marsha rule limiting Notion and other connector-heavy work to batches of two calls.
- The original 1 GB Marsha test limit caused a contained memory-cgroup restart during a six-page Notion test. VPS1 and every other service remained up.
- Raised the tested agent standard to 2 GB RAM, 2.5 GB combined RAM-plus-swap, and 160 PIDs.
- Applied the tested limits to Amanda, Edith, GohZed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma.
- Backups are stored at `/opt/openclaw/backups/20260717T173144MDT-vps1-oom-safeguards`.

## Files Changed

- `/etc/fstab`
- `/etc/sysctl.d/99-zedbiz-swap.conf`
- `/opt/openclaw/agents/{agent}/docker-compose.yml` for all eleven VPS1 OpenClaw agents
- `/opt/openclaw/agents/marsha/workspace/AGENTS.md`
- `ai-agent-sops/zedbiz-main-vps/README.md`
- This tracking record

## Services Restarted

- All eleven VPS1 OpenClaw agent containers were recreated sequentially.
- Each agent was restarted through its `op-start-{agent}.sh` wrapper so 1Password secrets were injected.
- Hindsight was updated in place and did not restart.

## Verification

- A successful read-only Marsha test searched Notion and fetched six pages in batches of at most two.
- The successful run made ten tool calls with zero failures, peaked near 1.7 GB, completed without an OOM event, and left zero `openclaw-hooks` workers.
- Hindsight completed a real `zedbiz-shared` consolidation of 57 pending memories in 109 seconds under the 3 GB cap.
- Hindsight returned to zero active slots and zero pending tasks; its database health endpoint returned healthy.
- Every agent passed its internal health endpoint.
- All configured Discord, Telegram, and Slack channel probes passed after restart through the 1Password wrappers.
- Final VPS1 state: about 8.8 GB available RAM, 4 GB swap with about 1 MB used, no new kernel OOM events, and zero hook workers.

## Failed Attempt And Correction

- A direct `docker compose up -d` recreation preserved the resource limits but bypassed 1Password injection, causing 401 responses on agent Discord probes.
- Re-running each agent through `op-start-{agent}.sh up` restored the correct credentials. All channel probes then passed.
- Durable rule: never recreate a VPS1 agent with bare Compose when its startup wrapper is available.

## Rollback Note

- Restore the relevant files from `/opt/openclaw/backups/20260717T173144MDT-vps1-oom-safeguards`.
- Recreate an agent only through its `op-start-{agent}.sh up` wrapper.
- Hindsight limits can be reverted with `docker update` after reviewing the recorded previous value of unlimited.
- Swap can be disabled only after removing its `/etc/fstab` entry, running `swapoff /swapfile`, and confirming sufficient free RAM. Do not remove swap during memory pressure.

## Links

- GitHub Issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/68
- Notion page: https://app.notion.com/p/3a0a3e33d581813581cad987f9a7f660
