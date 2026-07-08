# ZedBiz-openclaw-ai-agents-vps1-vps2

*(Formerly `zedbiz-ai-agents`)*

This repository is the operational home and technical source of truth for **OpenClaw agents running on VPS1 and VPS2**.

## 🤖 Agents Covered Here
Amanda, Victor, Marsha, Wilma, Edith, Inga, Gohzed, Grogar, Maggie, Terry, Vivian, Harry, Frank, Suzy

## 📋 The Technical Memory System
All technical work is tracked via GitHub Issues in this repository. Notion is for human-readable summaries only; GitHub is the working source of truth.

### The 6-Step Issue Filing Rule
Every agent (Manus, Cody, Ruby) MUST follow this process for every task:

1. **Search first:** `gh issue list --search "[agent] [topic]" --state all --limit 10`
2. **If a matching issue exists:** Add a comment there. Do not create a duplicate.
3. **If no match exists:** Create a new issue in this repo.
4. **Use exact title format:** `YYYY-MM-DD | [Agent/Tool] | [Short description]`
5. **Apply all 4 required labels:** `agent:`, `system:`, `type:`, `status:`
6. **Closeout rule:** Never close an issue without a final comment stating the Resolution and what was Verified.

### Required Labels
Every issue MUST have at least one label from each of these four categories:
- **Agent:** `agent:amanda`, `agent:victor`, `agent:marsha`, etc.
- **System:** `system:1password`, `system:asana`, `system:lancedb`, `system:telegram`, etc.
- **Type:** `type:bug`, `type:config`, `type:integration`, `type:sop`, etc.
- **Status:** `status:open`, `status:blocked`, `status:resolved`

### Issue Body Template
When creating an issue, use this structure:
- **What:** One sentence description
- **Agent / System Affected:** Name, VPS, platform
- **Search Performed:** Confirm you searched first
- **What Was Tried:** Bullet list
- **What Failed:** Record every failed attempt (crucial for future agents)
- **What Worked:** The actual fix
- **What Changed:** Files edited, containers restarted

## 📁 Repository Structure
- `/registry/` - Per-agent registry files (the definitive config/status for each agent)
- `/sops/` - Standard Operating Procedures (VPS1, VPS2, etc.)
- `/docs/` - System documentation and planning files
- `INDEX.md` - The master pointer file for the entire system

## 🔒 Secret Rules
- NEVER commit API keys, OAuth tokens, passwords, or gateway tokens.
- Live secrets live only on the VPS in the `.env` files or 1Password vault.

---
*For the complete GitHub Issue Filing Rules, refer to the [Technical Memory System Notion Page](https://app.notion.com/p/397a3e33d581812fa9dcfcfa80e88fab).*
