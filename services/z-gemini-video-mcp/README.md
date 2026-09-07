# ZedBiz Gemini Video MCP

This private MCP server gives approved ZedBiz agents one tool for analyzing a public YouTube video with Gemini.

## Tool

- `analyze_youtube_video`

The tool accepts one public HTTPS YouTube URL and an optional business question. It returns a plain-language analysis with timestamps and separates visible or audible observations from presenter claims.

## Security

- The Gemini key is read only from `GEMINI_API_KEY` at runtime.
- The key must come from 1Password and must never be committed or written to logs.
- Only public YouTube URLs are accepted in the first release.
- The request uses `store: false` so the Interactions API does not retain conversation state.
- The tool does not download, modify, or delete the source video.

## Run

```bash
npm ci --omit=dev
GEMINI_API_KEY='resolved-at-runtime' node server.mjs
```

## Test

```bash
npm test
```

## Rollback

Remove the `gemini-video` MCP entry from the agent's OpenClaw configuration, remove the `GEMINI_API_KEY` environment mapping, restart the agent through its approved 1Password-aware launcher, and remove the deployed package only after no agent references it.
