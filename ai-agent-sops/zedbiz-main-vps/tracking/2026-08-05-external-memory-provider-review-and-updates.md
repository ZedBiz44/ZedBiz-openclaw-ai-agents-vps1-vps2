# 2026-08-05 External Memory Provider Review And Updates

Date: 2026-08-05 MDT | Agent: Cody | Status: Implemented And Verified

## Scope

Reconcile the live External Memory Providers hub, July 16 Results artifact, Mem0/Hindsight/LanceDB SOPs, official releases, VPS1/VPS2 runtime, Rocky's documented Hindsight lane, and a repeatable empirical memory-testing standard.

GitHub workstream: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/111

## Initial Live Inventory

- VPS1 Hindsight server: customized `zedbiz/hindsight:0.8.4-flashrank-20260804`; upstream server release `0.8.6`.
- Hindsight OpenClaw integration: installed `0.9.0`; upstream `0.10.0`.
- Mem0 OpenClaw integration: installed `1.0.14`; upstream `1.0.15`.
- LanceDB OpenClaw integration: installed and current at `2026.7.1`.
- VPS1 memory agents were healthy. VPS2 Harry, Frank, and Suzy services were active.

## Release Decisions

- Hindsight server `0.8.6`: update the pinned custom CPU image while preserving FlashRank, the existing memory volume, resource limits, and rollback assets.
- Hindsight OpenClaw `0.10.0`: test on Inga first, verify the official agent SDK recall-token fix replaces the local patch, then expand one agent at a time.
- Mem0 OpenClaw `1.0.15`: test on Terry first, then Edith and Harry one at a time. The release aligns default model names and includes dependency-security repairs.
- LanceDB OpenClaw `2026.7.1`: no package update required.

## Source-Of-Truth Boundaries

- GitHub holds exact versions, deployment evidence, rollback details, and technical history.
- Notion holds the business-readable provider map, operating SOPs, dated Results artifact, testing standard, and daily journal.
- External provider memory remains working context, not the final authority for live runtime or durable technical claims.

## Verification To Complete

- Build and smoke-test the Hindsight `0.8.6` derived image before replacing the live service.
- Verify health, database connection, direct recall, resource limits, and all affected agent services after the service update.
- Verify each plugin update with installed package version, plugin doctor, service health, and provider initialization.
- Re-fetch every changed Notion page and link the final journal entry and issue closeout.

## Hindsight Server Update

- Pulled the official `0.8.6` image and pinned digest `sha256:ffa391a77284e49f6b55e32c86f33529ac4257831407b14038a72b6a0a232039`.
- Built `zedbiz/hindsight:0.8.6-flashrank-20260805` with FlashRank preserved.
- Created protected backup `/opt/openclaw/services/hindsight/backups/release-086-20260805-091418`.
- Started the new image against a temporary isolated volume first; `/health` returned healthy with the database connected, then the temporary container and volume were removed.
- Preserved the production `hindsight-data` volume, OpenClaw network, 3 GB memory limit, and 3.5 GB combined memory-plus-swap limit.
- Retained stopped rollback container `hindsight-pre-086-20260805` on the prior `0.8.4` image.
- Production `/health` returned healthy and database connected.
- Direct `zedbiz-shared` recall through `/memories/recall` returned HTTP 200 with 50 results.

## OpenClaw Integration Updates

### Mem0

- Terry pilot: `1.0.14 -> 1.0.15`; plugin doctor passed; gateway healthy; plugin registered and initialized.
- Edith: `1.0.14 -> 1.0.15`; plugin doctor passed; gateway healthy.
- Harry: `1.0.14 -> 1.0.15`; plugin doctor passed; systemd service active.
- Per-agent backups were stored under each agent's `backups/provider-plugin-20260805` state path.

### Hindsight

- Inga pilot: `0.9.0 -> 0.10.0`; plugin doctor passed; gateway healthy; plugin initialized against `internet-marketing` with response-first settings preserved.
- GohZed, Grogar, Marsha, and Maggie: updated to `0.10.0` one at a time; each gateway returned healthy.
- Frank and Suzy: updated to `0.10.0` one at a time; each VPS2 systemd service returned active.
- The updated integration uses Hindsight client `0.8.6` and the published agent SDK fix; the August 4 source patch remains available as historical rollback evidence but is not the active package path after the update.
- Rocky's VPS4 dynamic-bank implementation remains recorded at `0.9.0`; VPS4 was outside the requested VPS1/VPS2 live review and requires a separate live check before an update.

### LanceDB

- Amanda, Victor, Vivian, and Wilma remain on current `@openclaw/memory-lancedb 2026.7.1`.
- Verified independent database paths, `autoRecall=true`, `autoCapture=true`, `captureMaxChars=800`, `recallMaxChars=1000`, and `text-embedding-3-small`.
- No package or runtime change was required.

## Notion Updates

- External Memory Providers current map: added Official Documentation and Releases columns; added Rocky / `rocky-vps4`; refreshed live versions and operating notes.
- July 16 External Memory Layer SOP Adjustments: reorganized as a dated historical Results artifact and removed obsolete action-plan framing without dropping the findings, metrics, completed repairs, incident, commits, or later context.
- Hindsight SOP: added current server/integration versions, official release sources, preserved response-first rules, and documented Rocky's separate version boundary.
- Mem0 SOP: rebuilt from current live VPS1/VPS2 behavior and explicit-capture requirements.
- LanceDB SOP: rebuilt from the installed OpenClaw integration and removed unsupported generic index-setting instructions.
- Memory Testing: added a common empirical test battery, metrics, score, cadence, safety gates, provider-specific checks, A/B business-value test, and scorecard template.

## Final Verification

- Hindsight service healthy with database connected after all integration restarts.
- Every updated VPS1 container returned healthy.
- Harry, Frank, and Suzy services returned active.
- Plugin inspection reported Mem0 `1.0.15` and Hindsight `0.10.0` on the updated agents.
- LanceDB inspection reported `2026.7.1`, already current.
- Notion pages were re-fetched after update and the Technical Documentation journal was completed.
