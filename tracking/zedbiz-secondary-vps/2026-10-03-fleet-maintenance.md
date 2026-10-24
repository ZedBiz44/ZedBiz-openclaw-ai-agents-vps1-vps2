# VPS2 fleet maintenance — 2026-10-03

Suzy and Frank now run OpenClaw 2026.9.8 using GPT-6.1 Sol through their existing OAuth profile and the explicitly selected Codex 0.160.0 executable. Harry's successful pilot was applied sequentially. No paid API default or model fallback is configured.

## Live verification

- Suzy run `c35b40f5-55e7-4481-96a1-19f95bbfe30e`: exact Sol model, file proof and Hindsight recall, two successful tools, no fallback.
- Frank run `24626186-5699-48c8-9453-b9bf2ae7065d`: same checks passed.
- All three gateways returned HTTP 200; Discord probes passed; original instruction files and channel, cron and skills configuration matched backups.
- Six official external plugins per agent updated to 2026.9.8. Suzy and Frank Hindsight updated to 0.13.0 and live recall passed.
- Reviewed skill refresh: Harry ten, Suzy nine, Frank nine. Current Asana and WordPress skill sources matched. Duplicate z-record-knowledge backup folders removed from discovery and preserved outside the skills directory. Discovery lists 88/88/87 skills respectively.
- Shared Asana service updated to MCP SDK 1.32.0 and Asana 3.3.0; typecheck/build passed. Each agent's protected account identity, 47-tool listing and read-only task retrieval passed before completion.
- File Browser 2.63.23, yt-dlp 2026.08.19 and standalone Playwright 1.63 installed. Both File Browser instances returned HTTP 200. Playwright launched installed Chromium and passed a page test. Global npm tools report no outdated packages; snaps current.
- Server runs kernel 6.8.0-146-generic following today's earlier reboot. No reboot marker or failed systemd services. Removed unused kernel 139 and related packages; retained current 146 and fallback 142.

## Deliberate exceptions

- Eight Ubuntu packages remain phased by Ubuntu. No eligible ordinary upgrade is outstanding; phased rollout was not forced.
- Harry's custom patched Mem0 1.1.0 retained pending compatibility work for 1.2.1.
- Asana service retains jsdom 27.4 rather than untested major 30.1.1. Latest Asana still reports four high dependency audit findings in the Babel/braces/chokidar chain; npm's suggested force fix is a breaking downgrade to Asana 1.0.5 and was not applied. Audit decreased from nine findings to four; this is not a claim of complete security remediation.
- Local customized skills and Ubuntu-managed Python packages were preserved. Skills with no declared upstream cannot be certified latest.

## Recovery and cleanup

Full quiescent pre-upgrade state/program backups retained for all three agents; SQLite integrity verified. Exact duplicate activation node_modules trees removed only after recursive comparison. September pre94 program/state folders compressed and tar-compared before originals are removed; final cleanup evidence records the completed targets and recovered space.

## Records

- Issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/429
- PR: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/pull/438
- Cody daily journal: https://www.notion.so/3eea3e33d581814bb8a5faa6ae82ef9e

Raw protected logs and recovery material remain under `/root/cody-{agent}-maintenance-20261003`; published evidence excludes credentials and full model prompts.
