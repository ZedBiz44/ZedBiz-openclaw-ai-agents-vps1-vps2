# Hindsight Operation-Specific Model Routing Rollout

Date: 2026-09-16 | Agent: Cody | Status: Completed

## Scope

Updated the shared central Hindsight service without changing agent main models, memory banks, PostgreSQL data, automatic capture, or automatic recall.

## Approved Routing

- Retain: `openai/gpt-5.6-luna`, low reasoning
- Consolidation: `openai/gpt-5.6-luna`, low reasoning
- Reflect: `openai/gpt-oss-120b`, low reasoning
- Recall: `mid` by default; `high` for an explicitly comprehensive search
- Final decisions: each agent's main model

## Deployment Evidence

- Protected environment backed up before restart.
- `hindsight-central` recreated successfully and returned healthy.
- Runtime inspection confirmed all operation-specific variables.
- Read-only dry-run extraction returned HTTP 200 and one correctly structured fact.
- Live logs showed normal recall completing in about one second and reflection using GPT-OSS 120B.

## Rollback

Restore the timestamped protected environment backup and recreate `hindsight-central`. The database volume was not migrated or changed.

## Rocky

Rocky's separate VPS4 service uses `qwen/qwen3.6-35b-a3b`: reasoning off for retain and consolidation, and low reasoning for reflection.
