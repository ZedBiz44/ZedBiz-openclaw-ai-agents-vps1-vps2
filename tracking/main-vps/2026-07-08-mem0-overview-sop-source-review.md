# Mem0 Overview SOP and Source Review

date: 2026-07-08 | agent: Cody | status: Logged

## Summary

Created a Mem0 overview and operating SOP page under the AI-Agent-Memory-Provider Notion page, inside the `Memory Provider SOP's` section.

## Notion Page

- Parent: `AI-Agent-Memory-Provider`
- SOP page: `https://app.notion.com/p/397a3e33d58181b59067f715e447dd9b`

## Source Documents Reviewed

- OpenClaw memory CLI: `https://docs.openclaw.ai/cli/memory`
- OpenClaw memory overview: `https://docs.openclaw.ai/concepts/memory`
- OpenClaw dreaming: `https://docs.openclaw.ai/concepts/dreaming`
- Installed OpenClaw source on Terry: `/app/extensions/memory-core/src/cli.ts`
- Installed OpenClaw docs on Terry: `/app/docs/cli/memory.md`, `/app/docs/concepts/memory.md`, `/app/docs/concepts/dreaming.md`
- Mem0 docs home: `https://docs.mem0.ai/introduction`
- Mem0 open-source overview: `https://docs.mem0.ai/open-source/overview`
- Mem0 configuration: `https://docs.mem0.ai/open-source/configuration`
- Mem0 self-hosted setup: `https://docs.mem0.ai/open-source/setup`
- Mem0 Qdrant config: `https://docs.mem0.ai/components/vectordbs/dbs/qdrant`
- Mem0 OSS migration guide: `https://docs.mem0.ai/migration/oss-v2-to-v3`
- Mem0 GitHub repo: `https://github.com/mem0ai/mem0`

## Key Clarification

- OpenClaw `memory rem-harness` and `memory rem-backfill` are real OpenClaw `memory-core` dreaming/backfill commands.
- They backfill grounded historical daily notes into `DREAMS.md` and optionally stage candidates into the short-term promotion store.
- They do not prove Mem0 automatically imported every old SQLite or Markdown memory.
- For agents whose active memory slot is `openclaw-mem0`, `memory-core` may be present in config but disabled as the active memory slot.

## ZedBiz Mem0 Runtime Notes

- Terry and Edith use VPS1 Qdrant directly: `http://187.77.210.223:6333`.
- Harry uses the HTTPS Qdrant proxy: `https://marsha.zbiz.ca/qdrant-api`.
- All three use collection `mem0_vps1_agents` and user ID `zedbiz-vps1`.
- Recommended current settings were documented in the SOP: `topK=5`, `searchThreshold=0.1`, `tokenBudget=1500`, `text-embedding-3-small`, LLM temperature `0.2`, `autoCapture=true`, and `autoRecall=true`.
