# VPS1 Hindsight CPU Build

Date: 2026-08-04 | Agent: Cody | Status: Active

## Purpose

The upstream Hindsight 0.8.4 image contains the FlashRank provider code but does not install the optional `flashrank` package. This small derived image installs that dependency without changing Hindsight's application code.

## VPS1 Performance Profile

- Four x86 Linux CPU cores
- No GPU or MPS acceleration
- FlashRank TinyBERT CPU reranker
- Fifty rerank candidates
- Four total worker slots
- One worker slot reserved for consolidation
- No FP16 setting because this host receives no useful acceleration from it

The August 4 live benchmark completed ten recalls with a 0.664-second average, 0.830-second 95th percentile, and 1.190-second maximum. Known-fact checks for Mountain Time, residence, and GitHub/Notion routing still returned matching results.

## Deployment

The protected live environment file remains at `/opt/openclaw/services/hindsight/.env`. Never commit it or the API token.

Build and deploy from `/opt/openclaw/services/hindsight/build` with the external `hindsight-data` volume. Verify `/health`, direct recall quality, and an actual agent recall before removing the previous stopped container.

## Rollback

Stop the new `hindsight` container, rename the exact stopped pre-change container back to `hindsight`, restore the saved `.env`, and start it. The August 4 rollback snapshot is recorded in the related tracking file and GitHub Issue #109.
