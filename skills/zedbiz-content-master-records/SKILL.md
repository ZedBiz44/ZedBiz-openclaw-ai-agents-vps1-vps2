---
name: "zedbiz-content-master-records"
description: "Use for importing, Z-Coding, publishing, mirroring, connecting, and verifying Briefs, Biz-Plans, Research, and other ZedBiz Core records."
---

# ZedBiz Content Master Records

Use this skill as the master workflow for imported Evernote/Notion material and for Briefs, Biz-Plans, Research, Jack notes, Sources, and other records entering a ZedBiz Content Master Database.

This skill coordinates the assignment. Specialist skills own their detailed procedures.

## Load Specialist Skills Only When Required

- Load `request-z-code` before assigning, reserving, confirming, failing, checking, or reassigning any Z-Code.
- Load `zedbiz-notion-knowledge-publishing` before creating, moving, or materially updating a Content Master Database record. Follow its approved Codex Apps Notion access route.
- Load `zedbiz-knowledge-routing` when the human has not specified a destination database and the material could plausibly belong to more than one Core, database, or durable layer. For Core records, use routing to select the correct Wiki artifact type and location; the Wiki mirror itself is mandatory.
- Skip a full routing pass when the destination database is explicitly stated or unambiguous from the source. Still verify that the destination exists and fits the live schema.
- Load either `small-bite-wiki-research` or `zedbiz-wiki-research` when research is required. Do not load both by default.
- Use `small-bite-wiki-research` for a narrow first pass, a broad task likely to time out, or the smallest useful durable research artifact.
- Use `zedbiz-wiki-research` for substantial source-backed research, conflicting evidence, important verification, or a durable synthesis.
- When a Core record needs its mandatory Memory Wiki mirror without new research, use `wiki-maintainer` as the technical Wiki operator.

If a required specialist skill is unavailable, stop before its governed mutation and report the exact missing skill or tool.

## Non-Negotiable Rules

- Preserve an original imported page body exactly. Change only properties, title, icon, cover, or parent unless Jack explicitly authorizes body editing.
- If a cleaned or synthesized version is needed, preserve the original and create a separate derivative record.
- Stop and escalate if the source exposes secrets or sensitive material that should not be copied into a durable system.
- Search before creating. Reuse or update a matching record when it represents the same item and purpose.
- Never calculate, guess, increment, copy, or reuse a Z-Code. Use the centralized allocator.
- Never identify or connect a topic using the six-digit Topic Identifier alone. Use the complete Core + Lane + Topic Identifier identity and the allocator-authoritative Name-Key or topic record.
- Create only records justified by the assignment and evidence. Do not automatically create a Brief, Biz-Plan, Research page, relation, or extra Wiki artifact beyond the mandatory mirror for each Core record.
- Every record created, moved into, or materially updated in a Core Content Database must have a corresponding Memory Wiki record for agent retrieval. Process the Notion record and Wiki mirror as one completion unit.
- Use the live database schema, current SOP, and correct template. Do not rely on remembered field names, data-source IDs, or select values.
- Do not invent people, tools, businesses, relationships, claims, URLs, ownership, readiness, or commercial facts.
- Limit concurrent Notion mutation calls to two. Process Z-Code allocation, page creation, minimal verification, and confirmation sequentially per record.
- Never claim completion without fetching and checking every changed Notion record and validating every changed Wiki artifact.

## Workflow

### Recall And Open One Activity Record

- Query the active external memory provider for the topic, source IDs, prior attempts, decisions, and handoffs.
- Treat recalled content as a lead, not verified truth.
- Open or update one compact activity record for the assignment. Do not create one memory per page or step.

The activity record must contain the subject, assignment, status, source or agent, Mountain Time timestamp, authoritative location when available, and next action or handoff. At closeout, add affected page IDs or URLs, Z-Codes, decisions, verification results, unresolved gaps, and the final status.

### Inspect Governing Sources

- Fetch the source page or file.
- Fetch the target Content Master Database or canonical routing page and resolve the live data source and schema.
- Fetch the Z-Knowledge Database Record SOP and the current template or SOP for each intended Page-Type.
- For an imported Notion page, retain its page ID and a pre-change body snapshot or reliable fingerprint.

### Build The Working Record Manifest

Before mutations, create an internal manifest using `references/record-manifest.md`.

- Plan the complete record package, but execute one record at a time.
- Record the source, destination, record type, Name-Key, Core, Lane, research mode, existing-record match, Z-Code state, final URL, mandatory Wiki artifact, and verification state.
- Update the manifest after every allocator or publishing step so retries resume from known state.

### Route Only When Needed

- If the destination database is specified and consistent with the source, validate it and continue.
- If no destination is specified and the source could fit more than one Core, database, or durable layer, load and follow `zedbiz-knowledge-routing`.
- Store in Notion when humans need to review, filter, decide, or act from the record.
- Store in the Memory Wiki when agents need stable, reusable, source-backed retrieval.
- Every Core Content Database record must exist in both Notion and the Memory Wiki. Use routing to choose the correct Wiki artifact type and location.
- Link the paired Notion and Wiki artifacts when useful.
- For non-Core knowledge, follow the routing decision instead of creating unnecessary durable artifacts.

