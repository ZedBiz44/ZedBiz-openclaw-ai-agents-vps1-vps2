#!/bin/sh
set -eu
project_dir=""
for candidate in /home/node/.openclaw/npm/projects/mem0-*; do
  manifest="$candidate/node_modules/@mem0/openclaw-mem0/package.json"
  if [ -f "$manifest" ] && [ "$(node -p "require('$manifest').version")" = "1.2.1" ]; then
    [ -z "$project_dir" ] || { echo 'Multiple Mem0 1.2.1 projects; inspect active generation' >&2; exit 1; }
    project_dir="$candidate"
  fi
done
[ -n "$project_dir" ] || { echo 'Mem0 1.2.1 project not found' >&2; exit 1; }
qdrant_manifest="$project_dir/node_modules/@qdrant/js-client-rest/package.json"
[ "$(node -p "require('$qdrant_manifest').version")" = "1.18.0" ] || { echo 'Qdrant must remain pinned at 1.18.0' >&2; exit 1; }
[ "$(node -e "const {QdrantClient}=require('$project_dir/node_modules/@qdrant/js-client-rest'); process.stdout.write(typeof QdrantClient.prototype.search)")" = function ] || exit 1
python3 /home/node/.openclaw/scripts/repair-mem0-explicit-retention.py "$project_dir"
node /home/node/.openclaw/scripts/repair-mem0-host-peer.mjs "$project_dir"
echo '[mem0-compat] Mem0 1.2.1: Qdrant search, explicit retention, unique recall tools, host peer verified.'
