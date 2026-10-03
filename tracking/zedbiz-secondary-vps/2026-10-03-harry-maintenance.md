# Harry maintenance and Codex OAuth correction

Date: 2026-10-03 | Agent: Cody | Status: Live verified

## Production result

Harry runs OpenClaw 2026.9.8 with GPT-6.1 Sol through his existing OAuth account and Codex 0.160.0. No paid API default or model fallback is configured. Six external OpenClaw plugins are on 2026.9.8; custom Mem0 remains at its patched compatible version.

Production run `56f603bb-a2e8-40de-abb9-b714b6cd3b47` passed: exact Sol winner, no fallback, successful file proof through bash, zero tool failures. Eight root instruction files match the fresh backup byte-for-byte. Channels, cron and skill settings match the backup. All three VPS2 gateways return HTTP 200. Suzy and Frank remain on 2026.9.4. No further host reboot is required.

## Scope and cause

Jack authorized Harry's OpenClaw, plugin, skill and tool updates plus VPS2 maintenance. Suzy and Frank were not authorized for an individual runtime upgrade. After the initial Sol rejection, Jack supplied the VPS1 discovery and authorized retrying Harry with the newer Codex executable.

OpenClaw 2026.9.8 manages Codex 0.158.0 independently of the global CLI. Updating the global CLI alone did not change the app-server used by OpenClaw. The documented `plugins.entries.codex.config.appServer.command` setting selects `/usr/bin/codex`, verified as 0.160.0 on VPS2.

Harry's existing OAuth profile succeeded in a direct isolated 0.160.0 test with no API credential or fallback. The initial model-access conclusion was incorrect: the older runtime caused the rejection.

## Verified rehearsal

- Candidate OpenClaw 2026.9.8 and six external plugins completed migration in a restored state copy.
- Gateway port 44100; channels, IMAP and cron disabled in the copy.
- Explicit Codex runtime binding for `openai/gpt-6.1-sol`, `/usr/bin/codex` command, OAuth-only OpenAI order, no model fallback, OpenAI/Codex API-key environment variables cleared for the child app-server.
- Run `af17adc8-786c-4fed-b790-70b965f23979` returned an unpredictable file token through one successful bash tool call. Runtime winner was `openai/gpt-6.1-sol`, `fallbackUsed=false`, zero tool failures.
- Existing Mem0 recalled five memories successfully. Custom patched Mem0 1.1.0 and the Qdrant compatibility guard remain; no unverified memory-plugin replacement.
- Custom metadata-first IMAP fetch and notification-framing fixes retained and regression-tested earlier in this maintenance.
- Doctor attempted to merge TOOLS.md into AGENTS.md and disable gifgrep/himalaya. Activation restores existing root workspace Markdown and skill settings from the fresh backup.

## Earlier maintenance

- Seven reviewed custom skills updated: z-ai-skill-developer, z-audio-production, z-biz-plan, z-files-folders, z-video-analysis, z-video-critique, z-video-production. Preserved newer local memory-recording corrections. Four unavailable source repositories were not replaced.
- Shared CLI updates include Codex 0.160.0, Gemini 0.62.0, summarize 0.25.0, mcporter 0.14.2, ntn 0.23.17, npm 12.2.0, gog 0.43.0, camsnap 0.6.0 and xurl 1.3.4.
- VPS2 routine packages and kernel updated. Reboot independently verified October 3 at 09:15 Mountain; kernel 6.8.0-146 active, reboot marker absent. Eight Ubuntu-phased packages retained on their normal schedule.
- Jack authorized cleanup. Verified the September archive checksum, preserved changed/extra files, and removed duplicate restored folders and test dependencies. Recovered about 15 GiB before the new retry backup. Original recovery archives retained; all three agents passed health checks after cleanup.

## Recovery and records

Protected logs, original archive, isolated results and recovery copies are under `/root/cody-harry-maintenance-20261003`. Fresh activation state and program backups are taken with Harry stopped. Activation has automatic restoration on command or startup failure. Suzy and Frank remain untouched.

Technical workstream: [issue 429](https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/429).

Daily journal: [October 3 Cody](https://www.notion.so/3eea3e33d581814bb8a5faa6ae82ef9e).
