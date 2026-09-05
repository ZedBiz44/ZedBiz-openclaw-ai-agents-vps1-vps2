#!/bin/sh

# Purpose: Deploy the canonical modular Z-Knowledge skill set to approved VPS2
# OpenClaw agents, keep the Small Bite gate in active context, and optionally
# retire the conflicting legacy content-master skill without server backups.
# Added by: Cody
# Date added: 2026-08-27 Mountain Time
# Tested on: VPS2, /root/.openclaw-{agent}
# Recovery: redeploy the required version from its authoritative GitHub
# repository. Never retain server-side backup or retired copies of skills.

set -eu

all_agents="frank harry suzy"
skills="${ZK_SKILLS:-z-code-allocation z-knowledge-routing z-record-knowledge z-notion-knowledge-publish z-biz-plan z-small-bite-task z-wiki-research}"
legacy_skills="small-bite-wiki-research zedbiz-knowledge-routing zedbiz-notion-knowledge-publishing zedbiz-wiki-research"
staging="${ZK_STAGING_DIR:-/tmp/zk-rollout-20260827}"
retire_legacy="${RETIRE_LEGACY:-0}"
agents="${*:-$all_agents}"
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
  agents_file="$base/workspace/AGENTS.md"

  workspace_skills="$base/workspace/skills"
  managed_skills="$base/skills"
  legacy_nested_skills="$base/.openclaw/skills"
  case "$(realpath -m "$workspace_skills")" in
    "/root/.openclaw-$agent/workspace/skills") ;;
    *) echo "Unsafe workspace skill root: $workspace_skills" >&2; exit 2 ;;
  esac
  case "$(realpath -m "$managed_skills")" in
    "/root/.openclaw-$agent/skills") ;;
    *) echo "Unsafe managed skill root: $managed_skills" >&2; exit 2 ;;
  esac
  case "$(realpath -m "$legacy_nested_skills")" in
    "/root/.openclaw-$agent/.openclaw/skills") ;;
    *) echo "Unsafe legacy nested skill root: $legacy_nested_skills" >&2; exit 2 ;;
  esac
  mkdir -p "$workspace_skills" "$managed_skills" "$legacy_nested_skills"

  for skill in $skills; do
    source_dir="$staging/$skill"
    target_dir="$workspace_skills/$skill"
    temp_dir="$workspace_skills/.${skill}.deploy.$$"
    rm -rf -- "$temp_dir"
    cp -a "$source_dir" "$temp_dir"
    rm -rf -- "$target_dir"
    mv "$temp_dir" "$target_dir"
    rm -rf -- "$managed_skills/$skill" "$legacy_nested_skills/$skill"
  done

  if [ "$retire_legacy" = 1 ]; then
    for legacy_skill in $legacy_skills; do
      rm -rf -- \
        "$workspace_skills/$legacy_skill" \
        "$managed_skills/$legacy_skill" \
        "$legacy_nested_skills/$legacy_skill"
    done
  fi

  test -f "$agents_file"
  offset="$(awk -v needle="$gate" 'index($0, needle) { print total + index($0, needle) - 1; exit } { total += length($0) + 1 }' "$agents_file")"
  if [ -z "$offset" ] || [ "$offset" -ge 20000 ]; then
    temp_file="$base/workspace/.AGENTS.md.zk-gate.tmp"
    awk -v gate="$gate" 'NR == 1 { print; print gate; next } { print }' "$agents_file" > "$temp_file"
    mv "$temp_file" "$agents_file"
  fi

  new_offset="$(awk -v needle="$gate" 'index($0, needle) { print total + index($0, needle) - 1; exit } { total += length($0) + 1 }' "$agents_file")"
  test -n "$new_offset"
  test "$new_offset" -lt 20000

  echo "$agent: deployed modular Z-Knowledge skills; gate byte=$new_offset; legacy-retired=$retire_legacy; recovery=GitHub"
done
