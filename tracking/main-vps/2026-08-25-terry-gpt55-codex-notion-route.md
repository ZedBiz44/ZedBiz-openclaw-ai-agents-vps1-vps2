# Terry GPT-5.5 Codex Notion Route

**Date:** 2026-08-25  
**Status:** Approved Terry-only remediation  
**Scope:** Governed Notion operations only

## Purpose

Terry's normal GPT-5.6 Sol route remains on the OpenClaw runtime to retain native execution and video capabilities. Governed Notion work is routed through GPT-5.5 on the Codex runtime because this route has proven Codex Apps Notion tool discovery and a successful live read-only Notion search.

## Root Cause

The August 23 video capability deployment changed Terry's GPT-5.6 Sol, Terra, and Luna models from the Codex runtime to the OpenClaw runtime. The OpenClaw runtime does not expose `tool_search`, which is required to load deferred Codex Apps Notion tools. A separate local Codex supervisor endpoint failure was incorrectly used as a Notion health check but is unrelated to the Codex Apps OAuth route.

GPT-5.6 deferred-tool discovery is also unavailable in a fresh Marsha Codex runtime session. Therefore, switching Terry's GPT-5.6 route back to Codex would not be a sufficiently proven remedy.

## Implementation

The tracked wrapper at `scripts/terry-run-notion-codex.sh` accepts an authorized task file and invokes a dedicated non-delivery Terry session with:

- Model: `openai/gpt-5.5`
- Runtime: Codex
- Session key prefix: `agent:main:codex-notion-`
- Required route: Codex Apps Notion through Codex OAuth only

The wrapper forbids use of `codex_endpoint_probe` and `codex_sessions_list` as Notion health checks and reiterates the existing prohibition against `ntn`, direct tokens, and standalone OpenClaw Notion fallbacks.

## Validation Boundary

The repair must prove, in this order:

- The wrapper can load the required deferred Codex Apps Notion tools.
- The required duplicate search completes through Codex Apps Notion.
- Terry's daily journal is created or updated only if the task's authorization permits it, then refetched and verified.
- GPT-5.6 Sol retains native video and execution tooling.

No changes to Vivian or any other agent are authorized by this remediation.

## Rollback

Remove the deployed workspace wrapper. No model defaults, provider credentials, Notion connections, supervisor settings, or container configuration are changed by this bridge.
