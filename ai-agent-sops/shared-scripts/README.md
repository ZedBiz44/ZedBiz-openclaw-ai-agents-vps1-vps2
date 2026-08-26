# Shared Scripts

Reusable scripts and command snippets used across ZedBiz AI agent servers.

## Rule

Every script needs:

- Purpose
- Owner or agent that added it
- Date added
- Where it has been tested
- Rollback or removal note

## VPS1 Memory Baseline

- `set-vps1-agent-memory-baseline.sh` sets the 11 OpenClaw gateways to 3 GiB RAM plus 1 GiB swap headroom.
- It backs up each live Compose file, recreates through the agent's private 1Password service token, verifies the live Docker limits, and rolls back on verification failure.
- If live 1Password resolution fails, it uses an existing protected `.env.resolved` file only when that file contains no unresolved `op://` references.

