# Terry Memory Wiki Status Fix

Date: 2026-07-05 MDT
Agent: Cody
Status: Completed

## Summary

- Investigated Terry's `openclaw wiki status` failure on VPS1 after Edith's Agent Registry wiki ingestion was fixed.
- Confirmed Edith could run wiki commands successfully, while Terry failed with `Cannot read properties of undefined (reading 'localeCompare')`.
- Compared Terry and Edith memory-wiki configuration.
- Fixed Terry by changing the memory-wiki plugin from bridge mode to isolated mode while keeping the shared wiki path.

## Root Cause

Terry's memory-wiki config was set to:

- `vaultMode: bridge`
- bridge artifact indexing enabled
- shared search backend enabled

Edith's working config used:

- `vaultMode: isolated`
- bridge disabled
- the same shared wiki path: `/opt/openclaw/shared/knowledge/wiki`

The bridge-mode wiki status path was crashing inside the OpenClaw gateway with `localeCompare` on an undefined value. Switching Terry back to isolated mode restored the expected shared-wiki status behavior.

## Fix Applied

- Backed up Terry's config to:
  - `/home/node/.openclaw/openclaw.json.bak-cody-terry-wiki-20260705-1608`
- Updated Terry's `memory-wiki` plugin config:
  - `vaultMode: isolated`
  - `bridge.enabled: false`
  - `vault.path: /opt/openclaw/shared/knowledge/wiki`
  - `search.backend: shared`
  - `search.corpus: all`
- Restarted Terry's container.

## Verification

- Terry container restarted healthy.
- `openclaw wiki status` now succeeds from Terry.
- Terry reports:
  - vault mode: isolated
  - vault ready: `/opt/openclaw/shared/knowledge/wiki`
  - bridge disabled
- `openclaw wiki search --backend shared --corpus wiki Agent-Registry` returns `ZedBiz Agent Registry Snapshot` as result #1.
- `openclaw wiki compile` succeeds from Terry: `385 pages, 1 indexes updated`.
- `openclaw wiki lint` succeeds from Terry and reports existing unrelated wiki lint debt: `80 issues`.

## Notes

- The remaining config warning about `plugins.entries.memory-core` being present while the memory slot is `openclaw-mem0` still appears, but it does not block wiki status, search, compile, or lint.
- The shared wiki still has unrelated lint debt; this fix restored Terry's ability to verify the shared wiki.
