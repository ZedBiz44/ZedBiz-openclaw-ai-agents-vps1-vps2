#!/bin/sh

# Purpose: Deploy the canonical modular Z-Knowledge skill set to Ruby/Hermes,
# keep the Small Bite gate near the start of AGENTS.md, and retire the replaced
# request-z-code package after backup.
# Added by: Cody
# Date added: 2026-08-27 Mountain Time
# Tested on: Ruby VPS3, /opt/hermes-ruby
# Rollback: restore skills and AGENTS.md from the reported
# /opt/hermes-ruby/backups/zk-rollout-* directory, then restart with
# /usr/local/sbin/ruby-maintenance and re-run Hermes discovery and health.

set -eu

base=/opt/hermes-ruby
skills="z-code-allocation z-knowledge-routing z-record-knowledge z-notion-knowledge-publish z-biz-plan z-small-bite-task z-wiki-research"
staging="${ZK_STAGING_DIR:-/tmp/zk-rollout-20260827}"
stamp="$(TZ=America/Edmonton date +%Y%m%d-%H%M%S-MDT)"
backup="$base/backups/zk-rollout-$stamp"
gate='- For Z-Knowledge research, load `z-small-bite-task` and use only the minimum meaningful bites required.'

case "$(realpath -m "$base/skills")" in
  /opt/hermes-ruby/skills) ;;
  *) echo "Unsafe Ruby skill root" >&2; exit 2 ;;
esac

case "$(realpath -m "$staging")" in
  /tmp/zk-rollout-*) ;;
  *) echo "Unsafe staging directory: $staging" >&2; exit 2 ;;
esac

mkdir -p "$backup/skills"
cp -a "$base/AGENTS.md" "$backup/AGENTS.md"

for skill in $skills; do
  source_dir="$staging/$skill"
  target_dir="$base/skills/$skill"
  test -f "$source_dir/SKILL.md"
  if [ -e "$target_dir" ]; then
    cp -a "$target_dir" "$backup/skills/"
  fi
  rm -rf -- "$target_dir"
  cp -a "$source_dir" "$target_dir"
  chown -R 10000:10000 "$target_dir"
done

legacy_dir="$base/skills/request-z-code"
if [ -e "$legacy_dir" ]; then
  mkdir -p "$backup/legacy"
  cp -a "$legacy_dir" "$backup/legacy/"
  rm -rf -- "$legacy_dir"
fi

offset="$(awk -v needle="$gate" 'index($0, needle) { print total + index($0, needle) - 1; exit } { total += length($0) + 1 }' "$base/AGENTS.md")"
if [ -z "$offset" ] || [ "$offset" -ge 20000 ]; then
  temp_file="$base/.AGENTS.md.zk-gate.tmp"
  awk -v gate="$gate" 'NR == 1 { print; print gate; next } { print }' "$base/AGENTS.md" > "$temp_file"
  mv "$temp_file" "$base/AGENTS.md"
  chown 10000:10000 "$base/AGENTS.md"
fi

new_offset="$(awk -v needle="$gate" 'index($0, needle) { print total + index($0, needle) - 1; exit } { total += length($0) + 1 }' "$base/AGENTS.md")"
test -n "$new_offset"
test "$new_offset" -lt 20000

echo "ruby: deployed modular Z-Knowledge skills; gate byte=$new_offset; request-z-code retired; backup=$backup"
