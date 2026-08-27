#!/bin/sh

# Purpose: Deploy the canonical modular Z-Knowledge skill set to approved VPS1
# OpenClaw agents with exact-folder backups and path safety checks.
# Added by: Cody
# Date added: 2026-08-27 Mountain Time
# Tested on: VPS1, /opt/openclaw/agents
# Rollback: copy the selected skill folders from the reported
# /opt/openclaw/agents/{agent}/backups/zk-rollout-* directory back into the
# matching managed or workspace skill root, then restart and verify that agent.

set -eu

all_agents="amanda edith gohzed grogar inga maggie marsha terry victor vivian wilma"
skills="${ZK_SKILLS:-z-code-allocation z-knowledge-routing z-record-knowledge z-notion-knowledge-publish z-biz-plan z-small-bite-task z-wiki-research}"
staging="${ZK_STAGING_DIR:-/tmp/zk-rollout-20260827}"
agents="${*:-$all_agents}"
stamp="$(TZ=America/Edmonton date +%Y%m%d-%H%M%S-MDT)"

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
  for root in skills workspace/skills; do
    case "$(realpath -m "$agent_dir/$root")" in
      "/opt/openclaw/agents/$agent/skills"|"/opt/openclaw/agents/$agent/workspace/skills") ;;
      *) echo "Unsafe skill root: $agent_dir/$root" >&2; exit 2 ;;
    esac
  done

  backup_name="zk-rollout-$stamp"

  docker run --rm \
    -e BACKUP_NAME="$backup_name" \
    -e SKILLS="$skills" \
    -v "$agent_dir:/target" \
    -v "$staging:/source:ro" \
    alpine sh -euc '
      for root in skills workspace/skills; do
        mkdir -p "/target/$root"
        backup_root="/target/backups/$BACKUP_NAME/$root"
        mkdir -p "$backup_root"
        for skill in $SKILLS; do
          source_dir="/source/$skill"
          target_dir="/target/$root/$skill"
          test -f "$source_dir/SKILL.md"
          case "$target_dir" in
            /target/skills/*|/target/workspace/skills/*) ;;
            *) echo "Unsafe target: $target_dir" >&2; exit 2 ;;
          esac
          if [ -e "$target_dir" ]; then
            cp -a "$target_dir" "$backup_root/"
          fi
          rm -rf -- "$target_dir"
          cp -a "$source_dir" "$target_dir"
          chown -R 1001:1001 "$target_dir"
        done
      done
    '

  echo "$agent: deployed modular Z-Knowledge skills; backup=$agent_dir/backups/$backup_name"
done