### Search And Resolve Topic Identity

- Search the target database and relevant related databases using topic names, aliases, domains, source URLs, and likely Name-Key values.
- Fetch plausible matches. Titles alone are insufficient.
- Use allocator lookup for likely existing Name-Keys before allocating anything.
- Reuse the existing topic only after confirming the same full Core + Lane + Topic Identifier identity.
- If the source and candidate are materially different, use a new topic.
- If identity remains ambiguous, stop before merging, moving, relating, or allocating and request review.

### Decide Which Records Are Justified

- Read `references/page-type-decisions.md`.
- Preserve raw imported or Jack-authored source material as its appropriate source/Page-Type.
- Reuse an existing reliable Brief when it already covers the topic and purpose.
- Create or update a Brief only when the assignment needs a durable decision-oriented overview and the evidence supports one.
- Create a Biz-Plan only when the record contains or can responsibly develop an executable marketing and action plan.
- Use Research when the main output is source-backed findings, comparison, verification, or analysis rather than an operating plan.
- If a useful record is not yet justified, record the gap and recommended next milestone instead of creating a placeholder.

### Select The Research Path

- Do not call a research skill for a straight import or classification job that adds no new factual claims.
- Use `small-bite-wiki-research` for the smallest useful first-pass artifact or timeout-prone broad research.
- Use `zedbiz-wiki-research` for substantive source-backed research or synthesis.
- Separate source statements, agent conclusions, verified facts, confidence, and verification gaps.
- Use current authoritative sources for health, legal, financial, scientific, performance, ownership, rights, or other high-stakes claims.

### Allocate, Publish, Verify, And Confirm One Record At A Time

- Load `request-z-code` and use lookup before allocation.
- Reuse the allocator-authoritative topic identity when the existing topic match is confirmed.
- Allocate one new record and retain its stable `request_id`.
- If the allocator returns `requires_review`, stop that record and report the queue ID.
- Load `zedbiz-notion-knowledge-publishing` and create, move, or update the record through the approved Notion route.
- Immediately fetch the page and minimally verify its page ID, parent data source, Page-Name, Page-Type, and exact Z-Code.
- Confirm the allocation only after that minimal verification succeeds.
- If page creation fails, report allocator failure. Never recycle the code.
- After confirmation, complete relations, content checks, icon verification, and the full quality gate.
- Then continue to the next manifest record.

### Name, Classify, And Connect Carefully

- Follow the live naming SOP. Capitalize words and separate them with dashes.
- Distinguish Brief, Biz-Plan, Jack note, Research, Source, and sibling records in Page-Name.
- Use one stable topical icon across a record family unless the Page-Type rules require otherwise.
- Fill every required operating field from the live schema and SOP.
- Fill optional fields only when supported by evidence.
- Add a relation only after fetching the candidate and confirming its identity.
- Connect same-topic records using the full allocator-authoritative topic identity plus explicit relations, never the six-digit identifier alone.

### Create Or Verify The Mandatory Core Wiki Mirror

- For every Core Content Database record, create or verify the corresponding Memory Wiki record in the same assignment.
- Use the routing decision to select `sources/`, `entities/`, `concepts/`, `syntheses/`, or another approved Wiki location.
- If new research is required, use the selected research skill; it should use `wiki-maintainer` for the technical Wiki operation when available.
- If no new research is needed, use `wiki-maintainer` directly to create or update the mirror.
- Prefer updating an existing canonical Wiki page over creating a duplicate.
- Run standard Wiki status/lint and the ZedBiz frontmatter validation required by the active Wiki skill.
- Do not mark a Core record complete until the exact Wiki file exists and the Notion/Wiki pair is reported.

### Complete Quality Control And Closeout

- Read `references/record-quality-gate.md`.
- Fetch every changed Notion page after all mutations.
- Verify the source page body remained unchanged when preservation was required.
- Check for duplicate full Z-Codes and conflicting full topic identities.
- Verify Wiki artifacts and lint results only when Wiki work occurred.
- Update the single activity-memory record with final results and verify the memory write.
- Report records moved, created, updated, reused, deliberately not created, and why.

## Failure Handling

- Invalid schema or select value: refetch the live schema, correct only the failed value, and retry only that record.
- Connector timeout: inspect live state before retrying because the first mutation may have succeeded.
- Duplicate or questionable Z-Code: stop, use allocator lookup/status, and do not patch around it.
- Wrong or uncertain topic match: stop before moving, merging, connecting, or allocating.
- Source-body mismatch: stop immediately and avoid additional mutations.
- Missing exact relation: leave it unlinked and report the gap.
- Wiki operation unavailable: do not invent a mirror or claim it exists. Report the exact unavailable skill, tool, or validation command.
- Partial package failure: preserve the manifest state, verify completed records individually, and resume only from known state.

## Completion Report

- Record links, Page-Names, Page-Types, and destination databases.
- Full Z-Codes and confirmed full topic identities.
- Existing topics and records reused.
- Records created, moved, updated, or deliberately not created.
- Important verified relations.
- Imported-body preservation and icon verification.
- Research path and important verification gaps.
- Mandatory Core Wiki artifact and exact lint results.
- Activity-memory provider, verification result, and next action.

