# VPS1 Central Hindsight Build and Model Routing

Date: 2026-09-16 | Agent: Cody | Status: Active

## Purpose

The upstream Hindsight 0.8.6 image contains the FlashRank provider code but does not install the optional `flashrank` package. This small derived image installs that dependency without changing Hindsight's application code.

The upstream base is pinned by digest. Version 0.8.6 adds security dependency updates and fixes for retain reliability, backup restore compatibility, stalled health diagnostics, worker recovery, and idempotent asynchronous retention. The ZedBiz image keeps the August 4 CPU tuning intact.

## VPS1 Performance Profile

- Four x86 Linux CPU cores
- No GPU or MPS acceleration
- FlashRank TinyBERT CPU reranker
- Fifty rerank candidates
- Four total worker slots
- One worker slot reserved for consolidation
- No FP16 setting because this host receives no useful acceleration from it

The August 4 live benchmark completed ten recalls with a 0.664-second average, 0.830-second 95th percentile, and 1.190-second maximum. Known-fact checks for Mountain Time, residence, and GitHub/Notion routing still returned matching results.

## Current Model Routing

- Retain and consolidation: `openai/gpt-5.6-luna`, low reasoning
- Reflection: `openai/gpt-oss-120b`, low reasoning
- Recall: Hindsight retrieval and reranking, normally the `mid` budget; use `high` for an explicitly comprehensive search
- Final answer or decision: the calling agent's main model, not Hindsight's extraction model

OpenRouter is the model gateway for the Hindsight service. It is not the model running the agents themselves.

## Deployment

The protected live environment file remains at `/opt/openclaw/services/hindsight/.env`. Never commit it or any API token.

Build and deploy from `/opt/openclaw/services/hindsight/build` with the external `hindsight-data` volume. Verify `/health`, direct recall quality, and an actual agent recall before removing the previous stopped container.

## Rollback

Stop the new `hindsight` container and restore the previous pinned image through the protected Compose and environment backups. The September 16 model routing is recorded in `ai-agent-sops/zedbiz-main-vps/tracking/2026-09-16-hindsight-operation-model-routing.md`.
