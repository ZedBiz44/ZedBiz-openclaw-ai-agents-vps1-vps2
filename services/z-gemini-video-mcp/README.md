# ZedBiz Gemini Video MCP 0.2.0

`analyze_media_file` reviews an authorized file accessible to the calling runtime. It sends the real video with its audio (or an audio-only file) to Gemini, returns timestamped findings and usage, and deletes the temporary Google File upload. Model: `gemini-3.8-flash`; Interactions storage disabled; SDK automatic retries disabled. This is sampled audiovisual analysis, not continuous human playback or a guarantee of lip-sync accuracy.

Inputs: absolute `file_path`, optional `question` (4000 characters), video `fps` (0.1–24, default 4), optional `start_seconds` and `end_seconds`. Supported video includes MP4, MOV, WebM, MPEG, AVI and WMV. Supported audio includes MP3, WAV, M4A, AAC, FLAC and OGG. Maximum file size: 500 MiB. Private source uploads need the user's authorization. Do not infer visuals or sound from the filename or transcript.

`analyze_youtube_video` remains available for public HTTPS YouTube URLs. A Drive sharing page is not a local media file: retrieve the authorized file through the approved Drive route first.

## Runtime connections

- VPS1: `/opt/openclaw/shared/tools/z-gemini-video-mcp-v020/server.mjs`, using each agent's protected Gemini environment.
- VPS2: `/opt/openclaw-shared/tools/z-gemini-video-mcp-v020/server.mjs`, using the protected gateway child environment after `op run`.
- Rocky: `/home/openclaw/.local/share/openclaw-tools/z-gemini-video-mcp-v020/server.mjs`.
- Ruby: `/opt/data/tools/z-gemini-video-mcp-v020/launch-ssh.mjs`. Reuses her existing SSH key and pinned known-hosts file to obtain the dedicated Gemini credential from Terry's protected runtime. The credential is captured in memory and passed to the local server; video files are uploaded from Ruby, not copied to VPS1. No new key or vault grant was created. VPS1 availability is a dependency.
- Cody: `$CODEX_HOME/tools/z-gemini-video-mcp/launch-cody.mjs`, registered as global MCP server `gemini-video`, with startup timeout 30 seconds and tool timeout 600 seconds. Reuses Cody's existing authorized SSH access to the same protected credential. Files are uploaded directly from Cody's machine. VPS1 availability is a dependency.

## Current-session Codex fallback

An already running Codex task may not refresh its native MCP tool catalog. It can call the installed service immediately with `call.mjs`; no app restart is needed for this fallback. Write a JSON request with `name: "analyze_media_file"` and `arguments: {"file_path": "absolute/path/to/video.mp4", "question": "..."}`. Run `node <tool-directory>/call.mjs <request.json>` with `ZEDBIZ_GEMINI_SSH_KEY` pointing to the existing approved key path. The helper prints only the analysis result. Fresh Codex sessions discover the registered MCP tools.

## Verification and recovery

`npm test` covers MCP discovery, invalid URL rejection, file checks, interval/sampling request construction, cleanup, and no retry after a failed analysis request. `verify.mjs <server-or-launcher> [media-file]` checks discovery and optionally makes one real metered call. Never rerun a submitted analysis automatically after an uncertain result. Resolve credentials through the real runtime, not an ordinary SSH shell.

OpenClaw config backups end in `.before-gemini-files-20260921`; Ruby's config has the same suffix. The original 0.1 tool folders remain intact. Restore only the affected Gemini config entry from the backup to roll back, then reload that runtime's MCP connection. Do not overwrite unrelated configuration changes. Removing Cody's `gemini-video` MCP entry reverses its registration.
