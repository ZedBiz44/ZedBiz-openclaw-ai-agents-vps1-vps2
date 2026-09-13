# Z-Knowledge Database Record SOP

Date: 2026-09-13 | Author: Cody | Status: Active

## Purpose

Create, update, summarize, condense, expand, combine, or research information into reliable and reusable knowledge records, then store each record in the correct governed Notion database.

This procedure applies to information from any source. The source may be a person, website, document, email, chat, cloud drive, note application, database, memory provider, or original research.

## Source Of Truth

- The Z-Code Allocator database on VPS1 is the technical source of truth for Topic Identifiers, complete Z-Codes, Name-Keys, aliases, reservations, and audit history.
- This GitHub repository is the source of truth for allocator code and this technical SOP.
- Notion holds the operational knowledge records and human-readable Registry mirrors.
- The live `z-code-allocation` skill is the required agent workflow for allocator access.

People and agents must not calculate, increment, copy, select, recycle, or repair a Z-Code manually.

## When A Durable Record Is Appropriate

A record is meaningful when it preserves a decision, verified fact, reusable procedure, important relationship, approved plan, useful research result, or other information that will help future work.

A record is durable when it is expected to remain useful beyond the current conversation or assignment and can be maintained as facts change.

Do not create a permanent record for passing mentions, unverified guesses, duplicate material, temporary working notes, or findings that the user has not authorized for publication.

## Work Boundaries

- Follow the user's requested scope and authorization.
- Read-only, investigation-only, or “do not change anything” instructions do not authorize publishing or updating a permanent record.
- Knowledge capture does not override security, privacy, cost, approval, ownership, or destructive-action limits.
- Record directly relevant missing history when needed for the current assignment. Put broader cleanup into an approved backlog rather than silently expanding the task.

## Routing Rule

- The owning entity, subject, project, or initiative selects the destination database.
- The requested output selects the Page-Type.
- The source describes where the information came from. It does not automatically select the database.

Use the current knowledge-routing and Notion-publishing skills to confirm the destination and required fields.

## Topic And Record Names

Keep the topic identity separate from the individual page title.

- **Name-Key:** the stable, dash-separated topic identity used by the allocator. Related records share it.
- **Topic-Name:** the clear human-readable topic label stored once in the Z-Code Topic Registry.
- **Record-Title:** the exact current title of one Notion knowledge page.
- **Page-Name format:** `[Name-Key]-[Page-Type]-[Descriptor]`.
- **Descriptor:** a short phrase that distinguishes this record from other records under the topic.

Search the destination database, the Topic Registry, and the allocator before creating a new Name-Key. Reuse the existing topic when the subject identity is the same. Use a different Name-Key only when the subject is genuinely different.

Do not edit a Name-Key across individual Registry rows. An administrator must use the allocator's controlled topic-rename process. The previous Name-Key remains an alias to the same topic.

## Z-Code Structure

Each complete Z-Code has four parts:

`Knowledge-Family-Knowledge-Lane-Topic-Identifier-Record-Suffix`

Example: `Z1ST-80001-100042-050`

- The Knowledge Family identifies the broad ownership group.
- The five-digit Knowledge Lane identifies the governed category within that family.
- The six-digit Topic Identifier identifies one topic within that family and lane.
- The three-digit Record Suffix identifies one record under the topic.

Related records share the first three parts and have different Record Suffixes.

Current suffix ranges are:

- `010-019` for Brief records.
- `020-049` for Biz-Plan records.
- `050-999` for other Page-Types.
- `000-009` remain unused.

These ranges explain the code. They are not instructions for choosing a number manually.

## Record Creation Workflow

- Confirm that a durable record is authorized and useful.
- Research and verify the information needed for an accurate record.
- Search for an existing record and likely matching Name-Key.
- Confirm the destination database, Knowledge Core, Knowledge Lane, Page-Type, and proposed Record Title.
- Use `z-code-allocation` to look up the Name-Key.
- Reuse the established topic when the identity matches.
- Reserve a new Z-Code through the allocator only when a new record is authorized.
- Keep the same Request ID when retrying the same allocation.
- Create or update the Notion record with the exact issued Z-Code.
- Fill every relevant required field and remove secrets or credentials.
- Read the saved page back and verify its title, URL, Page-Type, Z-Code, destination, and important content.
- Confirm the allocation only after the final Notion page exists and passes verification.
- If page creation fails, report the allocation as failed. Do not reuse its code.

