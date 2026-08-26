# VPS1 Core-File Behavior Repair

Date: 2026-08-25
Agent: Cody
Status: Complete
Approver: Jack Zenert
Related issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/179
Related Notion audit: https://app.notion.com/p/3c7a3e33d5818147b828c03f1d846a34

## Purpose

Remove active VPS1 core instructions that cause forced replies, unsafe or ambiguous Notion routing, obsolete database destinations, false systemd claims, contradictory durable-publishing behavior, and stale memory recall.

## Approved Scope

- VPS1 agents: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma.
- Core files: `AGENTS.md`, `TOOLS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`, `MEMORY.md`, and agent KEY files.
- Disable the generic `notion` skill in each VPS1 agent's OpenClaw configuration.
- Preserve `z-notion-knowledge-publish` as the governed publishing workflow.
- Test Inga before fleet rollout.

## Planned Corrections

- Remove all active `3+3=6`, `2+2=4`, eye-colour, and chocolate-ice-cream test instructions.
- Replace obsolete tracker names with live canonical database/data-source resolution.
- Require governed Notion publishing through `z-notion-knowledge-publish` and Codex Apps Notion using the approved Codex OAuth route.
- Prohibit `ntn`, curl, direct API, environment-token, plaintext-key-file, and standalone Notion fallbacks.
- Replace broad automatic publishing rules with assignment-scoped authorization rules.
- Remove false VPS1 systemd service statements and identify Docker containers correctly.
- Remove transcript-summary lines and clearly stale Notion/tool/runtime fragments from curated `MEMORY.md` files while preserving durable business facts.

## Verification Required

- Generic `notion` reports disabled and not model-visible.
- `z-notion-knowledge-publish` remains eligible from the canonical non-backup path.
- No targeted forced-response text, obsolete tracker name, or false VPS1 systemd service remains.
- Agent container is healthy after restart.
- Inga responds normally to a non-publishing diagnostic prompt and identifies the correct governed Notion route when asked how she would publish authorized Z-Knowledge.
- Fleet rollout occurs only after the Inga pilot passes.

## Completed Changes

- Removed forced-response tests from Amanda, Gohzed, Grogar, Inga, Maggie, Marsha, and Terry KEY files.
- Removed forced eye-colour, arithmetic, and ice-cream responses from Maggie's `USER.md`; removed the ice-cream test from Edith and Inga `USER.md` files.
- Replaced obsolete tracker destinations for Gohzed, Inga, Maggie, Marsha, Vivian, and Wilma with live canonical database/data-source resolution.
- Replaced the overbroad automatic-publishing rule on all eleven agents with assignment-scoped durable-knowledge authorization.
- Corrected the direct confirmation-versus-auto-publish contradictions in Gohzed, Terry, and Vivian and aligned related wording in Edith, Grogar, Maggie, Marsha, and Victor.
- Added the same governed Notion route to all eleven `AGENTS.md` files: `z-notion-knowledge-publish` plus Codex Apps Notion through approved Codex OAuth; no raw-token or direct-API fallback.
- Disabled `skills.entries.notion.enabled` on all eleven agents. The generic skill is now disabled, ineligible, and not model-visible.
- Preserved `z-notion-knowledge-publish` as eligible and model-visible from `/home/node/.openclaw/skills/z-notion-knowledge-publish/SKILL.md` on all eleven agents.
- Removed false VPS1 systemd service statements for Amanda, Gohzed, Marsha, Terry, Vivian, and Wilma and corrected applicable `TOOLS.md` entries to Docker containers.
- Removed transcript-summary lines from all eleven curated `MEMORY.md` files and removed clearly stale direct-Notion, obsolete-skill, model/runtime, and credential-like fragments.
- Updated Edith's active knowledge-skill names to the current `z-*` names.
- Physically deleted the disabled managed generic `notion` folders from Amanda, Inga, Victor, and Wilma.
- Deleted Edith's obsolete `EDITH-KEY.md`; retained the current `EDITH_KEY.md`.
- Deleted Marsha's wrong-agent `maggie-key.md`.
- Removed unnecessary self-name and cross-agent wording from all eleven `AGENTS.md` files while preserving operational reporting, ownership, identity verification, record attribution, and literal paths or filenames.

## Verification Result

- Inga pilot passed before fleet rollout.
- Inga fresh-session behavior test returned only `READY` and the approved Codex OAuth route; no forced startup response appeared.
- Inga completed a live read-only Codex Apps Notion OAuth fetch of page `7a1a3e33-d581-83e3-ae02-01de59538c3e` and returned the exact title `Technical Documentation`.
- The Inga proof reported one successful `codex_apps.notion.fetch` call and zero tool failures; no fallback was used.
- On 2026-08-26, Jack reported that his own post-repair Inga test worked correctly.
- All eleven containers returned `healthy` after restart.
- All eleven report generic `notion`: disabled `true`, eligible `false`, model-visible `false`.
- All eleven report `z-notion-knowledge-publish`: eligible `true`, model-visible `true`, non-backup canonical path.
- Live scans found zero targeted forced-response strings, obsolete tracker names, false VPS1 systemd service names, old mandatory-capture headings, transcript-summary lines, or partial Notion token strings in the corrected core files.

## Deferred Core-File Planning

Jack explicitly deferred further core Markdown architecture work to another issue and thread.

- Review oversized always-loaded files, especially Vivian's `AGENTS.md`, Inga/Maggie/Grogar `SOUL.md`, and Victor's KEY files.
- Treat identical policy requirements on separate agents as valid; duplication is not itself a defect. Consolidate only the authoring source when it can still deploy the required policy independently to each agent.
- Review DREAMS and generated historical memory corpora separately. This repair cleaned curated `MEMORY.md`; it did not rewrite historical source journals or dream corpora.
- Do not mix that later architecture work into this completed Notion-route repair.

## Rollback

Temporary same-session rollback copies were removed after verification. GitHub and the canonical skill repository are the recovery sources; no backup copy was returned to an active workspace or skill-discovery root.

