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

## What Caused The Duplicate Roots

- Earlier ZedBiz deployment scripts deliberately copied skills into more than one discovery root during migrations.
- The scripts also created timestamped server backup trees containing complete skill packages.
- The 2026-09-02 VPS1 cleanup chose the managed/global root as canonical before the OpenClaw install default was checked closely enough.
- That decision was wrong for this fleet. OpenClaw's documented default and the live VPS2 and Rocky configurations all point to the agent workspace.
- The same-session VPS1 managed-root move was reversed after the documentation and all three live server layouts were compared.

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

## Live Implementation And Verification

- VPS1: moved all custom skills for Amanda, Edith, GohZed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma into each agent's workspace. Restarted every container one at a time. All eleven returned healthy, reported zero `openclaw-managed` skills, and loaded the repaired `website-screenshots` skill from `openclaw-workspace`.
- VPS2: moved unique inactive-root packages for Harry, Suzy, and Frank into their workspaces, removed same-name inactive copies, and removed 50 stored backup manifests. Restarted all three systemd services one at a time. All three returned active with zero managed, nested, or backup skill manifests and a visible workspace `website-screenshots` skill.
- Rocky/VPS4: left all 14 active workspace skills in place, removed nine stored backup skill packages, and verified the live gateway with zero managed or backup skill manifests.
- No replacement server-side backup was made. GitHub remains the recovery source.

## Configuration Impact

No `AGENTS.md`, YAML, JSON, cron, or service path change was required. Each runtime already had the correct workspace configured. Only skill files, deployment scripts, and documentation changed.
