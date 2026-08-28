#!/usr/bin/env bash
set -euo pipefail

version="${GOG_VERSION:-0.34.1}"
base_url="https://github.com/openclaw/gogcli/releases/download/v${version}"
archive="gogcli_${version}_linux_amd64.tar.gz"
agents=(harry frank suzy)
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
wrapper_path="$(cd "$(dirname "$0")" && pwd)/gog-vps2"
[[ -n "${gog_binary}" && -f "${wrapper_path}" ]] || exit 1

install -d -o root -g root -m 0755 /usr/local/libexec
if [[ -f /usr/local/bin/gog ]]; then
  cp /usr/local/bin/gog "/usr/local/bin/gog.backup-${backup_stamp}"
fi
install -o root -g root -m 0755 "${gog_binary}" /usr/local/libexec/gog-real
install -o root -g root -m 0755 "${wrapper_path}" /usr/local/bin/gog

for agent in "${agents[@]}"; do
  agent_home="/root/.openclaw-${agent}"
  gog_home="${agent_home}/.config/gogcli"
  install -d -o root -g root -m 0700 "${gog_home}"
  if [[ ! -s "${gog_home}/keyring.env" ]]; then
    password="$(head -c 48 /dev/urandom | base64 | tr -d '\n')"
    umask 077
    printf 'GOG_KEYRING_PASSWORD=%s\n' "${password}" > "${gog_home}/keyring.env"
  fi
  chmod 0600 "${gog_home}/keyring.env"

  HOME="${agent_home}" OPENCLAW_STATE_DIR="${agent_home}" \
    OPENCLAW_CONFIG_PATH="${agent_home}/openclaw.json" \
    openclaw config set skills.entries.gog.enabled true >/dev/null

  skill_json="$(HOME="${agent_home}" OPENCLAW_STATE_DIR="${agent_home}" \
    OPENCLAW_CONFIG_PATH="${agent_home}/openclaw.json" openclaw skills info gog --json)"
  printf '%s' "${skill_json}" | grep -q '"eligible": true'
  printf '%s' "${skill_json}" | grep -q '"modelVisible": true'
  HOME="${agent_home}" gog --version
  echo "${agent}: gog eligible and model-visible"
done

echo "VPS2 gog software activation complete. Google OAuth authorization is still required per agent."

