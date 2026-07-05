# 2026-06-11 - Disable Obsidian Vault Maintainer Across VPS1 and VPS2

## Summary

- Disabled `obsidian-vault-maintainer` so agents do not get routed into Obsidian-specific wiki maintenance work.
- VPS1 patched agent containers: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma.
- VPS2 patched agent configs: Harry, Suzy, Frank, and Edith.

## VPS1 Change

- Applied OpenClaw config patch inside each running agent container:
  - `skills.entries.obsidian-vault-maintainer.enabled=false`
- Restarted the VPS1 agent containers to apply the gateway config.
- Final verification showed all checked VPS1 agent containers healthy.
- Final skill verification showed `obsidian-vault-maintainer` as `eligible=false` and `disabled=true` for all checked VPS1 agents.

## VPS2 Change

- Patched the per-agent config files:
  - `/root/.openclaw-harry/openclaw.json`
  - `/root/.openclaw-suzy/openclaw.json`
  - `/root/.openclaw-frank/openclaw.json`
  - `/root/.openclaw-edith/openclaw.json`
- Backups were created beside each config before patching.
- Restarted active VPS2 services: Harry, Suzy, and Frank.
- Edith was patched but left inactive because its service was disabled and it conflicts with Frank on port `4300` when started.

## Final Status

- VPS1: all checked agent containers healthy.
- VPS2: Harry active, Suzy active, Frank active, Edith inactive.
- Notion journal entry created: `2026-06-11 | Cody | Disable Obsidian Vault Maintainer Across VPS Agents`.
