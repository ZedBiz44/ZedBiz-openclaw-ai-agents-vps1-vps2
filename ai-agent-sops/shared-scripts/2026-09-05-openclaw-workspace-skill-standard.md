# OpenClaw Workspace Skill Standard

Date: 2026-09-05 | Agent: Cody | Status: Implemented

## Decision

All ZedBiz custom skills for isolated OpenClaw agents belong in the active agent workspace's `skills` directory.

- VPS1 host: `/opt/openclaw/agents/<agent>/workspace/skills`
- VPS1 container: `/home/node/.openclaw/workspace/skills`
- VPS2: `/root/.openclaw-<agent>/workspace/skills`
- Rocky/VPS4: `/home/openclaw/.openclaw/workspace/skills`

Do not retain ZedBiz custom skill packages in managed/global, nested, backup, retired, archive, old, or rollback paths. GitHub is the recovery source.

## Why

OpenClaw's default `openclaw skills install` command targets `<workspace>/skills`. The `--global` option targets `<state-dir>/skills` for agents that actually share one state. ZedBiz agents on VPS1, VPS2, and VPS4 have isolated workspaces and runtime state, so using the global root adds a second inspection location without useful sharing.

## Required Deployment Behaviour

- Deploy one copy to the active workspace `skills` directory.
- Remove the same skill name from managed/global and legacy nested roots.
- Do not create a server-side skill backup.
- Restart or begin a fresh session after changes.
- Verify the skill is eligible, model-visible, and reported as `openclaw-workspace`.
- Verify no custom `SKILL.md` remains in server backup or retired trees.

## Source

- OpenClaw Skills: https://docs.openclaw.ai/tools/skills
- OpenClaw CLI Skills: https://docs.openclaw.ai/cli/skills
- OpenClaw Agent Workspace: https://docs.openclaw.ai/agent-workspace
