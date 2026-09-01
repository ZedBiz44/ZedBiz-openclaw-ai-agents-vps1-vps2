#!/usr/bin/env bash
set -euo pipefail

agents=(amanda edith gohzed grogar inga maggie marsha terry victor vivian wilma)

echo "agent|version|image|restart_count|health"
for agent in "${agents[@]}"; do
  version="$(docker exec "$agent" openclaw --version 2>/dev/null | tr -d '\r\n')"
  docker inspect "$agent" --format "$agent|$version|{{.Config.Image}}|{{.RestartCount}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}"
done

echo "external_plugins"
for agent in "${agents[@]}"; do
  printf '%s|' "$agent"
  docker exec "$agent" sh -lc 'openclaw plugins list --json | jq -r "[.plugins[] | select(.origin != \"bundled\") | {id,version,origin,status,enabled}] | @json"' 2>/dev/null
done

echo "skill_counts"
for agent in "${agents[@]}"; do
  printf '%s|' "$agent"
  docker exec "$agent" sh -lc 'openclaw skills list --json | jq -r "{total:(.skills|length),eligible:([.skills[]|select(.eligible==true)]|length),enabled_blocked:([.skills[]|select(.disabled==false and .eligible==false)]|length),enabled_missing:([.skills[]|select(.disabled==false and ((.missing.bins|length)>0 or (.missing.anyBins|length)>0 or (.missing.env|length)>0 or (.missing.config|length)>0 or (.missing.os|length)>0))]|length)} | @json"' 2>/dev/null
done

echo "config_policy"
for agent in "${agents[@]}"; do
  printf '%s|' "$agent"
  docker exec "$agent" sh -lc 'jq -c "{dmScope:(.session.dmScope // null),sessionVisibility:(.tools.sessions.visibility // null),trustedProxies:(.gateway.trustedProxies // []),gatewayBind:(.gateway.bind // null),pluginIds:((.plugins.entries // {})|keys),mcpIds:((.mcp.servers // {})|keys)}" /home/node/.openclaw/openclaw.json' 2>/dev/null
done

echo "doctor_summary"
for agent in "${agents[@]}"; do
  printf '%s|' "$agent"
  docker exec "$agent" sh -lc 'openclaw doctor --lint --json | jq -c "{ok:(.ok // false),findingCount:((.findings // [])|length),errors:([(.findings // [])[]|select(.severity==\"error\" or .severity==\"critical\")]|length),warnings:([(.findings // [])[]|select(.severity==\"warning\")]|length),codes:[(.findings // [])[]?.code]}"' 2>/dev/null || echo '{"probe":"failed"}'
done

echo "shared_tools"
for spec in \
  "gog:gog --version" \
  "ntn:ntn --version" \
  "summarize:summarize --version" \
  "mcporter:mcporter --version" \
  "rg:rg --version" \
  "ffmpeg:ffmpeg -version" \
  "himalaya:himalaya --version" \
  "codex:codex --version" \
  "gemini:gemini --version" \
  "nano-pdf:nano-pdf --version" \
  "gifgrep:gifgrep --version"; do
  name="${spec%%:*}"
  command="${spec#*:}"
  printf '%s|' "$name"
  docker exec amanda sh -lc "timeout 10 $command 2>&1 | head -1" || true
  if [[ "$name" == "gemini" || "$name" == "nano-pdf" || "$name" == "gifgrep" ]]; then
    printf '%s-victor|' "$name"
    docker exec victor sh -lc "timeout 10 $command 2>&1 | head -1" || true
  fi
done
