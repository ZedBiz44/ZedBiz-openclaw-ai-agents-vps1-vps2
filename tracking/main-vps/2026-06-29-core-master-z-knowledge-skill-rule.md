# Core Master Z-Knowledge Skill Rule

Date: 2026-06-29 | Agent: Cody | Status: Final

## Summary

- Updated ZedBiz skill instructions so every Notion Core Master Database row must have `Z-Knowledge` filled when the property exists.
- Converted `Z-Knowledge` from a best-effort property into a completion gate.
- Added stop-and-review language: if no live Notion option fits, agents must stop before finalizing and report the missing option/value needed for Jack's review.

## Updated Skill Repositories

- `ZedBiz44/zedbiz-notion-knowledge-publishing-skill`
  - Commit: `883f068`
  - Message: `Require Z-Knowledge on Core Master records`
  - Updated:
    - `zedbiz-notion-knowledge-publishing/SKILL.md`
    - `zedbiz-notion-knowledge-publishing/references/core-operating-fields.md`
    - `zedbiz-notion-knowledge-publishing/references/z-knowledge-folder-map.md`
- `ZedBiz44/zedbiz-knowledge-routing-skill`
  - Commit: `f58dbe3`
  - Message: `Require Z-Knowledge in Core Master routing`
  - Updated:
    - `zedbiz-knowledge-routing/SKILL.md`

## Rollout Copy

- Synced the same changes into the local rollout-master bundle:
  - `D:\Google Drive\Documents\Codex-Projects\ZedBiz-Skill-Repos\_sync\zedbiz-skills-master\zedbiz-notion-knowledge-publishing`
  - `D:\Google Drive\Documents\Codex-Projects\ZedBiz-Skill-Repos\_sync\zedbiz-skills-master\zedbiz-knowledge-routing`

## Verification

- `zedbiz-notion-knowledge-publishing` passed skill validation.
- `zedbiz-knowledge-routing` passed skill validation.
- Both source skill repos were pushed to GitHub on `main`.

## Notion Journal

- https://app.notion.com/p/38ea3e33d5818118a19af3c08d7c99c8
