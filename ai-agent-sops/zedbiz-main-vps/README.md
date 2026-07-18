# ZedBiz Main VPS

This folder tracks work on the main VPS server where the current Docker-based OpenClaw system is still being tested.

## Track Here

- Docker changes
- OpenClaw agent setup and fixes
- Caddy/domain routing
- permissions and ownership fixes
- cron jobs and scheduled work
- folder structure decisions
- agent-specific configuration changes
- skill additions to agents on the main VPS

## Required Log Rule

Every meaningful change should create or update one tracking entry in `tracking/`.

## VPS1 Agent Restart And Resource Standard

- Restart or recreate an agent through `/opt/openclaw/agents/{agent}/op-start-{agent}.sh up`. Do not run a bare `docker compose up -d` for an agent because it bypasses 1Password secret injection and can leave live channels unauthorized.
- VPS1 OpenClaw agent containers use `mem_limit: 2g`, `memswap_limit: 2560m`, and `pids_limit: 160` unless a tested agent-specific exception is documented.
- Hindsight uses a 3 GB memory limit and 3.5 GB combined memory-plus-swap limit.
- VPS1 has a 4 GB `/swapfile` with `vm.swappiness=10` as an emergency buffer. Swap is not a substitute for container limits.
- Test changes on one agent, verify the internal health endpoint and every configured live channel, then roll out sequentially.

