# Guide Change Log

Use this file for human-readable summaries of meaningful SOP changes. Git commits hold the exact technical diff; this file explains the operating reason.

---

### 2026-06-02 - Edith (VPS2): Phase 1 Install Complete

- **Agent:** Manus AI
- **Problem:** New agent Edith needed to be installed on VPS2 following the Phase 1.1 SOP.
- **Fix:** Full Phase 1 install: npm install into /opt/openclaw-edith, systemd service on port 4300, Caddy routing for edith.zbiz.ca, 1Password injection, memory/wiki setup, Codex OAuth (Path A copy from Harry).
- **Test Result:** HTTPS 200 at edith.zbiz.ca, memory dreaming confirmed (0 2 * * * America/Edmonton), wiki vault ready, Codex OAuth active (expires 2026-06-06).
- **Related Links:** tracking/edith-phase1-install-2026-06-02.md

### 2026-06-02 - VPS2 Phase 1.1 SOP: Curated Model List Added

- **Agent:** Manus AI
- **Problem:** Edith's model dropdown showed 100+ junk models (GPT-5.4 Pro, o1, o3, o4-mini, etc.) after Phase 1 install. Root cause: SOP template used a bare `model:` string instead of the full `agents.defaults.models` curated allowlist.
- **Fix:** Added Step 12 assertion to verify curated model list is in openclaw.json. Template now copies Harry's full `agents.defaults` block (63 models, primary: openai/gpt-5.5). Applied live fix to Edith.
- **Test Result:** Harry=63, Suzy=63, Edith=63 models. Zero diff. Dropdown identical across all three agents.
- **Related Links:** Notion ai-agent-base-build-sop (3e4a3e33), Notion human-agent-base-build-sop (04ea3e33), tracking/2026-06-02-vps2-sop-corrections.md

### 2026-06-02 - VPS2 Phase 1.1 SOP: Missing Steps Restored

- **Agent:** Manus AI
- **Problem:** A previous `replace_content` operation wiped most of both VPS2 Phase 1.1 SOP pages in Notion, leaving only 2 steps. Jack restored from backup but memory/wiki steps were missing.
- **Fix:** Added Step 5b (codex/discord plugin install), Step 6c (pre-seed workspace files), Step 12b (memory/wiki setup with 3 sub-steps), Step 16 (GitHub tracking note) to both agent and human SOPs. Updated Done-When checklist to reflect actual model config.
- **Test Result:** All 6 key checks passed on both Notion pages after update.
- **Related Links:** Notion ai-agent-base-build-sop (3e4a3e33), Notion human-agent-base-build-sop (04ea3e33), tracking/2026-06-02-vps2-sop-corrections.md

### 2026-06-02 - VPS1 Phase 1.1 SOP: Memory/Wiki Steps Added

- **Agent:** Manus AI
- **Problem:** VPS1 Phase 1.1 SOPs (both agent and human versions) were missing the memory and wiki setup steps. Same gap as VPS2 -- previous update had wiped them.
- **Fix:** Added Step 12 (agent SOP) and Step 12b (human SOP) for memory/wiki setup using `update_content` surgical insert. Method: search-and-replace insert, NOT replace_content. All existing steps preserved.
- **Test Result:** 8/8 checks on agent SOP, 10/10 on human SOP. All original steps intact.
- **Related Links:** Notion ai-agent-base-build-sop (c3fa3e33), Notion human-agent-base-build-sop (287a3e33), tracking/2026-06-02-vps1-sop-memory-wiki-addition.md

### 2026-06-01 - Standard AGENTS.MD Template

- **Agent:** Manus
- **Problem:** Draft template (v2026.6.1-draft) had no Skills reference, a buried customization checklist, no authority conflict rule, and passive startup rules.
- **Fix:** Reviewed two versions. Concise version (v2026.6.1-concise) addressed most gaps. Remaining recommendations: add Skills discovery method and restore authority conflict rule.
- **Test Result:** Template reviewed live against Notion page. Gaps documented. Template marked Current in Notion.
- **Related Links:** Notion 372a3e33d581814fb813cd0ff647579d, docs/2026-06-01-standard-agents-md-template.md

### 2026-06-01 - Standard TOOLS.MD Template (Review Session)

- **Agent:** Manus
- **Problem:** Three versions reviewed. First version was a policy doc with no actual tool map content, citation artifacts, and no Skills reference. Later versions improved significantly with Tactical Economy doctrine, Final Tool Action Filter, and Look-Before-Leap Protocol.
- **Fix:** Feedback delivered on each version. Key remaining gaps: no filled-in example tool entry, Skills invoke path still a placeholder in v2026.6.1-general-3.
- **Test Result:** Template reviewed live against Notion page across three passes. Gaps documented per version.
- **Related Links:** Notion 372a3e33d581817e8ca4f7cd1e2541bf, docs/2026-06-01-standard-tools-md-template.md

---

## Change Entry Template

### YYYY-MM-DD - Guide Name

- **Agent:** Cody, Manus, OpenClaw agent name, or human name
- **Problem:** What failed or caused confusion
- **Fix:** What changed in the guide
- **Test Result:** What was checked after the change
- **Related Links:** GitHub issue, Notion page, VPS agent, or commit
