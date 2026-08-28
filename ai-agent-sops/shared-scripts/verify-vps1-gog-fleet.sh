#!/usr/bin/env bash
set -euo pipefail

agents=(amanda edith gohzed grogar inga maggie marsha terry victor vivian wilma)

for agent in "${agents[@]}"; do
  status="$(docker inspect -f '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|restarts={{.RestartCount}}|oom={{.State.OOMKilled}}' "${agent}")"
  unresolved="$(docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "${agent}" | grep -c '=op://' || true)"
  gog_version="$(docker exec "${agent}" gog --version 2>/dev/null | awk '{print $1}')"
  skill_json="$(docker exec "${agent}" openclaw skills info gog --json 2>/dev/null)"
  eligible="$(printf '%s' "${skill_json}" | grep -c '"eligible": true' || true)"
  visible="$(printf '%s' "${skill_json}" | grep -c '"modelVisible": true' || true)"
  gateway_ready="$(docker logs --since 20m "${agent}" 2>&1 | grep -c '\[gateway\] ready' || true)"
  auth_errors="$(docker logs --since 20m "${agent}" 2>&1 | grep -c '401.*Unauthorized\|Incorrect API key.*op://' || true)"

  printf '%s|%s|unresolved=%s|gog=%s|eligible=%s|visible=%s|gateway_ready=%s|auth_errors=%s\n' \
    "${agent}" "${status}" "${unresolved}" "${gog_version}" "${eligible}" "${visible}" "${gateway_ready}" "${auth_errors}"
done

