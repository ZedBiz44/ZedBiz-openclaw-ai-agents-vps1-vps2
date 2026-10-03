#!/bin/bash
set -euo pipefail
stage=/opt/openclaw/builds/2026.9.8-terry-20261003/tools-stage
shared=/opt/openclaw/shared
backup=/opt/openclaw/backups/shared-tools-20261003
test ! -e "$backup"
mkdir -m 700 "$backup"
for name in gog-real ntn rg jq; do
    test -x "$stage/$name"
    cp -a "$shared/bin/$name" "$backup/$name"
    install -m 755 "$stage/$name" "$shared/bin/$name.new-20261003"
    mv "$shared/bin/$name.new-20261003" "$shared/bin/$name"
done
# Preserve wrappers and credentials. Replace only the two tested npm packages.
for name in mcporter @steipete/summarize; do
    test -d "$stage/npm/lib/node_modules/$name"
    mkdir -p "$backup/npm/$(dirname "$name")"
    mv "$shared/lib/node_modules/$name" "$backup/npm/$name"
    cp -a "$stage/npm/lib/node_modules/$name" "$shared/lib/node_modules/$name"
done
echo SHARED_TOOLS_UPDATED
# Himalaya 2.x changes CLI syntax; retain the verified 1.2.0 email tool.
