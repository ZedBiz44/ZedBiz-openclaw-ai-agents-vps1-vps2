# 2026-10-30 - VPS1 mobile pairing public URL rollout

## Summary

- Date: 2026-10-30, 19:41–19:44 MDT.
- Changed by: Cody.
- VPS/system: main-vps / VPS1 / OpenClaw 2026.10.6.
- Status: server-side rollout verified.
- Authorization: Jack requested the same proven Maggie fix for all remaining VPS1 agents after confirming his Android app works.
- Affected agents: Amanda, Edith, Gohzed, Grogar, Inga, Marsha, Terry, Victor, Vivian and Wilma. Maggie's successful pilot remained unchanged.

## Change reason

Without an explicit public pairing URL, the gateway resolves its Docker-private address into mobile setup codes. Phones cannot reach that address. Maggie's public URL correction passed actual Android pairing and node approval before this rollout.

## Change details

Live config for each agent: /opt/openclaw/agents/<agent>/config/openclaw.json, mounted at /home/node/.openclaw/openclaw.json.

Added only plugins.entries.device-pair.config.publicUrl = wss://<agent>.zbiz.ca/. All ten had no existing device-pair entry, and each expected HTTPS hostname matched the live allowedOrigins configuration. Preserved all other configuration. Final parsed-JSON comparisons against each backup confirmed the pairing entry was the sole change.

Protected mode-0600 backups live alongside each config with basename openclaw.json.before-vps1-mobile-pairing-<suffix>:

| Agent | Verified setup-code URL | Backup suffix | Validation and live RPC |
|---|---|---|---|
| amanda | wss://amanda.zbiz.ca | 1793410867226 | Passed |
| edith | wss://edith.zbiz.ca | 1793410867361 | Passed |
| gohzed | wss://gohzed.zbiz.ca | 1793410939645 | Passed |
| grogar | wss://grogar.zbiz.ca | 1793410939774 | Passed |
| inga | wss://inga.zbiz.ca | 1793410969016 | Passed |
| marsha | wss://marsha.zbiz.ca | 1793410969132 | Passed |
| terry | wss://terry.zbiz.ca | 1793411018113 | Passed |
| victor | wss://victor.zbiz.ca | 1793411018243 | Passed |
| vivian | wss://vivian.zbiz.ca | 1793411047498 | Passed |
| wilma | wss://wilma.zbiz.ca | 1793411047633 | Passed |

Used staged batches of two. No manual container restarts; observed configuration hot reload. No phone pairing requests approved, other VPS hosts changed, provider calls or new integrations.

## Commands and verification

- Read safe config fields with docker exec <agent> node, and inspect actual Docker config mounts.
- Applied checked JSON edit as node through docker exec -u node -i <agent> node; created exclusive protected backup before write.
- docker exec <agent> openclaw config validate passed for all ten.
- docker exec <agent> openclaw gateway call device.pair.setupCode --params '{"includeQr":false}' --json --timeout 10000 passed for all ten after reload.
- RPC result: correct public gatewayUrl; urlSource=plugins.entries.device-pair.config.publicUrl; access=full; setupCode present.
- Captured setup-code output privately and printed only these non-secret fields. Test setup codes were not exposed or retained in records; they expire normally.
- Every public HTTPS route returned 200 and every public WebSocket transport opened from Cody's PC.
- Final all-eleven health check: healthy, including Maggie.
- Original phone end-to-end success established on Maggie only. Other agents are ready for Jack to add; each still requires normal pairing and any node permission approval.

## Attempts and observations

A local Python preflight failed because the Windows python alias is unavailable. PowerShell/curl and ClientWebSocket probes succeeded.

Initial rollout orchestration waited for a restart timestamp change. Amanda and Edith actually hot-reloaded. Terminated only the waiting remote Python orchestration process, preserved completed edits, and resumed idempotently using actual healthy status and live RPC results as acceptance gates.

Marsha briefly returned her old Docker URL during reload and logged a device-pair service instance unavailable during replacement. Subsequent RPC and config validation passed. No persistent failure observed. No additional changes were needed.

## Rollback

Remove only the newly added device-pair entry from the relevant config after checking for subsequent edits. The protected backup contains the previous config; restore an entire backup only if no intervening changes would be lost. Let normal reload apply, then validate and check health. Roll back one affected agent at a time.

## Records and scope

- Issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/562
- Pilot: tracking/2026-10-30-maggie-android-pairing.md
- Daily Tech Updates: https://app.notion.com/p/409a3e33d58181f3a65ece54e459e1a1
- This technical implementation record is committed to main; no separate code branch required.
- Registry/SOP: no edits; no existing pairing guide was changed or duplicated.
