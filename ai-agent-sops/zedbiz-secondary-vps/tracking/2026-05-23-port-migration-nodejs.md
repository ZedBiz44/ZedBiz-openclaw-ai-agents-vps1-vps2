# Session Log: Port Migration + Node.js SOP Update
**Date:** 2026-05-23
**Agent:** Manus
**Server:** VPS-2 (2.24.104.80)

## Actions Taken

### 1. Port Migration — Harry and Edith
- Harry migrated from port 18789 to **4000**
- Edith migrated from port 18790 to **4001**
- UFW updated: ports 4000 and 4001 opened
- Both services verified running and HTTP 200 on new ports

**New URLs:**
- Harry: http://2.24.104.80:4000
- Edith: http://2.24.104.80:4001

**Port Convention Established:**
- VPS-1 agents: 3000+
- VPS-2 agents: 4000+

### 2. Node.js 24 Added to Both SOPs
- Added Step 0.5 to both human-agent-base-build-sop and ai-agent-base-build-sop
- Step checks current Node.js version first
- If below v24, installs via NodeSource setup_24.x
- AI SOP version includes assertion check (PASS/FAIL)
- Human SOP version includes plain verify step
- Both SOPs updated in Notion

**Why Node.js 24:**
- OpenClaw 2026.x minimum: Node.js 22.19
- Recommended runtime: Node.js 24 (V8 optimizations for real-time AI agents)
- Current install on VPS-2: v24.15.0

## Notion Pages Updated
- human-agent-base-build-sop: https://www.notion.so/04ea3e33d5818318b4ae812c80a98da3
- ai-agent-base-build-sop: https://www.notion.so/3e4a3e33d5818352bdb701eed29da450
