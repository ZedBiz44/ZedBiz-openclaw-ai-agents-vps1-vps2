# ZedBiz-openclaw-ai-agents-vps1-vps2

*(Formerly `zedbiz-ai-agents`)*

This repository is the operational home and technical source of truth for **OpenClaw agents running on VPS1 and VPS2**.

## 🤖 Agents Covered Here
Amanda, Victor, Marsha, Wilma, Edith, Inga, Gohzed, Grogar, Maggie, Terry, Vivian, Harry, Frank, Suzy

## Technical records and operating instructions

GitHub holds technical implementation and work history for this repository. The maintained [technical filing rules](https://www.notion.so/397a3e33d581812fa9dcfcfa80e88fab) and [agent journal responsibilities](https://www.notion.so/3e6a3e33d58181e28f6ad2eaf534caf3) are in Notion.

Technical recording applies to Cody, Manus, Victor, and Ruby when doing technical work. Every agent keeps a daily work journal; ordinary agents have no routine GitHub technical-record or Tech Updates duty. SOPs, prompts, and their review workflows are maintained in Notion only.

## 📁 Repository Structure
- `/registry/` - Per-agent registry files (the definitive config/status for each agent)
- `/sops/` - Historical material; use the maintained Notion SOPs for current instructions
- `/docs/` - System documentation and planning files
- `docs/github-issue-filing-sop.md` - Pointer to maintained Notion filing rules
- `INDEX.md` - The master pointer file for the entire system

## 🔒 Secret Rules
- NEVER commit API keys, OAuth tokens, passwords, or gateway tokens.
- Live secrets live only on the VPS in the `.env` files or 1Password vault.

---
Maintained operating guidance: [Technical Memory System](https://www.notion.so/397a3e33d581812fa9dcfcfa80e88fab).
