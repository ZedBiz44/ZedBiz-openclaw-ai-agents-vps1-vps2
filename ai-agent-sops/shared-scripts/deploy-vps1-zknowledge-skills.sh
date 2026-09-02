#!/bin/sh

# Purpose: Deploy the canonical modular Z-Knowledge skill set to approved VPS1
# OpenClaw agents with one canonical managed copy and path safety checks.
# Added by: Cody
# Date added: 2026-08-27 Mountain Time
# Tested on: VPS1, /opt/openclaw/agents
# Recovery: redeploy the required version from its authoritative GitHub
# repository. Never retain server-side backup or retired copies of skills.

set -eu

all_agents="amanda edith gohzed grogar inga maggie marsha terry victor vivian wilma"
skills="${ZK_SKILLS:-z-code-allocation z-knowledge-routing z-record-knowledge z-notion-knowledge-publish z-biz-plan z-small-bite-task z-wiki-research}"
staging="${ZK_STAGING_DIR:-/tmp/zk-rollout-20260827}"
agents="${*:-$all_agents}"

case "$(realpath -m "$staging")" in
  /tmp/zk-rollout-*) ;;
  *) echo "Unsafe staging directory: $staging" >&2; exit 2 ;;
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
    *) echo "Unknown VPS1 agent: $agent" >&2; exit 2 ;;
  esac

  agent_dir="/opt/openclaw/agents/$agent"
  case "$(realpath -m "$agent_dir/skills")" in
    "/opt/openclaw/agents/$agent/skills") ;;
    *) echo "Unsafe skill root: $agent_dir/skills" >&2; exit 2 ;;
  esac
  case "$(realpath -m "$agent_dir/workspace/skills")" in
    "/opt/openclaw/agents/$agent/workspace/skills") ;;
    *) echo "Unsafe workspace skill root: $agent_dir/workspace/skills" >&2; exit 2 ;;
  esac

  docker run --rm \
    -e SKILLS="$skills" \
    -v "$agent_dir:/target" \
    -v "$staging:/source:ro" \
    alpine sh -euc '
      mkdir -p /target/skills /target/workspace/skills
      for skill in $SKILLS; do
        source_dir="/source/$skill"
        target_dir="/target/skills/$skill"
        temp_dir="/target/skills/.${skill}.deploy.$$"
        workspace_duplicate="/target/workspace/skills/$skill"
        test -f "$source_dir/SKILL.md"
        case "$target_dir" in /target/skills/*) ;; *) exit 2 ;; esac
        case "$workspace_duplicate" in /target/workspace/skills/*) ;; *) exit 2 ;; esac
        rm -rf -- "$temp_dir"
        cp -a "$source_dir" "$temp_dir"
        chown -R 1001:1001 "$temp_dir"
        rm -rf -- "$target_dir"
        mv "$temp_dir" "$target_dir"
        rm -rf -- "$workspace_duplicate"
      done
    '

  echo "$agent: deployed modular Z-Knowledge skills to managed root; workspace duplicates removed; recovery=GitHub"
done
