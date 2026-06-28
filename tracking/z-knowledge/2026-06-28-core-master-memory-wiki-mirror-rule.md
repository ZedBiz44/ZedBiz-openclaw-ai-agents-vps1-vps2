# 2026-06-28 | Cody | Core Master Memory Wiki Mirror Rule

Date: 2026-06-28 | Author: Cody | Status: Complete

## Summary

Added a mandatory Z-Knowledge rule: every durable entry created or updated in a Notion Core Master Database must have a corresponding Memory Wiki entry for agent retrieval.

This was prompted by the GHL Affiliate Program research issue where People records were created in Notion Z-Knowledge but matching Memory Wiki entity pages were not created.

## Operating Rule

A Core Master Database record is not complete until the matching Memory Wiki page exists and is listed in the completion report.

Required mirror mapping:

- Core Master People records -> Memory Wiki `entities/` pages for each person.
- Companies, clients, prospects, tools, platforms, products, services, offers, and projects -> Memory Wiki `entities/` pages.
- Ideas, frameworks, strategies, methods, templates, SOP patterns, and reusable concepts -> Memory Wiki `concepts/` pages.
- Research summaries, reviews, recommendations, comparisons, and decision briefs -> Memory Wiki `syntheses/` pages.
- Raw evidence or source notes -> Memory Wiki `sources/` pages.

For Notion People records, the Memory Wiki person entity is mandatory. Agents should default to `wiki/entities/<person-slug>.md` unless the active wiki instructions require a people subfolder.

## Tool Limitation Rule

If a wiki mutation tool cannot create entity pages, the agent must manually create the Memory Wiki Markdown file with proper frontmatter.

If the wiki cannot be written at all, the agent must stop before bulk-creating Core Master records and ask Jack whether to proceed with a Notion-only partial. Agents must not create a large batch of Notion Core Master records and leave wiki mirrors as an unapproved follow-up.

## Skills Updated

- `ZedBiz44/zedbiz-knowledge-routing-skill`: `abcf601`
- `ZedBiz44/zedbiz-wiki-research-skill`: `d2c62fc`
- `ZedBiz44/zedbiz-notion-knowledge-publishing-skill`: `c521ee2`
- `ZedBiz44/small-bite-wiki-research-skill`: `b58ac5c`

## Live Rollout

VPS1 active path updated:

- `/opt/openclaw/agents/{agent}/skills`

Verified `openclaw skills list --eligible` shows all four Z-Knowledge research skills for running VPS1 agents:

- Amanda
- Edith
- Grogar
- Inga
- Maggie
- Marsha
- Terry
- Victor
- Vivian
- Wilma

Gohzed was updated on disk. Zara was skipped because `/opt/openclaw/agents/zara/skills` does not exist.

VPS2 active paths updated:

- `/root/.openclaw-harry/.openclaw/skills`
- `/root/.openclaw-frank/.openclaw/skills`
- `/root/.openclaw-suzy/.openclaw/skills`

Also refreshed VPS2 `workspace/skills` copies for compatibility.

Verified `openclaw skills list --eligible` shows all four Z-Knowledge research skills for:

- Harry
- Frank
- Suzy

## Completion Report Requirement Added

Agents must report each Notion Core Master page paired with its exact Memory Wiki file. If any mirror is missing, the task is incomplete unless Jack explicitly approved a Notion-only partial.
