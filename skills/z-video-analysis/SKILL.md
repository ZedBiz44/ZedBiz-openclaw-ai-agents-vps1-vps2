---
name: z-video-analysis
description: Analyze an approved public YouTube video with Gemini and report audio, visuals, timestamps, claims, and uncertainty.
---

# Z Video Analysis

Use the `gemini-video.analyze_youtube_video` tool when the user asks you to watch, understand, summarize, inspect, or answer questions about a public YouTube video.

## Required Input

- Obtain one public YouTube URL.
- Obtain the user's question or use the standard full-video analysis.
- Do not use private, unlisted, client-only, or internal video in the first release.

## Run the Analysis

- Send the public YouTube URL to `gemini-video.analyze_youtube_video`.
- Include the user's specific question when provided.
- Do not claim success until the tool returns a substantive answer.
- Do not retry automatically when a submitted request times out or its acceptance is unknown. Report the problem and request review.

## Return the Result

Clearly separate:

- What was heard or seen directly in the video.
- What the presenter said or claimed.
- What was checked using another reliable source.
- What remains uncertain.

Also include:

- The source URL.
- The part of the video inspected.
- Useful timestamps.
- The Gemini model used.
- Available usage information.

Never treat a presenter claim as independently verified unless another reliable source was actually checked.

## Stop Rules

- Stop if the URL is not public YouTube content.
- Stop if the user asks to upload private or restricted video.
- Stop if the tool reports a missing credential or unclear paid submission state.
- Never reveal, print, or request the Gemini key.
