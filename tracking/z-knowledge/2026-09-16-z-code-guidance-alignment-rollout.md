# Z-Code Guidance Alignment Rollout

Date: 2026-09-16 MDT  
Added by: Cody  
Status: Completed and verified

## Purpose

Align the live Z-Knowledge skills and Notion operating guidance with the current Z-Code rules identified by Edith and confirmed in the follow-up review.

## Problems Corrected

- Removed the conflicting instruction to create a Brief automatically when generic research has no Brief.
- Clarified that the shared six-digit value is the Topic Identifier, not a complete Z-Code.
- Clarified that every Biz-Plan receives its own complete allocator-issued Z-Code.
- Replaced the single hard-coded allocator client path with active-profile or approved-path discovery.
- Brought the Notion publishing SOP up to date with Record Title, Topic Registry relation, allocator verification, and permanent-retirement requirements.

## GitHub Source Changes

- [z-code-allocation-Skill PR 5](https://github.com/ZedBiz44/z-code-allocation-Skill/pull/5)
- [z-biz-plan-Skill PR 1](https://github.com/ZedBiz44/z-biz-plan-Skill/pull/1)
- [z-notion-knowledge-publish-Skill PR 3](https://github.com/ZedBiz44/z-notion-knowledge-publish-Skill/pull/3)

All three pull requests were squash-merged to their main branches.

## Notion Changes

Updated:

- Z-Biz-Plan-Skill-SOP
- Z-Notion-Knowledge-Publish-Skill-SOP

The current Z-Code-Allocation-Skill-SOP was reviewed and already held the correct allocator, correction, registry, and permanent-retirement rules.

## Live Rollout

Deployed the three aligned files to:

- VPS1: Amanda, Edith, GohZed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma.
- VPS2: Frank, Harry, and Suzy.
- VPS3: Ruby.
- VPS4: Rocky.

The deployment changed only:

- `z-code-allocation/SKILL.md`
- `z-biz-plan/SKILL.md`
- `z-notion-knowledge-publish/references/core-master-database-routing.md`

No production Z-Code was allocated, confirmed, failed, retired, reassigned, or changed during testing.

## Pilot And Verification

Edith was tested first.

- The new discovery rule found `/home/node/.openclaw/workspace/skills/z-code-allocation/scripts/request_z_code.mjs`.
- A live read-only allocator lookup returned `found: false` with exit success.
- All three skills were eligible and model-visible from the workspace source.
- A fresh GPT-6 Astra agent turn returned PASS and correctly stated all five aligned rules.
- No knowledge record, memory, or registry row was changed.

Fleet read-back then verified:

- Exact SHA-256 matches for the deployed allocator and Biz-Plan Skill files.
- The corrected Brief rule is present and the conflicting wording is absent.
- All eleven VPS1 containers were running and healthy.
- Frank, Harry, and Suzy services were active.
- Ruby's Hermes container was running.
- Rocky's OpenClaw gateway process was running and the three skills were discoverable.

Rocky's skill-discovery command also reported pre-existing missing environment warnings for Asana, Percify, and Gemini video. They did not affect this rollout.

## Recovery

The authoritative recovery source is the main branch of each Skill repository. Redeploy the required earlier commit if rollback is ever needed. No permanent server-side backup copies of retired Skill packages were retained.
