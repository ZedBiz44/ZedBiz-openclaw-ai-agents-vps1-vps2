# VPS2 component maintenance — 2026-10-18

Authorized scope: host packages, installed tools, Hindsight and custom Asana dependencies. Preserve native service layout, model/account routing, Harry's Mem0 customizations and existing schedules.

- Seventeen host packages updated, including Node 24.22.0 and 1Password CLI 2.41.0. No reboot marker or failed system units after the update. Docker is not installed on this native-agent host.
- Codex 0.163.0, Gemini CLI 0.64.0, summarize 0.25.2, mcporter 0.15.0 and ntn 0.23.20 deployed. Frank's staged pilot passed before global activation; all three actual agent capability checks passed after activation.
- Custom Asana service retains its 47-tool catalog. SDK 1.32.1, Express 5.3.0 and jsdom 30.1.3 passed typecheck/build, isolated real-identity testing and a production dependency audit with zero reported vulnerabilities. Frank, Harry and Suzy each retrieved their own identity after deployment.
- Frank and Suzy's Hindsight plugin updated to exact version 1.0.0, using the shared upgraded VPS1 API. Existing bank configuration preserved. Both recalled existing memories automatically and fetched Notion through their own runtimes. Frank captured accurate maintenance information and recalled it in a fresh session after restart.
- Harry retains Mem0 1.2.1 and its existing compatibility guard. A real `mem0_search` and own Asana identity call passed.

## Evidence and recovery

Protected evidence lives under `/root/cody-components-20261018`; preceding matched core backups remain under `/root/cody-vps2-20261018`. Host configuration, prior global tools, Asana source/build and stopped-service Hindsight plugin/state backups were retained. Core and tool acceptance used GPT-6.1-Sol without fallback.

Initial Hindsight CLI test lacked provider context and correctly skipped recall. Channel plus explicit synthetic operator sender context proved the actual automatic path without external messages. The existing OpenClaw `provenance-invalid` warning remains; no trust bypass was used and trusted native memory capability is not claimed.

Frank's active prompt contained a removed ingest command. A one-line compatibility amendment preserves authoritative exact values and uses automatic memory for compact pointers; no unavailable tool is invented. All other live prompt bytes were preserved. A fresh-session behavioral check passed role, approval, knowledge-routing, exact-URL and read-only GitHub boundaries. Prompt content is maintained in Notion, not duplicated here. Historical Notion full-prompt content is explicitly marked unsuitable for redeployment without reconciliation.

## Final command tools and authentication repair

- GitHub CLI 2.102.0 installed from the checksum-verified official Debian package. Frank's actual private-repository API read passed.
- GOG 0.45.0 activated. Harry/Suzy initially failed because default discovery selected an empty credential directory. The old 0.43 binary reproduced the same failure. Explicit existing per-agent stores passed OAuth refresh and Drive reads. The new `scripts/gog-native-wrapper.sh` selects those existing stores and loads their existing keyring environment; no credentials or accounts were changed or copied. Operator reads passed for all three agents, followed by actual Harry and Suzy runtime reads. Protected logs include initial failures and corrected proofs.
- Himalaya 2.2.1 installed from the checksum-verified upstream archive. Version passed. Existing native CLI account configuration was absent, so CLI email functionality is not claimed; OpenClaw's separately configured built-in mail integration was preserved.
- Final services were active with zero restarts; schedule counts remained Frank 8, Harry 8, Suzy 9. Point-in-time cgroup memory excluding inactive file cache was approximately 2.10 GB, 2.34 GB and 2.05 GB respectively. Harry had 24 historical `high` events, but no max-limit or OOM events. These readings are snapshots, not a sustained leak test.
