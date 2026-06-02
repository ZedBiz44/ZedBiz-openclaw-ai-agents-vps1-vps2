# 2026-06-01 - Standard AGENTS.MD Template

## Summary
- **Date:** 2026-06-01 Mountain Time
- **Agent:** Manus
- **System:** Notion, OpenClaw, AI Agent Registry
- **Change Type:** documentation-reviewed, agent-template-updated
- **Status:** done

## Why This Was Done
- Jack needed a standard `AGENTS.md` template reviewed and validated for use as the baseline for all OpenClaw agents.
- Two versions were reviewed in sequence: `v2026.6.1-draft` and `v2026.6.1-concise`.
- Goal was to identify gaps, validate structure, and confirm production-readiness.

## What Was Reviewed

### v2026.6.1-draft
- Reviewed full template structure including Purpose, Agent Setup, File Map, Startup Rules, Guiding Principles, Business Lens, Daily Operating Rules, Decision Framework, Execution Loop, Learned Lessons, Proactive Patterns, Tool Rules, Security Rules, Memory And Documentation, Communication Standards, Shared Channel Behavior, Escalation Rules, Status Format, Heartbeat Rules, Bulk Work Rules, Multi-Phase Work Rules, End Of Session Rules, and Template Customization Checklist.

**Gaps Identified:**
- No mention of Skills or SKILL.md discovery in the template.
- File Map did not include Skills directory.
- Startup Rules were passive -- no positive trigger for Skills check.
- Learned Lessons section had no instruction for how to add new lessons.
- Proactive Patterns section naming was weak; read as aspirational rather than doctrine.
- Template Customization Checklist was buried at the bottom.
- No version or change tracking instruction inside the file.

**Clarification on Skills Gap:**
- After discussion, confirmed the correct pattern is: agent checks a skills index or list (not individual SKILL.md files), then reads only the specific SKILL.md for a skill it is about to use.
- The real gap is whether the template tells the agent how to discover skills exist, and when to look.
- If skill discovery is code-driven in OpenClaw, the template does not need to address it. If prompt-driven, a discovery instruction is needed.

### v2026.6.1-concise
- Reviewed the reworked concise version. Significant improvement over draft.

**What Improved:**
- Purpose section explicitly states Skills and SKILL.md files handle reusable task methods.
- Startup Rules now include "Check available Skills before specialized work" and "Follow the relevant SKILL.md when a skill applies."
- Skills And Tools section added with correct doctrine.
- Priorities order added: Correctness > Evidence > Safety > Minimal change > Consistency > Performance.
- Maintenance Rules added to prevent file bloat over time.

**Remaining Gaps:**
- Skills discovery mechanism still implicit -- instruction says when to check but not how.
- Authority conflict rule dropped from draft -- no instruction for when Jack's direct instruction conflicts with a rule in the file.
- Completion Rules have no prompt to record what happened when documentation was required.
- Routing Rules hardcode Jack's setup (GitHub, Notion) rather than using placeholders for a shared template.
- Agent Setup dropped "Authority Level" field from the draft version.

## Decisions Made
- Template status set to Current in Notion at v2026.6.1-concise.
- Template is production-ready with two recommended additions: Skills discovery method and authority conflict rule.

## Related Links
- Notion: Standard-AGENTS-MD-Template (372a3e33d581814fb813cd0ff647579d)
