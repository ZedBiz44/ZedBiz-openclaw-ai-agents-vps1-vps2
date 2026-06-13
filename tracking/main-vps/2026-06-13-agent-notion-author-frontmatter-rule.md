# Agent Notion Author Frontmatter Rule Rollout - 2026-06-13

Date: 2026-06-13 | Author: Cody | Status: Completed

## Summary

Added a Notion page creation rule to live agent `AGENTS.md` files so each agent uses its own name in page front matter instead of defaulting to Cody.

Required visible front matter pattern:

```text
Date: YYYY-MM-DD | Author: {Agent Name} | Status: Draft plan for review
```

## Scope

VPS1 Docker agents updated:

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

VPS2 folder/systemd agents updated:

- Frank
- Harry
- Suzy

## Verification

Confirmed each updated `AGENTS.md` contains the correct agent-specific author example:

- VPS1 examples include `Author: Amanda`, `Author: Edith`, `Author: Gohzed`, `Author: Grogar`, `Author: Inga`, `Author: Maggie`, `Author: Marsha`, `Author: Terry`, `Author: Victor`, `Author: Vivian`, and `Author: Wilma`.
- VPS2 examples include `Author: Frank`, `Author: Harry`, and `Author: Suzy`.
- Literal `Author: Cody` checks returned no matches in the updated live agent `AGENTS.md` files.

## Notes

- Each live file was backed up before editing with a `bak-notion-author-rule` suffix.
- No agent containers or services were restarted.
- Frank was found on VPS2 as a live workspace but did not appear in the Agent Registry search results used during this pass; he was still included because the live workspace exists.
