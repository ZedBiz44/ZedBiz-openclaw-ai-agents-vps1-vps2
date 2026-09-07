# Marsha OpenAI Whisper Dedicated-Key Repair

Date: 2026-09-07 MDT  
Added by: Cody  
Agent receiving change: Marsha  
VPS or system: VPS1, OpenClaw 2026.8.2  
Related issue: #270  
Approved skill source: `skills/openai-whisper-api/` from pull request #279

## Purpose

Make Marsha's hosted OpenAI transcription skill use only `OPENAI_WHISPER_API_KEY`. The bundled OpenClaw copy still selected the general `OPENAI_API_KEY`, even though Marsha's dedicated Whisper key was already present and correctly resolved.

## Live Finding

- Marsha was healthy.
- Her protected environment file already contained safe references for both OpenAI variables.
- The running container had both values resolved. They were checked only by one-way fingerprints; no secret value was printed.
- The bundled `openai-whisper-api` skill reported `OPENAI_API_KEY` as its primary variable.
- No workspace override existed.

## Change

Installed the approved workspace override at:

`/opt/openclaw/agents/marsha/workspace/skills/openai-whisper-api/`

The installed script:

- requires `OPENAI_WHISPER_API_KEY`;
- sends only `OPENAI_WHISPER_API_KEY` to the OpenAI transcription API;
- remains executable; and
- preserves the upstream OpenClaw attribution and licence record.

The workspace is already mounted into Marsha's container, so no container restart or environment-file change was required.

## Commands and Attempts

- Copied the approved `SKILL.md`, `UPSTREAM.md`, and `scripts/transcribe.sh` files to a temporary location.
- The first install attempt stopped before changing the target because the container's minimal `sh` does not support an `ERR` trap.
- Repeated the bounded install with Bash, which Marsha's container already uses.
- Set the installed files to the `node` user and group with read-safe permissions; kept the helper executable.
- Removed temporary staging files after the successful install.

## Verification

- Marsha remained healthy with zero restart required.
- OpenClaw reports the skill source as `openclaw-workspace`.
- OpenClaw reports the skill as Ready, visible to the model, and available as a command.
- OpenClaw reports `OPENAI_WHISPER_API_KEY` as the primary environment variable.
- The deployed `SKILL.md` and `transcribe.sh` hashes match the approved source from pull request #279.
- A missing-key test stopped safely with `Missing OPENAI_WHISPER_API_KEY`.
- A real `gpt-4o-mini-transcribe` API request succeeded.
- A fresh Marsha session discovered the skill, ran it, created the requested output file, used three tool calls with zero failures, and replied `PASS`.
- `openclaw config validate` passed. One unrelated disabled memory-plugin warning remains unchanged.

## Rollback

No earlier workspace override existed. To roll back this change, remove only:

`/opt/openclaw/agents/marsha/workspace/skills/openai-whisper-api/`

The bundled OpenClaw skill will then become active again. No environment or container rollback is needed.

## Result

Marsha now uses the dedicated Whisper credential through `OPENAI_WHISPER_API_KEY` for hosted OpenAI transcription.
