#!/usr/bin/env bash
set -euo pipefail

work_dir="$(mktemp -d)"
stamp="$(date +%Y%m%dT%H%M%S%z)"
trap 'rm -rf "${work_dir}"' EXIT

gog_version=0.38.1
gog_archive="gogcli_${gog_version}_linux_amd64.tar.gz"
curl -fsSL "https://github.com/openclaw/gogcli/releases/download/v${gog_version}/${gog_archive}" -o "${work_dir}/${gog_archive}"
curl -fsSL "https://github.com/openclaw/gogcli/releases/download/v${gog_version}/checksums.txt" -o "${work_dir}/gog-checksums.txt"
expected="$(awk -v name="${gog_archive}" '$2 == name {print $1}' "${work_dir}/gog-checksums.txt")"
actual="$(sha256sum "${work_dir}/${gog_archive}" | awk '{print $1}')"
[[ -n "${expected}" && "${expected}" == "${actual}" ]]
tar -xzf "${work_dir}/${gog_archive}" -C "${work_dir}"
gog_binary="$(find "${work_dir}" -maxdepth 2 -type f -name gog -print -quit)"

docker run --rm \
  -v /opt/openclaw/shared/bin:/dest \
  -v "${gog_binary}:/src/gog-real:ro" \
  alpine:3.22 sh -c "cp /dest/gog-real /dest/gog-real.backup-${stamp}; cp /src/gog-real /dest/gog-real; chown root:root /dest/gog-real; chmod 0755 /dest/gog-real"

docker run --rm \
  -v /opt/openclaw/shared/lib:/dest \
  node:24-bookworm sh -c '
    set -eu
    npm install -g --prefix /tmp/stage @steipete/summarize@0.21.11 mcporter@0.13.8
    rm -rf /dest/node_modules/@steipete/summarize /dest/node_modules/@steipete/summarize-core /dest/node_modules/mcporter
    cp -a /tmp/stage/lib/node_modules/. /dest/node_modules/
    npm cache clean --force
  '

docker run --rm \
  -v /opt/openclaw/shared/bin:/shared \
  alpine:3.22 sh -c "cp /shared/ntn /shared/ntn.backup-${stamp}"
docker run --rm \
  -v /opt/openclaw/shared/bin:/shared \
  ghcr.io/zedbiz44/openclaw-base:2026.8.2 \
  bash -lc 'curl -fsSL https://ntn.dev | NTN_VERSION=0.22.12 NTN_INSTALL_DIR=/shared bash'

docker exec amanda sh -lc 'gog --version; summarize --version; mcporter --version; ntn --version'
