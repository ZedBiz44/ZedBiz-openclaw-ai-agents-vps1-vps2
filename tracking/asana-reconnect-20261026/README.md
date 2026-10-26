# Asana reconnect repair, October 26, 2026

Date: 2026-10-26 | Agent: [Manus] | Status: Applied fleet-wide; Rocky memory and next scheduled acceptance pending

## Purpose

Keep the accepted OpenClaw 2026.10.6 upgrade while fixing a shared MCP reconnection race. The guard waits for both a connected transport and tool metadata before dispatch. It does not replay a failed operation or change credentials, models, Codex routes, memory, schedules or delivery policy.

[Primary technical issue 493](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/493) records Jack’s conditional approval, attempts, failures, verification and remaining decisions. [Issue 492](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/492) holds the preceding live fleet diagnosis. [Victor’s original repair](https://github.com/ZedBiz44/z-agent-health-report-Skill/issues/6#issuecomment-6417595335) is the tested patch source.

## What is verified

- Amanda and Wilma already run the refined fix. Both passed actual native Asana, Codex-connected Notion, memory and required messaging/health checks.
- Both passed corrected real inactivity acceptance in the same existing conversations after the Asana service reported zero old sessions. Actual native identity/workspace calls succeeded without replay. This proves normal use after inactivity; it does not trace every exact server-close cause.
- Eight additional VPS1 candidates preserve their individual accepted base images and passed seven readable and six exported-worker behaviors. Victor’s preexisting exact staged candidate has the same proof.
- Frank, Harry, Suzy and Rocky have a different native package with one target module, not VPS1’s three bundled copies. Their in-memory candidates each passed seven readable behaviors using synthetic loopback MCP only.
- Ruby and Roy run Hermes on VPS3 and are excluded from this OpenClaw repair.

## Runtime changes and safeguards

VPS1 changes only the owning agent’s Compose image selection and performs a controlled recreation through its existing op-start credential loader. Each original accepted image and exact saved Compose file remains available. Restart requires complete authoritative active-session coverage, no running scheduled job and idle connected channels.

Native VPS2/VPS4 changes only `dist/agents/agent-bundle-mcp-runtime.js` after exact original/candidate hash checks, backup and metadata capture. It atomically replaces the module, preserves ownership/mode, and restarts only the confirmed owning systemd service at idle. Existing runtime credentials are consumed privately; they are not changed or published.

One agent is verified before moving to the next. A different production issue stops further rollout and returns the decision to Jack. No forced busy restart or timeout/provider workaround is allowed.

## Files

- `scripts/`: incident-specific guarded staging, inactivity, deployment and current-feature acceptance code. These preserve the original task’s private path conventions and are not a new general SOP.
- `proof/vps1-patch-manifest.json`: exact three bundled file guards and hashes.
- `proof/native-patch-manifest.json`: exact native module paths, metadata and guard.
- `proof/actual-inactivity-acceptance.json`: sanitized actual expiry/resumption acceptance.
- `proof/regression-agents.mjs`, `proof/regression-worker.mjs`: existing synthetic container fixtures.
- `proof/run-native-behavior-proof.mjs`: native in-memory adaptation of the same readable fixture.
- `INACTIVITY-RESULT.md`: completed gate and its limitations.

Raw business responses, memory contents, full configuration, environment values and credentials are deliberately excluded. Do not run the deployment scripts by assumption: they require the accepted task’s staged candidates and actual gate files.

## Retained failed attempts

The first inactivity prompt wrongly prohibited normal tool discovery. Amanda made no native call, so it was invalid test setup, not a verified reconnect failure. That result remains in the private task history. The corrected test permitted the normal discovery route and waited for the automatically prepared connection to disappear before retry.

Terry’s first isolated fixture could not read its test file because umask left the proof folder private. No fixture operation ran and no live change occurred. Corrected only the secret-free proof folder and tested the same already built image without rebuilding it. The original errors remain retained.

## Remaining acceptance

Tomorrow’s ordinary daily journals cannot be claimed passed today. Existing scheduled results still need review even after all current deployment checks pass. Main-branch status and final per-agent rollout receipts will be linked from issue 493. Until a PR is merged, this branch is implementation evidence, not an assertion that main already reflects every live change.

## Final deployment checkpoint

All fifteen agents have the exact repair, remain on 2026.10.6 / Node 24.22.1 and passed the final read-only runtime/hash/health inventory. Fourteen passed actual Asana, Codex Notion and existing memory reads. Rocky passed Asana, Notion, health and all required channel probes, but his memory test is not verified because the remote operator call lacks the stable authenticated sender required by his unchanged provider-separated policy. No sender spoofing or memory-policy change is allowed to obtain a test pass. See `FINAL-STATUS.md`, `proof/native-live-acceptance.json` and `proof/final-runtime-audit.json`.

Jack’s normal message to Rocky is the remaining actual memory check. Victor retains already assigned next-cycle scheduled/recurrence review. Issue 493 stays open; PR 494 is open and main is unchanged. Future software replacement can overwrite a local hotfix, so retain this guard and regression proof with the upgrade record.
