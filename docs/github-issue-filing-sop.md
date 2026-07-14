# GitHub Issue Filing SOP

Date: 2026-07-14 | Agent: Cody | Status: Active

## Purpose

This SOP defines how ZedBiz agents record technical work in GitHub so future agents can find what happened without asking Jack to replay the story.

GitHub is the technical source of truth. Notion is the human-readable planning and summary layer.

## Repo Decision Rule

Every technical issue goes into exactly one primary repo.

| Repo | Use For |
| --- | --- |
| ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2 | OpenClaw agents on VPS1 or VPS2, including Amanda, Victor, Marsha, Wilma, Edith, Inga, Gohzed, Grogar, Maggie, Terry, Vivian, Harry, Frank, and Suzy. |
| ZedBiz44/ZedBiz-hermes-ai-agents-vps3 | Ruby, Hermes, or the VPS3 Hermes stack. |
| ZedBiz44/ZedBiz-general-tech-issues-updates | Server infrastructure, WHM, 1Password fleet work, Manus/Cody tooling, technical memory system work, and general tech that is not clearly agent-specific. |

If unsure, file in `ZedBiz44/ZedBiz-general-tech-issues-updates` and add `needs-routing`.

Older references to `ZedBiz44/zedbiz-ai-agents` are legacy wording unless live GitHub evidence proves otherwise. OpenClaw VPS1/VPS2 work belongs in `ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2`.

## Search Before Creating

Before starting work or creating a new issue, search GitHub first.

Search at least:

- The most likely repo.
- The agent name if an agent is involved.
- The system name, such as 1Password, Hindsight, WHM, OpenClaw, Hermes, Notion, or GitHub.
- One short topic keyword.
- Open and closed issues.

Read the most recent 3-5 relevant results before creating a new issue.

## Issue Title Format

Use this title format:

```text
YYYY-MM-DD | [Agent/Tool/System] | [Short description of what happened]
```

Examples:

- `2026-07-08 | Amanda | Asana webhook auth fix`
- `2026-07-08 | Victor | 1Password op CLI setup`
- `2026-07-08 | Ruby | WHM API access -- Imunify whitelist`
- `2026-07-08 | VPS1 Fleet | OPENAI_API_KEY vault reference fix`

## Required Labels

Every issue needs the minimum labels that make it searchable.

Required:

- `agent:` when a specific agent is involved.
- `system:` always.
- `type:` always.
- `status:` always.

Optional:

- `priority:` when useful.
- `needs-routing` when the issue may belong in a different repo.

## Issue Creation Checklist

Before creating:

- Search the most likely repo.
- Search by agent name.
- Search by system name.
- Search by short topic keyword.
- Check open and closed issues.

When creating:

- Use the standard title format.
- Add required labels.
- Fill the issue body with what is known.
- Include `Search Performed` in the body.
- Link related Notion page, GitHub file, PR, branch, VPS path, or SOP if available.

While working:

- Add comments for important attempts, failed attempts, fixes, verification, and decisions.
- Do not create a new issue just because the same task continued in a new session.
- Record failed attempts because future agents waste the most time repeating those.

Before closing:

- Add the final closeout comment.
- Confirm what was verified.
- Note whether registry, SOP, Tech Updates, technical records, or PRs were updated.

## Issue Body Template

```markdown
## What
One sentence: what is this issue about?

## Current Status
Open / In Progress / Blocked / Resolved

## Agent / System Affected
Agent name, VPS, platform, integration, or repo.

## Search Performed
What repos, agent names, system names, and topic keywords were checked before creating this issue.

## Related Existing Issues
Links to related or dependent issues, or `None found`.

## What Was Tried
- Attempt 1
- Attempt 2

## What Failed
What did not work and why.

## What Worked
The actual fix or current best answer.

## What Changed
Files edited, configs updated, containers restarted, Notion pages changed, or branches/PRs created.

## Next Action
The next practical step.
```

## Parent Issue / Workstream Rule

Use one main issue for a multi-day workstream.

Good examples:

- A 1Password startup failure gets one issue for the startup or secret-injection problem.
- A Codex/OpenClaw model rollout gets one issue for the model rollout workstream.
- A fleet upgrade gets one issue when the agents are being updated for the same reason and tested under the same rollout plan.

Create a separate issue when there is a separate root problem, separate system, separate decision path, or separate owner.

Cross-link issues when one workstream becomes a dependency for another.

Do not mash every related event into one giant issue. Link related issues clearly.

## Comment Update Rule

Agents must comment on the issue whenever something material happens.

Comment when:

- A diagnosis finding changes the direction.
- A fix is attempted.
- A fix fails.
- A fix works.
- A rollback happens.
- A test verifies the result.
- The task moves from one agent or repo to another.
- A Notion page, SOP, registry file, branch, PR, or technical record is updated.

A useful issue should let the next agent understand what happened without asking Jack to replay the story.

## PR And Main Branch Rule

GitHub Issues explain the work. Pull requests move code, configs, docs, and SOPs into the official source of truth.

If a branch contains technical changes, the work is not fully source-of-truth complete until one of these is true:

- The branch is merged to main through a PR.
- A PR is open and linked from the issue.
- The issue clearly states why the branch is intentionally not merged yet.

For live rollout work, the final issue comment should include:

- Branch name.
- PR link or reason no PR exists.
- Commit IDs for important changes.
- What was verified live.
- Whether main now reflects the live state.

Main branch is the default technical truth. An unmerged branch is evidence, not the final canonical state.

## Closeout Rule

Before closing any issue, add a final comment containing:

```markdown
## Final Closeout

**Resolution** -- What fixed it, one clear sentence.

**Verified** -- How it was confirmed working.

**Registry Updated** -- Yes / No / Not applicable.

**SOP Updated** -- Yes / No / Not applicable.

**Tech Updates Logged** -- Yes / No / Not applicable.

**Technical Record Updated** -- Yes / No / Not applicable.

**PR / Main Branch Status** -- Merged / PR open / Not applicable / intentionally unmerged with reason.

**Follow-up Needed** -- Any remaining risk or next steps.
```

Closed means done and verified. Do not close an issue that is only partially resolved.

## Applies To

This playbook applies to Victor, Manus, Cody, Ruby, and every other ZedBiz agent. The repo may change by agent or system, but the filing rules stay the same.

## Notion Reference

Technical Memory System: https://app.notion.com/p/397a3e33d581812fa9dcfcfa80e88fab
