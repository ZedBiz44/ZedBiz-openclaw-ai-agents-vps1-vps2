# Maggie Android pairing URL correction

Date: 2026-10-30 MDT | Added by: Cody | Agent: Maggie | System: VPS1 OpenClaw

## Purpose and authorization
Jack approved correcting Maggie-only QR pairing after Android NETWORK_UNREACHABLE. Issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/562

## Change
File: /opt/openclaw/agents/maggie/config/openclaw.json (container /home/node/.openclaw/openclaw.json).
Set plugins.entries.device-pair.config.publicUrl to wss://maggie.zbiz.ca/; preserve all other settings. Previously no override existed and the resolver selected ws://172.18.0.28:3008. Installed UI sends no publicUrl override.

Protected backup: /home/node/.openclaw/openclaw.json.before-android-pairing-1793409954567. Created as node with mode 0600 before editing. Native config watcher detected change and normal startup restarted gateway; no manual restart command.

## Commands and tests
Inspected installed setup-code resolver and plugin schema. Applied targeted JSON edit through docker exec -u node -i maggie node. Ran docker exec maggie openclaw config validate: passed, existing disabled memory-core warning retained. Initial node-user CLI validation reported shared-state read/cleanup error; root CLI validation passed. Direct node-user JSON read also passed. Early RPC probes timed out during startup. After container became healthy, docker exec maggie openclaw gateway call device.pair.setupCode --params '{"includeQr":false}' --json --timeout 15000 succeeded. Output captured privately and reduced to non-secret fields: gatewayUrl=wss://maggie.zbiz.ca, urlSource=plugins.entries.device-pair.config.publicUrl, access=full, hasSetupCode=true. Test credential not printed or saved in records. Public WebSocket transport also opens.

## Outcome and follow-up
Configuration and actual running setup-code method verified. Jack must refresh dashboard, create fresh QR, scan in Android and confirm paired status. End-to-end phone success pending; issue remains open. No other agents changed; no SOP edit. Daily Tech Updates journal appended.

## Rollback
Remove only the newly added publicUrl field (and empty new entry if appropriate), retaining unrelated subsequent edits. Protected backup records prior state; restore whole file only after checking for subsequent changes. Normal watcher applies configuration changes.
