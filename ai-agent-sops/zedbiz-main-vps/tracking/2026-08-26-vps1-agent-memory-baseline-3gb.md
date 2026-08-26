# VPS1 Agent Memory Baseline Increased to 3 GB

Date: 2026-08-26 | Agent: Cody | Status: Complete

## Summary

- **Date:** 2026-08-26 Mountain Time
- **Changed By:** Cody
- **VPS:** main-vps
- **Affected Agents:** Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma
- **Status:** Done and live-verified

## Change Reason

- Z-Research assignments sometimes completed their tool work but returned no final response.
- Kernel evidence showed Docker OOM kills during research work for Inga, Terry, and Vivian.
- The old Docker setting allowed 2 GiB RAM and only 512 MiB additional swap because `memswap_limit: 2560m` is the combined RAM-plus-swap ceiling, not 2.5 GiB of swap.

## Capacity Decision

- Gateway RAM ceiling: `mem_limit: 3g`.
- Combined RAM-plus-swap ceiling: `memswap_limit: 4g`.
- Each agent can therefore use one full additional GiB of swap after reaching its 3 GiB RAM ceiling.
- These are per-container ceilings, not reserved memory. VPS1 has 15 GiB RAM and 4 GiB shared host swap, so concurrent fleet-wide spikes still require monitoring.
- Asana sidecar limits remain unchanged at 384 MiB RAM and 64 processes.

## Change Details

- VPS path: `/opt/openclaw/agents/{agent}/docker-compose.yml`
- GitHub script: `ai-agent-sops/shared-scripts/set-vps1-agent-memory-baseline.sh`
- Every Compose file received a timestamped `docker-compose.yml.bak-memory-*` rollback copy.
- Inga was the pilot because she had produced both successful and silent Z-Research outcomes.
- The other ten agents were recreated only after Inga reached gateway-ready with zero restarts and zero OOM state.
- Agent recreation used each agent's own `.op.token` with `op run --env-file .env` so private-vault credentials remained isolated.
- Wilma's live vault currently lacks a referenced WordPress MCP item. Her protected August 24 `.env.resolved` file was used as the controlled fallback; the missing LightningWP key remains unavailable and requires separate follow-up.

## Verification

- All 11 gateways reported `running`, zero restarts, and `OOMKilled=false`.
- All 11 gateways reported exactly 3,221,225,472 bytes RAM and 4,294,967,296 bytes combined RAM plus swap.
- All 11 gateways reached `[gateway] ready` and started at least one communication provider.
- No new kernel OOM event occurred after the rollout began.
- Host state after rollout: 7.2 GiB RAM available and 3.2 GiB swap free.
- Live gateway use ranged from approximately 377 MiB to 891 MiB immediately after startup.

## Rollback Note

- Restore the newest pre-change `docker-compose.yml.bak-memory-*` file for the affected agent.
- Recreate the agent through its private 1Password-aware route: `op-start-{agent}.sh` or the tracked rollout script.
- Verify gateway-ready, channels, live Docker limits, restart count, and OOM state after rollback.

## Links

- GitHub Issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/184
- Notion Journal: https://app.notion.com/p/3c8a3e33d58181f396f1c3cbaa0b2384
