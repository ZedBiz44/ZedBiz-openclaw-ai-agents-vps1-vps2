#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <active-mem0-plugin-project-directory>" >&2
  exit 2
fi

project_dir="$1"
oss_dir="$project_dir/node_modules/mem0ai/dist/oss"

[[ -d "$project_dir" ]] || { echo "Project not found: $project_dir" >&2; exit 1; }
[[ -f "$oss_dir/index.js" && -f "$oss_dir/index.mjs" ]] || {
  echo "Mem0 OSS runtime files not found under: $oss_dir" >&2
  exit 1
}

cd "$project_dir"
npm install --no-audit --no-fund --save-exact @qdrant/js-client-rest@1.18.0

for file in "$oss_dir/index.js" "$oss_dir/index.mjs"; do
  if grep -q 'parsedUrl.protocol === "https:" ? 443 : 6333' "$file"; then
    continue
  fi
  sed -i \
    's/params\.port = parsedUrl\.port ? parseInt(parsedUrl\.port) : 6333;/params.port = parsedUrl.port ? parseInt(parsedUrl.port) : parsedUrl.protocol === "https:" ? 443 : 6333;/' \
    "$file"
  grep -q 'parsedUrl.protocol === "https:" ? 443 : 6333' "$file"
  node --check "$file"
done

npm ls @qdrant/js-client-rest --depth=0
echo "Mem0 1.0.15 Qdrant compatibility guard applied. Restart the owning gateway and run a real write/search probe."

