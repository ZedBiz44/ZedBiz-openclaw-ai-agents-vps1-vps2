#!/usr/bin/env bash
set -euo pipefail

version="${GOG_VERSION:-0.34.1}"
base_url="https://github.com/openclaw/gogcli/releases/download/v${version}"
archive="gogcli_${version}_linux_amd64.tar.gz"
agents=("$@")

if (( ${#agents[@]} == 0 )); then
  agents=(amanda edith gohzed grogar inga maggie marsha terry victor vivian wilma)
fi

work_dir="$(mktemp -d)"
backup_stamp="$(date +%Y%m%dT%H%M%S%z)"
trap 'rm -rf "${work_dir}"' EXIT

curl -fsSL "${base_url}/${archive}" -o "${work_dir}/${archive}"
curl -fsSL "${base_url}/checksums.txt" -o "${work_dir}/checksums.txt"
expected="$(awk -v name="${archive}" '$2 == name {print $1}' "${work_dir}/checksums.txt")"
actual="$(sha256sum "${work_dir}/${archive}" | awk '{print $1}')"
[[ -n "${expected}" && "${expected}" == "${actual}" ]] || {
  echo "gog checksum verification failed" >&2
  exit 1
}

tar -xzf "${work_dir}/${archive}" -C "${work_dir}"
gog_binary="$(find "${work_dir}" -maxdepth 2 -type f -name gog -print -quit)"
[[ -n "${gog_binary}" ]] || {
  echo "gog binary was not found in the release archive" >&2
  exit 1
}

wrapper_path="$(cd "$(dirname "$0")" && pwd)/gog"
[[ -f "${wrapper_path}" ]] || {
  echo "gog wrapper is missing beside this installer" >&2
  exit 1
}

docker run --rm \
  -v /opt/openclaw/shared/bin:/dest \
  -v "${gog_binary}:/src/gog-real:ro" \
  -v "${wrapper_path}:/src/gog:ro" \
  alpine sh -lc '
    set -eu
    if [ -f /dest/gog ]; then cp /dest/gog "/dest/gog.backup-'"${backup_stamp}"'"; fi
    cp /src/gog-real /dest/gog-real
    cp /src/gog /dest/gog
    chown root:root /dest/gog-real /dest/gog
    chmod 0755 /dest/gog-real /dest/gog
  '

for agent in "${agents[@]}"; do
  agent_root="/opt/openclaw/agents/${agent}"
  compose_file="${agent_root}/docker-compose.yml"
  [[ -f "${compose_file}" ]] || {
    echo "missing compose file for ${agent}" >&2
    exit 1
  }

  cp "${compose_file}" "${compose_file}.backup-${backup_stamp}"

  python3 - "${compose_file}" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text()
mount = "    - /opt/openclaw/shared/bin/gog:/usr/local/bin/gog:ro\n"
if mount not in text:
    anchor = "    - /opt/openclaw/shared:/opt/openclaw/shared:rw\n"
    if anchor not in text:
        raise SystemExit(f"shared volume anchor missing in {path}")
    text = text.replace(anchor, anchor + mount, 1)
    path.write_text(text)
PY

  docker run --rm -v "${agent_root}/config:/cfg" alpine sh -lc '
    set -eu
    mkdir -p /cfg/gogcli
    if [ ! -s /cfg/gogcli/keyring.env ]; then
      password="$(head -c 48 /dev/urandom | base64 | tr -d "\n")"
      umask 077
      printf "GOG_KEYRING_PASSWORD=%s\n" "${password}" > /cfg/gogcli/keyring.env
    fi
    chown -R 1000:1000 /cfg/gogcli
    chmod 0700 /cfg/gogcli
    chmod 0600 /cfg/gogcli/keyring.env
  '

  if docker ps --format '{{.Names}}' | grep -qx "${agent}"; then
    docker exec "${agent}" openclaw config set skills.entries.gog.enabled true >/dev/null
  fi

  docker compose -f "${compose_file}" config --quiet
  start_wrapper="${agent_root}/op-start-${agent}.sh"
  [[ -x "${start_wrapper}" ]] || {
    echo "missing 1Password-aware start wrapper for ${agent}" >&2
    exit 1
  }
  if ! "${start_wrapper}" up; then
    resolved_env="${agent_root}/.env.resolved"
    if [[ -r "${resolved_env}" ]] && ! grep -q '=op://' "${resolved_env}"; then
      echo "${agent}: vault resolution failed; using protected .env.resolved fallback" >&2
      (
        cd "${agent_root}"
        docker compose --env-file .env.resolved up -d
      )
    else
      exit 1
    fi
  fi

  for _ in $(seq 1 30); do
    status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${agent}" 2>/dev/null || true)"
    [[ "${status}" == "healthy" || "${status}" == "running" ]] && break
    sleep 2
  done

  verified=false
  for _ in $(seq 1 15); do
    if docker exec "${agent}" sh -lc '
      set -eu
      gog --version
      openclaw skills info gog --json | grep -q "\"eligible\": true"
      openclaw skills info gog --json | grep -q "\"modelVisible\": true"
    '; then
      verified=true
      break
    fi
    sleep 2
  done
  [[ "${verified}" == "true" ]] || {
    echo "${agent}: gog did not become eligible and model-visible" >&2
    exit 1
  }
  echo "${agent}: gog eligible and model-visible"
done

echo "VPS1 gog software activation complete. Google OAuth authorization is still required per agent."

