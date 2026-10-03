#!/bin/bash
# =============================================================================
# OpenClaw Host-Level Email Poll Script
# /opt/openclaw/scripts/email-poll.sh
#
# Purpose: Poll each agent's inbox via himalaya (no LLM, zero token cost).
#          Only trigger an OpenClaw agent session if unread mail is found.
#
# Architecture: Host-Poll Email Triage
# - Runs as a Linux system cron (not OpenClaw cron)
# - Uses docker exec to run himalaya inside each agent container
# - himalaya connects directly to IMAP — no agent session, no LLM
# - If unread mail found: triggers isolated OpenClaw session on that agent
# - If inbox empty: exits silently, zero cost
#
# Usage: email-poll.sh <agent_name>
#   e.g. email-poll.sh terry
#
# Requirements:
#   - jq installed on host (apt install jq)
#   - himalaya installed inside each agent container
#   - Agent container must be running
# =============================================================================

AGENT="$1"

if [ -z "$AGENT" ]; then
  echo "Usage: $0 <agent_name>"
  exit 1
fi

LOG_DIR="/opt/openclaw/scripts/logs"
LOG_FILE="$LOG_DIR/email-poll-${AGENT}.log"
FLAG_FILE="/tmp/email-poll-${AGENT}-pending.json"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# --- Step 1: Check container is running ---
if ! docker ps --format "{{.Names}}" 2>/dev/null | grep -q "^${AGENT}$"; then
  echo "[$TIMESTAMP] SKIP: $AGENT container not running" >> "$LOG_FILE"
  exit 0
fi

# --- Step 2: Poll inbox via himalaya inside the container ---
# Uses "not flag seen" query — only unread messages
# --page-size 10 limits to 10 most recent unread messages
if docker exec "$AGENT" himalaya --version 2>/dev/null | grep -q '^himalaya v2\.'; then
  RESULT=$(docker exec "$AGENT" himalaya envelope search --mailbox INBOX --page-size 10 --json "not flag seen" 2>/dev/null)
else
  RESULT=$(docker exec "$AGENT" himalaya -o json envelope list --page-size 10 "not flag seen" 2>/dev/null)
fi
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
  echo "[$TIMESTAMP] ERROR: himalaya failed for $AGENT (exit $EXIT_CODE)" >> "$LOG_FILE"
  exit 1
fi

# --- Step 3: Check if any unread mail found ---
RESULT=$(printf '%s\n' "$RESULT" | jq -ce 'if type == "array" then . elif (.envelopes | type) == "array" then .envelopes else error("Invalid envelope response") end') || exit 1
COUNT=$(printf '%s\n' "$RESULT" | jq 'length')

# Maintenance proof: never schedule an agent or send a notification.
if [ "${EMAIL_POLL_CHECK_ONLY:-0}" = 1 ]; then
  printf 'Read-only inbox check passed for %s: %s unread envelopes\n' "$AGENT" "$COUNT"
  exit 0
fi

if [ -z "$COUNT" ] || [ "$COUNT" -eq 0 ]; then
  echo "[$TIMESTAMP] [NO ACTION] $AGENT inbox empty" >> "$LOG_FILE"
  exit 0
fi

# --- Step 4: Unread mail found — check if already pending ---
if [ -f "$FLAG_FILE" ]; then
  echo "[$TIMESTAMP] SKIP: $AGENT already has a pending email session (flag file exists)" >> "$LOG_FILE"
  exit 0
fi

# Save the unread envelope list for the agent to reference
echo "$RESULT" > "$FLAG_FILE"

echo "[$TIMESTAMP] MAIL FOUND: $COUNT unread message(s) for $AGENT — triggering agent session" >> "$LOG_FILE"

# --- Step 5: Trigger isolated OpenClaw agent session ---
# Uses --light-context (skills still load via TOOLS.md) + the agent's configured OAuth model
# Agent is instructed to summarize only — no action without Jack's approval
PROMPT="You have $COUNT unread email(s) in your inbox. Use the himalaya skill to list and read them. Summarize each message in 1-2 sentences (sender, subject, key point). Do NOT reply, delete, archive, or take any action. Just summarize and wait for Jack's instructions. If nothing requires attention, output exactly: [NO ACTION]"

# Victor uses node user
if [ "$AGENT" = "victor" ]; then
  docker exec -u node -e HOME=/home/node victor \
    openclaw cron add \
    --at "+5s" \
    --session isolated \
    --light-context \
    --timeout-seconds 120 \
    --message "$PROMPT" \
    --delete-after-run \
    2>/dev/null && echo "[$TIMESTAMP] Agent session triggered for $AGENT" >> "$LOG_FILE"
else
  docker exec "$AGENT" \
    openclaw cron add \
    --at "+5s" \
    --session isolated \
    --light-context \
    --timeout-seconds 120 \
    --message "$PROMPT" \
    --delete-after-run \
    2>/dev/null && echo "[$TIMESTAMP] Agent session triggered for $AGENT" >> "$LOG_FILE"
fi

# Remove flag file after triggering (agent will handle the mail)
rm -f "$FLAG_FILE"

exit 0
