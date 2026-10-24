# Gemini audio and video file access for the full fleet

Date: 2026-09-21 | Agent: Cody | Status: Deployed and verified; source review pending

## Authorized outcome

Jack requested immediate Gemini video-analysis access for Cody, all OpenClaw agents, and Ruby. Issue: https://github.com/ZedBiz44/ZedBiz-openclaw-ai-agents-vps1-vps2/issues/396

The existing 0.1 service accepted only public YouTube URLs. Version 0.2 adds actual local video and audio files, configurable visual sampling and targeted intervals. Existing main models, other MCP connections, and existing skills are preserved.

## Live verification

- Created a 9-second MP4 with three solid scenes (red, blue, green), no visible text, and spoken words: "Copper lantern. The number is seventeen. This sentence exists only in the sound."
- Terry passed first before remaining runtimes were connected. The actual sound-only phrase and scene order were independently returned by Gemini.
- VPS1: Amanda, Edith, GohZed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, Wilma passed real sound/picture analysis.
- VPS2: Harry, Frank, Suzy passed real sound/picture analysis using credentials from the live gateway child after the protected `op run` parent.
- VPS4: Rocky passed real sound/picture analysis as the OpenClaw runtime user.
- VPS3: Ruby passed Hermes-native MCP discovery and real sound/picture analysis as the Hermes runtime user. A fresh Ruby/Grok chat called `mcp__gemini_video__analyze_media_file` and returned the correct scene order and speech (session `20260921_200352_f45270`).
- Cody passed registered launcher discovery and real sound/picture analysis on the Windows-local MP4. The installed generic CLI helper also passed an audio-only WAV test.
- A fresh Terry gateway chat called `gemini-video__analyze_media_file` and returned the correct scenes and speech (session `gemini-file-proof-20260921`).
- All successful file calls returned `uploaded_file_cleanup: deleted` and `stored_by_interactions_api: false`.
- Eight automated tests pass. Dependency audit reported zero vulnerabilities.

## Repairs and bounded failures

- The old tool filter exposed only `analyze_youtube_video`; every OpenClaw config now includes `analyze_media_file` as well.
- Several read-only OpenClaw CLI probes encountered transient SQLite snapshot instability. Retried read-only discovery without resubmitting the paid analysis; subsequent probes succeeded.
- The VPS2 systemd main process is `op`, not the gateway child holding resolved Gemini credentials. Verified the actual child environment without printing any secret.
- Ruby's existing 1Password account cannot access the shared vault and cannot create items in her vault. The stored special management account could not inspect that vault either. No new secret record was created. Used Ruby's already-working SSH route to VPS1; the dedicated Gemini credential stays in process memory.
- Shell CRLF and nested quoting faults were corrected by using saved scripts. They did not indicate an analysis failure; the successful paid call was retained rather than repeated.

## Limits and rollback

See the service README for paths, runtime routes, inputs, current-session Cody helper, and rollback. The tool samples frames; it does not claim continuous human playback or perfect lip-sync verification. File limit is 500 MiB. Calls consume the existing Gemini project's usage. No plan, subscription, billing setting, quota, main agent model, or unrelated integration was changed.

Notion journal: https://app.notion.com/p/3e2a3e33d5818106a9e0f4fb69ceb238

Ruby gateway was refreshed only after its live control socket reported zero active agents. The new process returned to running state with API, Telegram, Discord and email connected. No agent task was interrupted.
