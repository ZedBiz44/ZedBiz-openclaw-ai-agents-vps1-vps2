# 2026-06-01 - Standard TOOLS.md Template

## Summary

- **Date:** 2026-06-01 Mountain Time
- **Agent:** Manus
- **System:** Notion, OpenClaw, AI Agent Registry
- **Change Type:** documentation-updated, agent-template-created
- **Status:** done

## Why This Was Done

- Jack needed a standard `TOOLS.md` template for OpenClaw agents.
- The source material had useful safety guidance but needed to become a true tool map.
- A useful `TOOLS.md` must tell the agent what tools exist, what unlocks them, how to invoke them, what risk level they carry, and what fallback to use.

## What Changed

- Created shared Notion document `Standard-TOOLS-MD-Template`.
- Stored it in the `Agent-Documents` database as `Tools-MD`.
- Set the shared template version to `v2026.6.1-standard`.
- Built the template around:
  - Purpose
  - Capability gates
  - Tool selection priority
  - Read-only versus action tools
  - Available tool inventory block
  - Standard tool categories
  - Error handling and fallbacks
  - Credential and secret rules
  - Maintenance checklist
- Removed non-relevant references from the shared template:
  - Git and GitHub sections
  - Anthropic API access
  - Slack
  - Telegram
  - Environment summary
  - VPS, Docker, and OpenClaw runtime section
- Updated the shared template version to `v2026.6.1-general`.
- Created `Victor-Tools-Template` as a reference copy before removing the infrastructure sections from the shared template.
- Kept environment summary plus VPS, Docker, and OpenClaw runtime guidance in Victor's version for infrastructure work.
- Set Victor's template version to `v2026.6.1-victor`.
- Trimmed the shared general template to reduce daily instruction load.
- Added a `Startup Verification Rule`.
- Added a fork-and-remove-unused-categories note for each agent copy.
- Tightened category descriptions while preserving the tool inventory block.
- Updated the shared template version to `v2026.6.1-general-2`.
- Integrated Tactical Economy doctrine into the shared template.
- Added Look-Before-Leap Protocol.
- Added strict file, install, command, script, automation, and reversibility boundaries.
- Added Web and External Action Rules, including the external action air-gap.
- Added Final Tool Action Filter.
- Updated the shared template version to `v2026.6.1-general-3`.
- Added `Template Customization` section near the top.
- Compact capability gate key list.
- Merged Look-Before-Leap and Final Tool Action Filter into one `Tool Action Filter`.
- Added concrete Skills discovery method.
- Added filled-in `Example: Notion MCP` inventory entry.
- Added explicit maintenance trigger for added/broken tools and major new projects.
- Updated the shared template version to `v2026.6.1-general-4`.
- Updated `Victor-Tools-Template` to mirror the latest shared template improvements while preserving technical/server content.
- Preserved Victor-specific Environment Summary, Server Safety Rules, VPS SSH example, and VPS/Docker/OpenClaw runtime guidance.
- Updated Victor template version to `v2026.6.1-victor-2`.
- Updated Victor character count to `12,082`.

## Design Notes

- Removed citation artifacts from the source text.
- Made the template generic enough for all OpenClaw agents.
- Kept Skills as the home for reusable task methods.
- Kept `TOOLS.md` focused on actual capabilities, invocation details, access requirements, gotchas, and boundaries.
- Added placeholder blocks so each agent can document real tools instead of only high-level categories.
- Split the general agent template from Victor's infrastructure reference so non-technical agents do not carry unnecessary VPS or Docker instructions.
- Kept the inventory block intact because it is the operational core of `TOOLS.md`.
- Kept scope, communication, and general behavior rules out of `TOOLS.md` unless they directly affect tool use.
- Added one concrete example entry to reduce inconsistent customization across agents.
- Victor's version intentionally runs longer than the shared template because server tooling needs stronger path, access, runtime, and safety context.

## Test Result

- **What was tested:** Notion page creation, database placement, page rendering, Victor reference copy creation, shared template slimming, startup verification revision, Tactical Economy integration, final polish revision, Victor alignment revision, and Technical Documentation journal update.
- **Result:** Shared template and Victor reference template were created and verified.
- **Evidence:** Created Notion pages `Standard-TOOLS-MD-Template` and `Victor-Tools-Template`, then updated the Technical Documentation journal record.

## Links

- Notion template page: https://www.notion.so/372a3e33d581817e8ca4f7cd1e2541bf
- Victor template page: https://www.notion.so/372a3e33d58181eda6fdd81636bf7bd6
- Agent-Documents database: https://www.notion.so/141ff5e3dfea492f8004afece936204e
- AI-Agent-Databases page: https://www.notion.so/371a3e33d58180b7b7b0fa140cbfea3c

## Review Session - 2026-06-01 (Manus)

Three versions of the shared template were reviewed in sequence during a live feedback session.

**v2026.6.1-general (first review):**
- Template read as a policy document rather than a tool map. Core tools, commands, and invocation details were missing.
- Raw citation artifacts (`[cite: 103]` etc.) were present and needed removal.
- Trigger conditions were inconsistent across tool categories.
- Capability gate key-to-capability mapping was missing.
- Tool categories were too generic with no invocation examples.
- Skills were not referenced.
- No example tool inventory entry existed.

**v2026.6.1-general-3 (second review):**
- Tactical Economy doctrine was the strongest new addition.
- Final Tool Action Filter was a clean close.
- Look-Before-Leap Protocol and Web And External Action Rules were solid improvements.
- Startup Verification Rule was a smart addition.
- Remaining gaps: Skills category still had no invoke path, no filled-in example tool entry, fork instruction buried in Purpose, no maintenance frequency trigger.

**v2026.6.1-general-3 (third review, same version re-read):**
- Confirmed the same gaps. No new version was pushed between second and third review.
- Recommendation: add one filled-in Notion MCP example entry and make Skills invoke path concrete.

**Skills Invoke Path Discussion:**
- Clarified that the Skills invoke path should be the actual OpenClaw skills discovery command, not a placeholder, because it is the same across all OpenClaw agents.
- If OpenClaw handles discovery in code, the template instruction is fine as-is.
- If prompt-driven, the actual command or path belongs in the template by default.
