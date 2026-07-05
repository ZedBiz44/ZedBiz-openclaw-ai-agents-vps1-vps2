# 2026-06-22 - Maggie 502 Container Restart

Date: 2026-06-22 MDT | Agent Name: Cody | Status: Fixed And Verified

## Summary

- Investigated why `https://maggie.zbiz.ca` was returning `502 Bad Gateway`.
- Found Caddy was healthy and routing `maggie.zbiz.ca` to `maggie:3008`.
- Found the `maggie` container had exited with code `1` on 2026-06-21 at 15:51:59 MDT.
- Found the container restart policy was `no`, so Maggie stayed offline after the crash.
- Started Maggie and changed only Maggie's restart policy to `unless-stopped`.
- Verified `https://maggie.zbiz.ca` returned `200 OK`.
- Verified Docker reported Maggie as running and healthy.

## Root Cause

- Maggie crashed because the Discord voice WebSocket stack raised an unhandled error:
  - `Error: Unexpected server response: 521`
- Node treated the unhandled voice connection error as fatal and exited the process.
- The public 502 happened because Caddy could no longer reach the stopped Maggie backend.

## Live Fix

- Applied to Maggie only:
  - Updated restart policy to `unless-stopped`.
  - Started the `maggie` container.

## Verification

- Docker status after repair:
  - `Status=running`
  - `Health=healthy`
  - `RestartPolicy=unless-stopped`
  - `RestartCount=0`
- Public endpoint:
  - `https://maggie.zbiz.ca` returned `HTTP/1.1 200 OK`.
- Startup logs confirmed:
  - Gateway loaded and became ready.
  - Active model loaded as `openai/gpt-5.5`.
  - Discord bot resolved as `@maggie-openclaw`.
  - Discord voice bridge rejoined and reported ready.
- Read-only `openclaw doctor` completed with housekeeping and security warnings, but no plugin load errors and no blocker for today's 502 repair.

## Follow-Up Notes

- The restart policy prevents a repeat of the same public outage pattern where a one-off Discord voice crash leaves Maggie stopped.
- A deeper Discord voice hardening pass may still be useful if the 521 voice WebSocket error recurs.
- Doctor reported unrelated housekeeping/security items, including open state/config permissions, orphan transcripts, open Discord DM/group policies, and gateway security warnings.
