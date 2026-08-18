# VPS1 Agent PID Limit Increased To 2048

Date: 2026-08-18 | Agent: Cody | Status: Complete

## Purpose

- Remove the undersized 160-task container ceiling that prevented an agent from starting recovery commands after Chromium subprocess accumulation.
- Give all 11 main VPS1 agents enough headroom for browser, research, and multi-tool work without removing the server's safety guardrails.

## Capacity Decision

- Main agent limit: `pids_limit: 2048`.
- Main-agent theoretical maximum: 22,528 tasks across 11 containers.
- Sidecar limits remain unchanged at 64 tasks each.
- VPS1 kernel `threads-max` was 127,631, so the main-agent ceilings total about 18% of the host thread ceiling.
- The 2 GB memory and 2.5 GB memory-plus-swap limits remain in place and continue to prevent one agent from consuming the host.

## Pilot

- Pilot agent: Wilma.
- Backed up Wilma's live Compose file before changing it.
- Recreated Wilma at `pids_limit: 2048` using the agent's 1Password-aware startup path.
- The pilot exposed an operational restart trap: a bare `docker compose` command passes unresolved `op://` references. The correct route is `op run --env-file .env -- docker compose ...` or the agent's `op-start-{agent}.sh` wrapper.
- The older `/opt/openclaw/scripts/resolve-secrets.sh` route is not the live startup path and its stored Connect token returned HTTP 401. No fleet restart used that broken route.
- Wilma completed 16 consecutive Chromium screenshots with zero PID-limit events and returned to normal process levels afterward.

## Fleet Rollout

- Applied `pids_limit: 2048` to Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma.
- Recreated each main agent sequentially through `op run --env-file .env` and stopped for a health and channel check after every agent.
- Every live Compose file receives a timestamped rollback copy.
- Asana helper containers retain their existing 64-task limits.
- Final verification: all 11 main agents healthy with zero restarts and zero PID-limit events; all 11 Asana helper containers healthy at 64 tasks.
- Host verification after rollout: 1,876 active threads, 6.6 GB memory available, 3.5 GB swap free, and zero unhealthy containers.

## Rollback

- Restore each timestamped `docker-compose.yml.pre-pids2048-*` copy.
- Recreate the affected agent through its 1Password-aware startup wrapper.
