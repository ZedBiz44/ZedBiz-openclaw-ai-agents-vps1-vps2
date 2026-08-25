# Terry and Vivian Permanent Combined-Tool Rollout

## Purpose

This rollout makes the tested Terry and Vivian Sol setup durable. GPT-5.6 Sol stays on the Codex runtime for normal work and governed Notion work. Approved OpenClaw tools are discovered only when needed for video and operations.

## Source-Controlled Components

| Path | Role |
|---|---|
| `policies/combined-tool-policy.md` | Shared normal-work and governed-tool policy |
| `agents/terry/combined-tool-override.json` | Minimal Terry Sol, Terra, and Luna mapping assertion |
| `agents/vivian/combined-tool-override.json` | Minimal Vivian Sol, Terra, and Luna mapping assertion |
| `scripts/apply_combined_tool_policy.js` | Backup, runtime assertion, and marked policy-block updater |
| `scripts/apply-agent-combined-tool-policy.sh` | Safe Terry or Vivian deployment entry point |
| `scripts/rollback-agent-combined-tool-policy.sh` | Exact configuration and instruction rollback entry point |

## Live Result

The policy is deployed as one marked block in each agent’s `workspace/AGENTS.md`. The updater writes a timestamped backup before a live configuration or instruction change. It only asserts these mappings:

| Model | Required runtime |
|---|---|
| GPT-5.6 Sol | Codex |
| GPT-5.6 Terra | OpenClaw |
| GPT-5.6 Luna | OpenClaw |

No full live configuration or credentials are committed. No other agent is changed.

## Verification

After deployment, verify the marked policy block, the three model mappings, agent health, and one fresh Sol read-only test with exact Codex Apps Notion fetch plus no-spend Percify model listing.
