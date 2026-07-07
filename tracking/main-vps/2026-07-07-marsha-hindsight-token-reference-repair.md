# 2026-07-07 - VPS Change - Marsha Hindsight Token Reference Repair

## Summary

- **Date:** 2026-07-07 Mountain Time
- **Changed By:** Cody
- **VPS:** main-vps
- **Affected Agent:** Marsha
- **Status:** done

## Change Reason

- Marsha was returning `502` at `https://marsha.zbiz.ca/health` because the `marsha` container was crash-looping.
- The startup failure was caused by an unresolved secret reference in Marsha's Hindsight plugin config:
  - `plugins.entries.hindsight-openclaw.config.hindsightApiToken`
  - referenced env secret: `HINDSIGHT_API_TOKEN`
- Marsha uses the private Docker Hindsight route `http://hindsight:8888`, and the Hindsight service is not configured to require this token for the internal route.
- Maggie proved the working control pattern: same private Hindsight route, same `zedbiz-shared` bank, no token field, and healthy Hindsight initialization.

## Root Cause

- The Hindsight plugin documentation includes `hindsightApiToken` for an external Hindsight API pattern.
- That external-token pattern was applied to Marsha's private Docker route without adding `HINDSIGHT_API_TOKEN` to Marsha's runtime environment.
- The bad field existed before the outage but did not break Marsha until the container restarted on 2026-07-07 at about 05:44 Mountain Time.

## Change Details

- VPS path:
  - `/opt/openclaw/agents/marsha/config/openclaw.json`
- Backup created:
  - `/opt/openclaw/agents/marsha/config/openclaw.json.bak-cody-hindsight-token-20260707T171542-0600`
- Files changed:
  - Removed only `plugins.entries.hindsight-openclaw.config.hindsightApiToken`
- Services restarted:
  - Restarted only Docker container `marsha`
- Docker containers affected:
  - `marsha`

## Verification

- Config field removed:
  - `has_hindsightApiToken=false`
  - `bank=zedbiz-shared`
  - `url=http://hindsight:8888`
- Container status:
  - `marsha|Up About a minute (healthy)`
- Public endpoint:
  - `https://marsha.zbiz.ca/health`
  - returned `200 OK`
  - response: `{"ok":true,"status":"live"}`
- Logs checked:
  - No fresh `HINDSIGHT_API_TOKEN` or `SecretRefResolutionError` entries after the successful restart.
  - Hindsight initialized with bank `zedbiz-shared`.
- Config validation:
  - `Config valid: ~/.openclaw/openclaw.json`
  - Existing version warning remains: config written by `2026.6.8`, command path running `2026.6.6`.

## Rollback Note

- Restore the backup:
  - `/opt/openclaw/agents/marsha/config/openclaw.json.bak-cody-hindsight-token-20260707T171542-0600`
- Restart only the `marsha` container.
- This would restore the unresolved token reference and is expected to reintroduce the startup failure unless `HINDSIGHT_API_TOKEN` is also added correctly.

## Operating Rule Captured

- For internal VPS1 Hindsight access through `http://hindsight:8888`, do not add `hindsightApiToken` unless the Hindsight API itself is explicitly configured to require one and the matching env secret is present in the agent runtime.

## Links

- GitHub Issue:
- Notion page:
- Related commit:
