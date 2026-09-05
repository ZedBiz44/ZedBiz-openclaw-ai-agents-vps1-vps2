#!/bin/sh

# Purpose: Deploy the canonical modular Z-Knowledge skill set to Rocky's
# OpenClaw workspace and keep the Small Bite gate inside active context.
# Added by: Cody
# Date added: 2026-08-27 Mountain Time
# Tested on: Rocky VPS4, /home/openclaw/.openclaw/workspace
# Recovery: redeploy the required version from its authoritative GitHub
# repository, restart the OpenClaw user gateway, and re-run discovery and
# health checks. Never retain server-side skill backups.

set -eu

base=/home/openclaw/.openclaw
skills="z-code-allocation z-knowledge-routing z-record-knowledge z-notion-knowledge-publish z-biz-plan z-small-bite-task z-wiki-research"
staging="${ZK_STAGING_DIR:-/tmp/zk-rollout-20260827}"
gate='- For Z-Knowledge research, load `z-small-bite-task` and use only the minimum meaningful bites required.'

case "$(realpath -m "$base/workspace/skills")" in
  /home/openclaw/.openclaw/workspace/skills) ;;
  *) echo "Unsafe Rocky skill root" >&2; exit 2 ;;
esac

case "$(realpath -m "$base/skills")" in
  /home/openclaw/.openclaw/skills) ;;
  *) echo "Unsafe Rocky managed skill root" >&2; exit 2 ;;
esac

case "$(realpath -m "$staging")" in
  /tmp/zk-rollout-*) ;;
  *) echo "Unsafe staging directory: $staging" >&2; exit 2 ;;
esac

for skill in $skills; do
  source_dir="$staging/$skill"
  target_dir="$base/workspace/skills/$skill"
  test -f "$source_dir/SKILL.md"
  rm -rf -- "$target_dir"
  cp -a "$source_dir" "$target_dir"
  chown -R 1000:1000 "$target_dir"
  rm -rf -- "$base/skills/$skill"
done

offset="$(awk -v needle="$gate" 'index($0, needle) { print total + index($0, needle) - 1; exit } { total += length($0) + 1 }' "$base/workspace/AGENTS.md")"
if [ -z "$offset" ] || [ "$offset" -ge 20000 ]; then
  temp_file="$base/workspace/.AGENTS.md.zk-gate.tmp"
  awk -v gate="$gate" 'NR == 1 { print; print gate; next } { print }' "$base/workspace/AGENTS.md" > "$temp_file"
  mv "$temp_file" "$base/workspace/AGENTS.md"
  chown 1000:1000 "$base/workspace/AGENTS.md"
fi

new_offset="$(awk -v needle="$gate" 'index($0, needle) { print total + index($0, needle) - 1; exit } { total += length($0) + 1 }' "$base/workspace/AGENTS.md")"
test -n "$new_offset"
test "$new_offset" -lt 20000

echo "rocky: deployed modular Z-Knowledge skills; gate byte=$new_offset; recovery=GitHub"
