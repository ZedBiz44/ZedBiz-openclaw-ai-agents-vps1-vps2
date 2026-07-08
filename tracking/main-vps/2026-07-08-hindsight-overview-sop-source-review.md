# 2026-07-08 - Hindsight Overview SOP and Source Review

Date: 2026-07-08 Mountain Time
Agent: Cody
Status: Completed

## Scope

Created a business-readable Hindsight overview and memory-provider SOP in Notion under the `AI-Agent-Memory-Provider` hub, inside the `Memory Provider SOP's` section.

## Notion Record

- Hub page: https://app.notion.com/p/393a3e33d5818070ad0af83819192729
- New SOP page: https://app.notion.com/p/397a3e33d58181598308f6e2b9637cd5
- Page title: `Hindsight Overview and Memory Provider SOP`

## Verified Source Links

- Official Hindsight docs: https://hindsight.vectorize.io/
- Official OpenClaw Hindsight integration: https://hindsight.vectorize.io/sdks/integrations/openclaw
- Official GitHub repo: https://github.com/vectorize-io/hindsight
- Official Hindsight Docker image referenced by repo/docs: `ghcr.io/vectorize-io/hindsight:latest`
- Official OpenClaw plugin package: `@vectorize-io/hindsight-openclaw`
- OpenClaw plugin operations docs: https://docs.openclaw.ai/tools/plugin
- Current GitHub limitation to track: https://github.com/vectorize-io/hindsight/issues/963

## Source Review Summary

- Hindsight is the Vectorize agent-memory system, not the unrelated GTM/revenue-data product using the same name.
- The official OpenClaw path is `@vectorize-io/hindsight-openclaw`.
- The plugin supports automatic recall before prompt build and automatic retain after agent turns.
- Official docs describe Cloud, External API, and Embedded daemon setup modes.
- Official docs list `hindsightApiUrl`, `hindsightApiToken`, `dynamicBankId`, `bankId`, `autoRecall`, `autoRetain`, `retainRoles`, `recallBudget`, `recallMaxTokens`, `recallTopK`, `recallTypes`, and bank mission/default settings as key configuration controls.
- OpenClaw plugin docs say runtime inspection is the proof point, not cold config alone.
- GitHub issue #963 says `hindsight-openclaw` works as an active retain/recall plugin, but does not currently export OpenClaw `publicArtifacts` for Memory Wiki bridge import.

## ZedBiz Operating Decisions Captured

- Hindsight remains live working memory.
- Memory Wiki and GitHub/local Markdown remain durable reviewed source-of-truth layers.
- Notion remains the business-readable operations layer.
- Current ZedBiz Hindsight banks:
  - `internet-marketing`: Inga and Suzy.
  - `ghl`: GohZed and Grogar.
  - `zedbiz-shared`: Marsha, Maggie, Frank, and Ruby.
- Active provider truth comes from live `plugins.slots.memory`, not from the mere presence of configured plugin entries.
- For VPS1 private Docker access through `http://hindsight:8888`, do not add `hindsightApiToken` unless the Hindsight API route actually requires a token and the matching runtime secret exists.
- For cross-VPS access through `https://marsha.zbiz.ca/hindsight-api`, keep the secured token/proxy pattern.
- Hindsight should store useful working context and pointers to canonical docs, not full SOPs or raw logs.

## SOP Sections Created

- Source check.
- What Hindsight does.
- How Hindsight works.
- Current ZedBiz Hindsight banks.
- Key settings and recommended configuration.
- SOP to edit settings safely.
- SOP to evaluate Hindsight quality.
- SOP to make proper adjustments.
- Review rhythm.
- ZedBiz operating rule separating working memory from reviewed source-of-truth systems.

## Notes

- The Notion enhanced markdown resource URI failed earlier in this workspace with an invalid URL response, so the page was created with conservative Notion Markdown.
- The `Agent-Memory` local folder had a `.git` directory but did not behave as a usable Git repository from this shell. This record was added to the existing `ZedBiz44/zedbiz-ai-agents` tracking repo instead, matching prior Hindsight records.
