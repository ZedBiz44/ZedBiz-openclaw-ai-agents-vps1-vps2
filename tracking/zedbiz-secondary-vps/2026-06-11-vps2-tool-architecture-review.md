# 2026-06-11 | Cody | VPS2 Tool Architecture Review

Date: 2026-06-11 Mountain Time
Agent: Cody
Status: Diagnose - live review completed; action pending confirmation

## Summary

Reviewed the VPS2 folder-based systemd tool question after a prior thread reported that VPS2 was missing the VPS1 custom tool bundle. Checked the live VPS2 server and relevant Notion documentation.

## Sources Checked

- Notion Technical Documentation page and Tech Updates database
- VPS2 Maintenance SOP
- Agent-Creation-VPS2-SOP
- OpenClaw Tools page
- VPS1 OpenClaw Update Procedure
- Harry VPS rebuild note
- VPS2 OOM incident note
- June 10 Edith/Frank migration note
- Live VPS2 host at 2.24.104.80

## Live VPS2 Findings

- Hostname: srv1677638
- Timezone: Mountain Time / America Edmonton
- Active systemd agents: openclaw-harry, openclaw-suzy, openclaw-frank
- Runtime model: folder-based systemd, not Docker
- OpenClaw version: 2026.5.28 on Harry, Suzy, and Frank
- Node/npm: Node v24.15.0, npm 11.12.1
- Resource state: 48 GB disk, about 29 GB free; 4 GB swap active
- Service user: root for all three agents
- Startup scripts: use op run with per-agent env files

## Tool Inventory

Only ffprobe was found on the host PATH from the VPS1-style external CLI tool bundle.

Missing tools:

- yt-dlp
- rclone
- gh
- yq
- pandoc
- uv / uvx
- gron
- glow
- eza
- duf
- fzf
- freeze
- vhs
- git-cliff
- just
- grex

## Recommendation

Do not migrate VPS2 to Docker for this issue. VPS2 is intentionally documented as a folder-based systemd Hostinger setup, and the current services match that design.

Recommended fix is a managed host-level shared toolbox:

- Install the external CLI tools once on the VPS2 host under /usr/local/bin.
- Keep the install/update script tracked in GitHub as the source of truth.
- Make the script idempotent so rerunning it updates tools without manual cleanup.
- Verify from the host first, then test through one agent, then confirm all active VPS2 agents can see the tools.

## Action Status

No server changes were made during this review. Next step should be a confirmed Get-er-Done pass to add the VPS2 host tool installer, run it, and verify one agent before checking the rest.

## Notion Record

Tech Updates page created: 2026-06-11 | Cody | VPS2 Tool Architecture Review
