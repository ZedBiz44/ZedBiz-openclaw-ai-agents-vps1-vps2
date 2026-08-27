#!/bin/sh

# Purpose: Keep the mandatory Z-Knowledge Small Bite gate inside the active
# OpenClaw AGENTS.md context for every approved VPS1 agent.
# Added by: Cody
# Date added: 2026-08-27 Mountain Time
# Tested on: VPS1, /opt/openclaw/agents
# Rollback: restore AGENTS.md from the reported
# /opt/openclaw/agents/{agent}/backups/zk-small-bite-gate-* directory.

set -eu

all_agents="amanda edith gohzed grogar inga maggie marsha terry victor vivian wilma"
agents="${*:-$all_agents}"
stamp="$(TZ=America/Edmonton date +%Y%m%d-%H%M%S-MDT)"
gate='- For Z-Knowledge research, load `z-small-bite-task` and use only the minimum meaningful bites required.'

for agent in $agents; do
  case " $all_agents " in
    *" $agent "*) ;;
    *) echo "Unknown VPS1 agent: $agent" >&2; exit 2 ;;
  esac

  agent_dir="/opt/openclaw/agents/$agent"
  agents_file="$agent_dir/workspace/AGENTS.md"
  case "$(realpath -m "$agents_file")" in
    "/opt/openclaw/agents/$agent/workspace/AGENTS.md") ;;
    *) echo "Unsafe AGENTS.md target: $agents_file" >&2; exit 2 ;;
  esac

  backup_name="zk-small-bite-gate-$stamp"
  docker run --rm \
    -e AGENT="$agent" \
    -e BACKUP_NAME="$backup_name" \
    -e GATE="$gate" \
    -v "$agent_dir:/target" \
    alpine sh -euc '
      source_file=/target/workspace/AGENTS.md
      test -f "$source_file"
      offset="$(awk -v needle="$GATE" "index(\$0, needle) { print total + index(\$0, needle) - 1; exit } { total += length(\$0) + 1 }" "$source_file")"
      if [ -n "$offset" ] && [ "$offset" -lt 20000 ]; then
        echo "$AGENT: gate already active at byte $offset"
        exit 0
      fi

      backup_dir="/target/backups/$BACKUP_NAME"
      temp_file=/target/workspace/.AGENTS.md.zk-gate.tmp
      mkdir -p "$backup_dir"
      cp -a "$source_file" "$backup_dir/AGENTS.md"
      awk -v gate="$GATE" "NR == 1 { print; print gate; next } { print }" "$source_file" > "$temp_file"
      mv "$temp_file" "$source_file"
      chown 1001:1001 "$source_file"
      new_offset="$(awk -v needle="$GATE" "index(\$0, needle) { print total + index(\$0, needle) - 1; exit } { total += length(\$0) + 1 }" "$source_file")"
      test -n "$new_offset"
      test "$new_offset" -lt 20000
      echo "$AGENT: gate active at byte $new_offset; backup=/opt/openclaw/agents/$AGENT/backups/$BACKUP_NAME/AGENTS.md"
    '
done
