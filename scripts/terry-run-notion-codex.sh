#!/usr/bin/env bash
# Terry-only bridge for governed Notion operations.
# Runs a discrete, authorized Notion task through the proven GPT-5.5 Codex route.
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <task-file> [session-suffix]" >&2
  exit 64
fi

TASK_FILE="$1"
SESSION_SUFFIX="${2:-$(date -u +%Y%m%dT%H%M%SZ)}"

if [[ ! -r "$TASK_FILE" ]]; then
  echo "Task file is not readable: $TASK_FILE" >&2
  exit 66
fi

TASK_TEXT="$(cat "$TASK_FILE")"
if [[ -z "${TASK_TEXT//[[:space:]]/}" ]]; then
  echo "Task file is empty: $TASK_FILE" >&2
  exit 65
fi

read -r -d '' ROUTE_POLICY <<'POLICY' || true
You are Terry's governed-Notion execution route. This turn is deliberately running through GPT-5.5 with the Codex runtime because it is the verified path to Codex Apps Notion tools.

Follow the workspace AGENTS.md and TOOLS.md policies exactly. For Notion work, use only Codex Apps Notion tools through Codex OAuth. If those tools are deferred, load them with tool_search before continuing. Do not call codex_endpoint_probe or codex_sessions_list as a Notion health check. Do not use ntn, NOTION_API_TOKEN, /app/skills/notion, or any standalone OpenClaw Notion fallback.

Honor the task's authorization boundary. Search before creating. For a mutation, refetch and verify the final parent, title, required properties, content, and relevant links. Return a concise evidence-based outcome with the verified Notion URL or an exact blocking error.
POLICY

exec openclaw agent \
  --agent main \
  --model openai/gpt-5.5 \
  --session-key "agent:main:codex-notion-${SESSION_SUFFIX}" \
  --timeout 600 \
  --json \
  --message "${ROUTE_POLICY}

AUTHORIZED TASK:
${TASK_TEXT}"