## Required Record Information

Complete the fields required by the destination database. At minimum, verify:

- Page Name or Record Title.
- Purpose.
- Z-Knowledge-Core.
- Z-Code.
- Page-Type.
- Creator or responsible agent.
- Status.
- Confidence.
- Sensitivity.
- Source and source links where applicable.
- Relevant business, knowledge-use, person, tool, project, or other approved relations.

Use one clear sentence for Purpose. Set confidence from the quality and recency of the evidence, not merely the software where the material was found. Imported or older information must be verified before a higher confidence rating is used.

## Registry Records

The allocator's Notion mirror maintains two databases.

### Z-Code Registry

One row represents one complete Z-Code and individual knowledge record. It includes the Record Title, Notion URL, Page-Type, Record Suffix, status, allocation details, and a relation to its topic.

### Z-Code Topic Registry

One row represents one Knowledge Core, Knowledge Lane, and Topic Identifier combination. It stores the Name-Key and Topic-Name once. Related Z-Code Registry rows connect to this topic row and display its names through the relation.

The Registry databases are human-readable mirrors. Do not treat a manual Registry edit as a replacement for an allocator transaction.

## Permanent Retirement Rule

Every Topic Identifier and complete Z-Code becomes permanently reserved when issued.

- Stale, failed, abandoned, reassigned, withdrawn, merged, and deleted codes are never assigned to another topic or record.
- A reassigned code remains a historical alias to its current replacement.
- Gaps in the sequence are normal and must not be filled manually.
- The allocator must check active records, aliases, and permanent issuance history before returning a code.

## Corrections And Reassignment

- Correct ordinary record wording or content without changing its identity or Z-Code.
- Use the controlled topic-rename process when the Name-Key needs correction. Preserve the former Name-Key as an alias.
- Use the controlled topic-reassignment process when the Knowledge Family or Knowledge Lane is wrong.
- Topic reassignment changes all related complete Z-Codes, preserves their Record Suffixes, retires the former codes, and creates old-to-new aliases.
- If only one record belongs to a different subject while the remaining topic records are correct, stop and review whether that record needs a separate Name-Key. Do not move the entire topic blindly.

## Secrets And Sensitive Information

- Never store passwords, private keys, tokens, complete environment files, or other credentials in Notion.
- Remove exposed credentials from imported material.
- Store required credentials through the approved secret manager and record only the safe credential reference.
- Stop and notify the responsible administrator if exposed credentials are discovered.

## Failure Handling

- If the allocator is unavailable, keep draft working notes but do not invent a code or publish the final governed record.
- If a Name-Key conflicts with a different Core or Lane, stop that record and send the review ID to the assigned allocator administrator.
- If identity, destination, classification, or ownership is unclear, stop and request a decision before publication.
- If Notion mirroring fails, preserve the allocator result and leave the mirror event queued for retry.
- After three failed attempts at the same step, record the failure and request technical review.

## Verification And Completion

The work is complete only when:

- The record exists in the correct Notion database.
- Its content and required properties were read back and verified.
- The allocator shows the allocation as active.
- The complete Z-Code is unique and exactly matches the record.
- The Z-Code Registry shows the correct Record Title and Notion URL.
- The record is related to the correct Z-Code Topic Registry row.
- The Topic Registry shows the correct Name-Key, Topic-Name, Core, Lane, and Topic Identifier.
- Any correction, failure, reassignment, or rename has an audit record and preserved alias where required.

## Related Technical Sources

- [Z-Code Allocation Skill](https://github.com/ZedBiz44/z-code-allocation-Skill)
- [Z-Code Allocator Service](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/tree/main/services/z-code-allocator)
- [Z-Code Allocation SOP in Notion](https://app.notion.com/p/3a3a3e33d58180f7bf5ed69f0a398b84)
- [Z-Code Registry in Notion](https://app.notion.com/p/89267d1e18f84f669269c900dc730b08)

