---
name: openai-whisper-api
description: "OpenAI Audio Transcriptions API via curl; gpt-4o-transcribe, mini, diarize, or whisper-1."
homepage: https://platform.openai.com/docs/guides/speech-to-text
metadata:
  {
    "openclaw":
      {
        "emoji": "🌐",
        "requires": { "bins": ["curl", "node"], "env": ["OPENAI_WHISPER_API_KEY"] },
        "primaryEnv": "OPENAI_WHISPER_API_KEY",
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "curl",
              "bins": ["curl"],
              "label": "Install curl (brew)",
            },
          ],
      },
  }
---

# OpenAI transcriptions API

Transcribe audio through `/v1/audio/transcriptions`. Set `OPENAI_BASE_URL` for an OpenAI-compatible proxy or local gateway.

## Quick start

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a
```

Defaults:

- Model: `gpt-4o-transcribe`
- Output: `<input>.txt`

## Useful flags

```bash
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --model gpt-4o-transcribe --out /tmp/transcript.txt
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --model gpt-4o-mini-transcribe
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --model gpt-4o-transcribe-diarize --json
{baseDir}/scripts/transcribe.sh /path/to/audio.ogg --model whisper-1
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --language en
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --prompt "Speaker names: Peter, Daniel"
{baseDir}/scripts/transcribe.sh /path/to/audio.m4a --json --out /tmp/transcript.json
```

Notes:

- Supported upload formats include `mp3`, `mp4`, `mpeg`, `mpga`, `m4a`, `wav`, `webm`.
- The hosted API has a 25 MB upload limit.
- Use diarize for speaker labels; the script sends `chunking_strategy=auto` and rejects `--prompt`.

## API key

Set `OPENAI_WHISPER_API_KEY` through the approved secret manager. This skill does not fall back to the general `OPENAI_API_KEY`.

