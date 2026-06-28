# Z-Knowledge Skills Rollout

Date: 2026-06-28 | Agent: Cody | Status: Completed

## Summary
Rolled out the Z-Knowledge skill set to the live OpenClaw agent workspaces so agents can route ZedBiz knowledge, write source-backed wiki research, publish to the correct Notion Core Master Databases, and use the new Z-Connections linking rules.

## Skills Deployed
- `zedbiz-knowledge-routing`
- `zedbiz-wiki-research`
- `zedbiz-notion-knowledge-publishing`

The deployed `zedbiz-notion-knowledge-publishing` skill includes `references/z-connections-linking-rules.md` with the live Z-Connections database reference:

- Z-Connections page: https://app.notion.com/p/c3d932bbd6fa49e898d7b771f77dcd9c
- Z-Connections data source: `collection://3436501a-7bd4-4b74-8b6c-8dc490038865`

## Main VPS Rollout
Installed into `/opt/openclaw/agents/{agent}/workspace/skills` for:

- Amanda
- Edith
- Gohzed
- Grogar
- Inga
- Maggie
- Marsha
- Terry
- Victor
- Vivian
- Wilma
- Zara

## Main VPS Verification
- Verified all listed agent workspace folders contain the three ZedBiz skills.
- Verified all running containers expose the three skills through `openclaw skills list`:
  - Amanda
  - Edith
  - Gohzed
  - Grogar
  - Inga
  - Maggie
  - Marsha
  - Terry
  - Victor
  - Vivian
  - Wilma
- Zara has the files installed but did not have a running container during verification.

## VPS2 Rollout
Installed into `/root/.openclaw-{agent}/workspace/skills` for:

- Harry
- Frank
- Suzy

## VPS2 Verification
- Verified Harry, Frank, and Suzy workspace folders contain the three ZedBiz skills.
- Verified each agent's OpenClaw CLI sees all three ZedBiz skills with `openclaw skills list`.

## Notes
- Terry was used as the first test lane before the main-fleet rollout.
- VPS2 uses a systemd/root-state layout rather than the main VPS Docker workspace layout.
- VPS3/Hermes did not show an OpenClaw agent workspace layout in the local notes checked during this rollout.
