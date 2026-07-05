# 2026-06-13 - Marsha Live Voice Plugin Fix

Date | Author | Status: 2026-06-13 | Cody | Partial - Voice Presence Fixed, Live Hearing Blocked

## Summary

- Rechecked Marsha after Discord showed outbound TTS/voice-file output worked, but live voice-channel presence/listening was still missing.
- Confirmed Marsha already had Discord voice config, OpenAI realtime voice support, and native commands enabled.
- Confirmed missing piece was not only the `voice-call` plugin path.
- The Discord `/vc join` command is registered as a channel-picker option, and raw pasted channel IDs can fail in Discord's UI with `A channel id specified is invalid`.
- Patched Marsha only on VPS1, installed the official compatible `@openclaw/voice-call` plugin, added voice auto-join/follow config, switched to `stt-tts` fallback mode, restarted Marsha, and verified she joined the voice channel.
- Continued testing showed that voice presence and raw UDP receive are working, but OpenClaw is still not converting incoming Discord voice packets into speaking/capture/transcript events.

## Fix Applied

- Added explicit `channels.discord.voice.mode = "agent-proxy"`.
- Enabled:
  - `plugins.entries.voice-call.enabled = true`
  - `skills.entries.voice-call.enabled = true`
  - `plugins.entries.talk-voice.enabled = true`
- Installed:
  - `@openclaw/voice-call@2026.6.5`
- Added:
  - `channels.discord.voice.autoJoin = [{ guildId: "1491589465175621794", channelId: "1515154998856515796" }]`
  - `channels.discord.voice.allowedChannels = [{ guildId: "1491589465175621794", channelId: "1515154998856515796" }]`
  - `channels.discord.voice.followUsersEnabled = true`
  - `channels.discord.voice.followUsers = ["discord:864290378395025478"]`
- Switched final working mode to:
  - `channels.discord.voice.mode = "stt-tts"`
- Configured OpenAI TTS fallback:
  - `gpt-4o-mini-tts`
  - `cedar`
- Restarted only:
  - `marsha`

## Verification

- Marsha returned to healthy after restart.
- `voice-call` plugin is installed, enabled, and loaded.
- `voice-call` skill is eligible and not disabled.
- OpenAI provider remains loaded with speech, realtime transcription, and realtime voice provider support.
- Discord provider remains loaded.
- Discord permissions for voice channel `1515154998856515796` include:
  - Connect
  - Speak
  - Use Application Commands
  - Send Voice Messages
  - Use VAD
- Voice status confirms JackZ is currently in voice channel `1515154998856515796`.
- Initial `agent-proxy` attempts failed with:
  - `Failed to start Discord realtime voice: Unexpected server response: 500`
- After switching to `stt-tts`, logs showed:
  - `voice: joined guild=1491589465175621794 channel=1515154998856515796 mode=stt-tts`
- Voice status for Marsha bot user confirms she is in voice channel `1515154998856515796`.

## Final State

- Marsha is joined to the Discord voice channel using `stt-tts`.
- Marsha is unmuted and undeafened.
- JackZ is in the same voice channel, unmuted and undeafened.
- Raw Discord voice UDP packets reach Marsha's container while Jack speaks.
- OpenClaw still emits no `speaking`, `capture`, `receive`, or `transcript` events, so Marsha cannot hear/respond from live voice yet.
- Realtime `agent-proxy` is not the working mode on this pass because the OpenAI realtime bridge returned a server-side 500.
- `openai-whisper` and `sag` were not required for this fix; OpenAI STT is configured via `tools.media.audio`.
- DAVE-off was tested again under OpenClaw `2026.6.6` and reverted because it destabilized voice join.
- Marsha now runs from a mounted OpenClaw `2026.6.6` runtime path with matching Discord and Codex plugins installed at startup; direct health returns `{"ok":true,"status":"live"}`.

## Remaining Blocker

- The remaining blocker is inside the Discord voice receiver / DAVE / `@discordjs/voice` receive layer.
- Practical next path is an upstream OpenClaw Discord receiver fix or a local fallback receiver that can subscribe/decode incoming Discord voice packets without relying on the missing speaking/capture event path.

## GitHub

- Commented the full change log and final verification on GitHub Issue #7.
- Added follow-up comment with raw packet proof and the remaining live-hearing blocker.
