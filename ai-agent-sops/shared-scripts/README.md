# Shared Scripts

Reusable scripts and command snippets used across ZedBiz AI agent servers.

## Rule

Every script needs:

- Purpose
- Owner or agent that added it
- Date added
- Where it has been tested
- Rollback or removal note

## Server Skill Storage

- GitHub is the rollback and recovery source for every custom skill.
- Never create server-side backup, retired, old, archive, or timestamped copies of a skill package.
- Keep one active copy of each custom skill in the agent's OpenClaw workspace `skills` directory.
- VPS1 uses `/opt/openclaw/agents/<agent>/workspace/skills` on the host and `/home/node/.openclaw/workspace/skills` in the container.
- VPS2 uses `/root/.openclaw-<agent>/workspace/skills`.
- Rocky on VPS4 uses `/home/openclaw/.openclaw/workspace/skills`.
- Do not deploy ZedBiz custom skills to `<state-dir>/skills` or another managed/global root. The ZedBiz OpenClaw runtimes are isolated per agent, so the global location adds no useful sharing and creates a second place to inspect.
- Replace a skill through a temporary same-filesystem staging directory, move it into the canonical path, and remove the temporary directory in the same operation.
- After deployment, verify that the workspace copy is eligible and model-visible, no custom skills remain in managed/global roots, and no `SKILL.md` files remain under agent backup or retired trees.

## VPS1 Memory Baseline

- `set-vps1-agent-memory-baseline.sh` sets the 11 OpenClaw gateways to 3 GiB RAM plus 1 GiB swap headroom.
- It backs up each live Compose file, recreates through the agent's private 1Password service token, verifies the live Docker limits, and rolls back on verification failure.
- If live 1Password resolution fails, it uses an existing protected `.env.resolved` file only when that file contains no unresolved `op://` references.

