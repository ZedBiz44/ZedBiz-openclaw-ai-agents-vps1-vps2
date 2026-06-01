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

## Design Notes

- Removed citation artifacts from the source text.
- Made the template generic enough for all OpenClaw agents.
- Kept Skills as the home for reusable task methods.
- Kept `TOOLS.md` focused on actual capabilities, invocation details, access requirements, gotchas, and boundaries.
- Added placeholder blocks so each agent can document real tools instead of only high-level categories.
- Split the general agent template from Victor's infrastructure reference so non-technical agents do not carry unnecessary VPS or Docker instructions.
- Kept the inventory block intact because it is the operational core of `TOOLS.md`.
- Kept scope, communication, and general behavior rules out of `TOOLS.md` unless they directly affect tool use.

## Test Result

- **What was tested:** Notion page creation, database placement, page rendering, Victor reference copy creation, shared template slimming, startup verification revision, Tactical Economy integration, and Technical Documentation journal update.
- **Result:** Shared template and Victor reference template were created and verified.
- **Evidence:** Created Notion pages `Standard-TOOLS-MD-Template` and `Victor-Tools-Template`, then updated the Technical Documentation journal record.

## Links

- Notion template page: https://www.notion.so/372a3e33d581817e8ca4f7cd1e2541bf
- Victor template page: https://www.notion.so/372a3e33d58181eda6fdd81636bf7bd6
- Agent-Documents database: https://www.notion.so/141ff5e3dfea492f8004afece936204e
- AI-Agent-Databases page: https://www.notion.so/371a3e33d58180b7b7b0fa140cbfea3c
