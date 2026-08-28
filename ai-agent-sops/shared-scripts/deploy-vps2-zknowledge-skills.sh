#!/bin/sh

# Purpose: Deploy the canonical modular Z-Knowledge skill set to approved VPS2
# OpenClaw agents, keep the Small Bite gate in active context, and optionally
# retire the conflicting legacy content-master skill after backup.
# Added by: Cody
# Date added: 2026-08-27 Mountain Time
# Tested on: VPS2, /root/.openclaw-{agent}
# Rollback: restore skills and AGENTS.md from the reported
# /root/.openclaw-{agent}/backups/zk-rollout-* directory, then restart and
# verify the affected openclaw-{agent}.service.

set -eu

all_agents="frank harry suzy"
skills="${ZK_SKILLS:-z-code-allocation z-knowledge-routing z-record-knowledge z-notion-knowledge-publish z-biz-plan z-small-bite-task z-wiki-research}"
legacy_skills="small-bite-wiki-research zedbiz-knowledge-routing zedbiz-notion-knowledge-publishing zedbiz-wiki-research"
staging="${ZK_STAGING_DIR:-/tmp/zk-rollout-20260827}"
retire_legacy="${RETIRE_LEGACY:-0}"
agents="${*:-$all_agents}"
stamp="$(TZ=America/Edmonton date +%Y%m%d-%H%M%S-MDT)"
gate='- For Z-Knowledge research, load `z-small-bite-task` and use only the minimum meaningful bites required.'

case "$(realpath -m "$staging")" in
  /tmp/zk-rollout-*) ;;
  *) echo "Unsafe staging directory: $staging" >&2; exit 2 ;;
esac

case "$retire_legacy" in
  0|1) ;;
  *) echo "RETIRE_LEGACY must be 0 or 1" >&2; exit 2 ;;
esac

for skill in $skills; do
  test -f "$staging/$skill/SKILL.md" || {
    echo "Missing staged skill: $staging/$skill/SKILL.md" >&2
    exit 1
  }
done

for agent in $agents; do
  case " $all_agents " in
    *" $agent "*) ;;
    *) echo "Unknown VPS2 agent: $agent" >&2; exit 2 ;;
  esac

  base="/root/.openclaw-$agent"
  backup="$base/backups/zk-rollout-$stamp"
  agents_file="$base/workspace/AGENTS.md"

  for root in workspace/skills .openclaw/skills; do
    case "$(realpath -m "$base/$root")" in
      "/root/.openclaw-$agent/workspace/skills"|"/root/.openclaw-$agent/.openclaw/skills") ;;
      *) echo "Unsafe skill root: $base/$root" >&2; exit 2 ;;
    esac
    mkdir -p "$base/$root" "$backup/$root"

    for skill in $skills; do
      source_dir="$staging/$skill"
      target_dir="$base/$root/$skill"
      if [ -e "$target_dir" ]; then
        cp -a "$target_dir" "$backup/$root/"
      fi
      rm -rf -- "$target_dir"
      cp -a "$source_dir" "$target_dir"
    done

    if [ "$retire_legacy" = 1 ]; then
      for legacy_skill in $legacy_skills; do
        legacy_dir="$base/$root/$legacy_skill"
        if [ -e "$legacy_dir" ]; then
          mkdir -p "$backup/legacy/$root"
          cp -a "$legacy_dir" "$backup/legacy/$root/"
          rm -rf -- "$legacy_dir"
        fi
      done
    fi
  done

  test -f "$agents_file"
  cp -a "$agents_file" "$backup/AGENTS.md"
  offset="$(awk -v needle="$gate" 'index($0, needle) { print total + index($0, needle) - 1; exit } { total += length($0) + 1 }' "$agents_file")"
  if [ -z "$offset" ] || [ "$offset" -ge 20000 ]; then
    temp_file="$base/workspace/.AGENTS.md.zk-gate.tmp"
    awk -v gate="$gate" 'NR == 1 { print; print gate; next } { print }' "$agents_file" > "$temp_file"
    mv "$temp_file" "$agents_file"
  fi

  new_offset="$(awk -v needle="$gate" 'index($0, needle) { print total + index($0, needle) - 1; exit } { total += length($0) + 1 }' "$agents_file")"
  test -n "$new_offset"
  test "$new_offset" -lt 20000

  echo "$agent: deployed modular Z-Knowledge skills; gate byte=$new_offset; legacy-retired=$retire_legacy; backup=$backup"
done
