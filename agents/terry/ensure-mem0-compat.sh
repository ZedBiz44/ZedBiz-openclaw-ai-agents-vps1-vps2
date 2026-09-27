#!/bin/sh
set -eu
project_dir=""
for candidate in /home/node/.openclaw/npm/projects/mem0-*; do
  manifest="$candidate/node_modules/@mem0/openclaw-mem0/package.json"
  if [ -f "$manifest" ] && [ "$(node -p "require('$manifest').version")" = "1.1.0" ]; then
    project_dir="$candidate"
    break
  fi
done
if [ -z "$project_dir" ]; then
  echo '[mem0-compat] Mem0 1.1.0 project directory not found' >&2
  exit 1
fi
qdrant_manifest="$project_dir/node_modules/@qdrant/js-client-rest/package.json"
qdrant_version="$(node -p "require('$qdrant_manifest').version")"
if [ "$qdrant_version" != "1.18.0" ]; then
  echo "[mem0-compat] Qdrant client must remain pinned at 1.18.0, found: $qdrant_version" >&2
  exit 1
fi
has_search="$(node -e "const {QdrantClient}=require('$project_dir/node_modules/@qdrant/js-client-rest'); process.stdout.write(typeof QdrantClient.prototype.search)")"
if [ "$has_search" != "function" ]; then
  echo "[mem0-compat] Qdrant search compatibility failed: search=$has_search" >&2
  exit 1
fi
echo '[mem0-compat] Mem0 1.1.0 verified with Qdrant JS 1.18.0 search().'

# Preserve the authorized explicit-retention and tool-routing repair.
python3 /home/node/.openclaw/scripts/repair-mem0-explicit-retention.py "$project_dir"
