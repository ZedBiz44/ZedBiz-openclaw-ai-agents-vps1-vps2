# 2026-08-27 - Modular Z-Knowledge Fleet Rollout

## Summary

- **Date:** 2026-08-27 Mountain Time
- **Added By:** Cody
- **Agents:** Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, Wilma, Frank, Harry, Suzy, Ruby, and Rocky
- **Systems:** VPS1 OpenClaw, VPS2 OpenClaw, VPS3 Hermes, and VPS4 OpenClaw
- **Status:** Tested and complete

## Skill Purpose

Standardize the complete modular Z-Knowledge workflow, keep the Small Bite rule inside active agent context, preserve Brief versus Biz-Plan boundaries, and remove replaced legacy knowledge packages that could compete with the modular workflow.

## Canonical Source

- `z-code-allocation`: `2f170289d3f2edcc23151022df604c52a20f17d3`
- `z-knowledge-routing`: `c49b9f80d53d58c8701f69d6bdfc495c6b07e5d8`
- `z-record-knowledge`: `230cb46823fef6167fc9e1b9cfd54fa139e905db`
- `z-notion-knowledge-publish`: `d0948d97b912d81f3658ff5a6fa1deba0eaaefd9`
- `z-biz-plan`: `88ee54d41370e47647ed48abd4880b8c79479b5c`
- `z-small-bite-task`: `73c69c6a39b64cf72e04eee2e48fbd2c77509622`
- `z-wiki-research`: `3b8d41f8391d9764058a4e84d6cceeef5d5437fb`

Deployed `SKILL.md` SHA-256 prefixes, in the same order: `e5431a60`, `35c5a604`, `1f9d36f3`, `661c6cfa`, `bacf8bfc`, `83ecdff0`, and `8987ae71`.

## Files Added

- `ai-agent-sops/shared-scripts/deploy-vps1-zknowledge-skills.sh`
- `ai-agent-sops/shared-scripts/ensure-vps1-zknowledge-small-bite-gate.sh`
- `ai-agent-sops/shared-scripts/deploy-vps2-zknowledge-skills.sh`
- `ai-agent-sops/shared-scripts/deploy-ruby-zknowledge-skills.sh`
- `ai-agent-sops/shared-scripts/deploy-rocky-zknowledge-skills.sh`

## Deployment

### VPS1

- Terry passed first, then Marsha.
- All eleven agents received identical packages in both managed and workspace roots so OpenClaw precedence cannot select an older duplicate.
- The mandatory Small Bite rule is on line two or four of every active `AGENTS.md`, including Vivian.
- All eleven agents are healthy with restart count zero, `OOMKilled=false`, three GiB RAM, and four GiB combined RAM-plus-swap.

### VPS2

- Frank passed first, then Harry and Suzy.
- Modern packages were synchronized in both VPS2 skill roots.
- The following replaced packages were backed up and retired: `zedbiz-content-master-records`, `small-bite-wiki-research`, `zedbiz-knowledge-routing`, `zedbiz-notion-knowledge-publishing`, and `zedbiz-wiki-research`.
- All three services are active with zero restarts, no active legacy match, and the Small Bite gate on line two.

### Ruby / Hermes

- Installed all seven packages at `/opt/hermes-ruby/skills` with UID/GID `10000:10000`.
- Backed up and retired `request-z-code`.
- Restarted with `/usr/local/sbin/ruby-maintenance`; attributed change ID: `53830601-7929-4408-8372-0142ac58ffda`.
- API, chat, models, skills, channels, and system health passed. All seven skills are local and enabled.

### Rocky / OpenClaw

- Installed all seven packages at `/home/openclaw/.openclaw/workspace/skills` with UID/GID `1000:1000`.
- Added the Small Bite gate on line two and restarted Rocky's user gateway.
- Gateway, skill discovery, and local Hindsight health passed.

## Behaviour Tests

- Terry and Marsha passed fresh, non-mutating routing and read-only boundary tests.
- Frank passed both general routing and explicit autonomous-continuation tests after the correct VPS2 gateway environment was used.
- Ruby passed a normal no-preload Hermes test.
- Rocky passed explicit and normal fresh-session tests after the full Small Bite Skill was loaded.
- Successful tests kept review-only work read-only, used Brief as the factual foundation, used Biz-Plan as the execution layer, and did not treat bite boundaries as approval gates.

## Delivery Reliability

OpenClaw 2026.7.1 already supplies the required native SQLite delivery queue with idempotency keys, acknowledgement deletion, startup recovery, retry backoff, dead-letter handling, and health reporting. A duplicate custom outbox was not added.

The audit found forty-one historical failed outbound Discord entries across eight VPS1 agents. They range from 2026-06-16 through 2026-08-25 and predate this rollout. There were no pending entries and no failed session-queue entries. They were preserved because replaying partially delivered or permission-failed messages could create duplicates.

## Rollback

- VPS1 backups: `/opt/openclaw/agents/{agent}/backups/zk-rollout-*` and `zk-small-bite-gate-*`.
- VPS2 backups: `/root/.openclaw-{agent}/backups/zk-rollout-*`.
- Ruby backup: `/opt/hermes-ruby/backups/zk-rollout-20260827-165642-MDT`.
- Rocky backup: `/home/openclaw/.openclaw/backups/zk-rollout-20260827-170040-MDT`.
- Restore only the exact affected skill folders and `AGENTS.md`, restart through the verified platform route, then re-run hashes, discovery, health, and a fresh planning-only test.

## Links

- VPS1/VPS2 rollout: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/196
- Legacy migration: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/197
- Small Bite/controller review: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/191
- Ruby rollout: https://github.com/ZedBiz44/ZedBiz-hermes-ai-agents-vps3/issues/40
- Rocky rollout: https://github.com/ZedBiz44/ZedBiz-general-tech-issues-updates/issues/54
- Notion Technical Journal: https://app.notion.com/p/3c9a3e33d581811a914ef4395c0ad9ea
