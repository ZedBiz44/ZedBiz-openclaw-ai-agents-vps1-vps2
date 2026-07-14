# ZedBiz-openclaw-ai-agents-vps1-vps2

*(Formerly `zedbiz-ai-agents`)*

This repository is the operational home and technical source of truth for **OpenClaw agents running on VPS1 and VPS2**.

## 🤖 Agents Covered Here
Amanda, Victor, Marsha, Wilma, Edith, Inga, Gohzed, Grogar, Maggie, Terry, Vivian, Harry, Frank, Suzy

## 📋 The Technical Memory System
All technical work is tracked via GitHub Issues in this repository. Notion is for human-readable summaries only; GitHub is the working source of truth.

Canonical GitHub playbook: [docs/github-issue-filing-sop.md](docs/github-issue-filing-sop.md)

That SOP is the current operating rule for repo routing, search-before-create, required labels, issue body templates, parent issue/workstream handling, comment updates, PR/main-branch status, and closeout comments.

### The 6-Step Issue Filing Rule
Every agent (Victor, Manus, Cody, Ruby, and future agents) MUST follow this process for every task:

1. **Search first:** `gh issue list --search "[agent] [topic]" --state all --limit 10`
2. **If a matching issue exists:** Add a comment there. Do not create a duplicate.
3. **If no match exists:** Create a new issue in the correct repo.
4. **Use exact title format:** `YYYY-MM-DD | [Agent/Tool] | [Short description]`
5. **Apply required labels:** `agent:` when agent-specific, plus `system:`, `type:`, and `status:`.
6. **Closeout rule:** Never close an issue without a final comment stating the resolution, verification, documentation updates, and PR/main-branch status.

### Required Labels
Every issue MUST have the minimum labels that make it searchable:
- **Agent:** `agent:amanda`, `agent:victor`, `agent:marsha`, etc. when a specific agent is involved
- **System:** `system:1password`, `system:asana`, `system:lancedb`, `system:telegram`, etc.
- **Type:** `type:bug`, `type:config`, `type:integration`, `type:sop`, etc.
- **Status:** `status:open`, `status:blocked`, `status:resolved`

### Issue Body Template
When creating an issue, use the full template in [docs/github-issue-filing-sop.md](docs/github-issue-filing-sop.md), including:
- **What:** One sentence description
- **Agent / System Affected:** Name, VPS, platform
- **Search Performed:** Confirm you searched first
- **Related Existing Issues:** Link dependencies or `None found`
- **What Was Tried:** Bullet list
- **What Failed:** Record every failed attempt
- **What Worked:** The actual fix
- **What Changed:** Files edited, containers restarted, PRs or branches created
- **Next Action:** The next practical step

## 📁 Repository Structure
- `/registry/` - Per-agent registry files (the definitive config/status for each agent)
- `/sops/` - Standard Operating Procedures (VPS1, VPS2, etc.)
- `/docs/` - System documentation and planning files
- `docs/github-issue-filing-sop.md` - Canonical issue-recording playbook
- `INDEX.md` - The master pointer file for the entire system

## 🔒 Secret Rules
- NEVER commit API keys, OAuth tokens, passwords, or gateway tokens.
- Live secrets live only on the VPS in the `.env` files or 1Password vault.

---
*For the human-readable overview, refer to the [Technical Memory System Notion Page](https://app.notion.com/p/397a3e33d581812fa9dcfcfa80e88fab). GitHub SOPs remain the agent-facing technical source of truth.*
