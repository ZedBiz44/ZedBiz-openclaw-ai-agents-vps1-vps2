#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--auto" && -n "${2:-}" ]]; then
  project_dir="$(find "$2/npm/projects" -maxdepth 1 -type d -name 'mem0-openclaw-mem0-*' -printf '%T@ %p\n' | sort -nr | head -1 | cut -d' ' -f2-)"
elif [[ $# -eq 1 ]]; then
  project_dir="$1"
else
  echo "Usage: $0 <active-mem0-plugin-project-directory> | --auto <openclaw-state-directory>" >&2
  exit 2
fi

[[ -d "$project_dir" ]] || { echo "Project not found: $project_dir" >&2; exit 1; }
oss_dir="$project_dir/node_modules/mem0ai/dist/oss"
[[ -f "$oss_dir/index.js" && -f "$oss_dir/index.mjs" ]] || { echo "Mem0 OSS runtime files not found under: $oss_dir" >&2; exit 1; }
cd "$project_dir"

plugin_version="$(node -e 'const fs=require("fs"); const p=JSON.parse(fs.readFileSync("node_modules/@mem0/openclaw-mem0/package.json","utf8")); process.stdout.write(p.version)')"
[[ "$plugin_version" == "1.1.0" ]] || { echo "Compatibility guard stopped: approved only for openclaw-mem0 1.1.0, found $plugin_version" >&2; exit 1; }

npm pkg set 'dependencies.@qdrant/js-client-rest=1.18.0' 'overrides.@qdrant/js-client-rest=1.18.0'
qdrant_version="$(node -e 'const fs=require("fs"); const p=JSON.parse(fs.readFileSync("node_modules/@qdrant/js-client-rest/package.json","utf8")); process.stdout.write(p.version)')"
if [[ "$qdrant_version" != "1.18.0" ]]; then
  npm install --no-audit --no-fund
else
  npm install --package-lock-only --ignore-scripts --no-audit --no-fund >/dev/null
fi

for file in "$oss_dir/index.js" "$oss_dir/index.mjs"; do
  if ! grep -q 'parsedUrl.protocol === "https:" ? 443 : 6333' "$file"; then
    sed -i 's/params\.port = parsedUrl\.port ? parseInt(parsedUrl\.port) : 6333;/params.port = parsedUrl.port ? parseInt(parsedUrl.port) : parsedUrl.protocol === "https:" ? 443 : 6333;/' "$file"
    sed -i 's/params\.port = parsedUrl\.port ? parseInt(parsedUrl\.port, 10) : 6333;/params.port = parsedUrl.port ? parseInt(parsedUrl.port, 10) : parsedUrl.protocol === "https:" ? 443 : 6333;/' "$file"
  fi
  grep -q 'parsedUrl.protocol === "https:" ? 443 : 6333' "$file"
  node --check "$file"
done

qdrant_version="$(node -e 'const fs=require("fs"); const p=JSON.parse(fs.readFileSync("node_modules/@qdrant/js-client-rest/package.json","utf8")); process.stdout.write(p.version)')"
node -e 'const { QdrantClient } = require("@qdrant/js-client-rest"); if (typeof QdrantClient.prototype.search !== "function") { throw new Error("QdrantClient.search is unavailable"); }'
echo "Mem0 $plugin_version HTTPS compatibility guard verified; Qdrant JS client $qdrant_version exposes search()."

