# Frank OpenAI Codex OAuth Plugin Diagnosis

Date: 2026-06-11 | Agent: Cody | Status: Diagnose - feedback only

## Context

- User reported Frank failing during OpenAI Codex OAuth setup.
- Screenshot command:
  - `export HOME=/root/.openclaw-frank`
  - `export OPENCLAW_STATE_DIR=/root/.openclaw-frank`
  - `export OPENCLAW_CONFIG_PATH=/root/.openclaw-frank/openclaw.json`
  - `/opt/openclaw-frank/node_modules/.bin/openclaw models auth login --provider openai-codex --device-code`
- Observed error: `No provider plugins found. Install one via openclaw plugins install`.

## Prior VPS2 Evidence Checked

- VPS2 uses folder-based `systemd`, not Docker-per-agent.
- Frank install path previously validated as `/opt/openclaw-frank`.
- Frank state path previously validated as `/root/.openclaw-frank`.
- Prior successful doctor pattern required exporting `HOME`, `OPENCLAW_STATE_DIR`, and `OPENCLAW_CONFIG_PATH` before running the OpenClaw binary from `/opt/openclaw-frank`.
- Prior curated tool/plugin set included `@openclaw/codex` and `@openclaw/discord`.
- Prior reusable installer path was `/root/curated-vps2-tool-installer.sh`.

## Current Diagnostic Read

- This is not yet an OAuth failure.
- The CLI is failing before OAuth because no provider plugin is discoverable.
- Likely causes to verify on the live host:
  - `@openclaw/codex` is missing from `/root/.openclaw-frank/npm`.
  - The CLI invocation is not loading Frank's plugin/tool directory.
  - Plugin metadata or config registration was removed or disabled by a doctor/update cleanup.
  - Frank's current OpenClaw core and `@openclaw/codex` versions are mismatched.

## Live Verification Attempt

- A read-only SSH check was attempted against the previously recorded VPS2 IP `2.24.104.80`.
- SSH stopped with a host-key change warning, so no bypass was attempted.
- A second saved host entry `187.77.210.223` denied the available key.
- No server changes were made.

## Recommended Next Step

- Confirm the current correct VPS2 host/IP or access route.
- On Frank, verify:
  - `systemctl show openclaw-frank -p Environment -p ExecStart`
  - `ls -ld /opt/openclaw-frank /root/.openclaw-frank /root/.openclaw-frank/npm`
  - `npm ls --prefix /root/.openclaw-frank/npm --depth=0`
  - presence/version of `/root/.openclaw-frank/npm/node_modules/@openclaw/codex/package.json`
  - whether `/root/curated-vps2-tool-installer.sh` still exists and passes `bash -n`
- If `@openclaw/codex` is missing or mismatched, reinstall/update the curated tool for Frank first, then retry OAuth.
