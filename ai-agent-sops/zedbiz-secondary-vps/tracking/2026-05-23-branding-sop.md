# Agent Branding Implementation (Native Install)

**Date:** 2026-05-23
**Agents:** Harry, Suzy
**Server:** Secondary VPS (2.24.104.80)

## Overview
Implemented per-agent branding for the native OpenClaw install using an Nginx reverse proxy. Because the native install shares global UI files, we cannot modify the global files without affecting all agents. The proxy intercepts requests for static assets (favicon, manifest, index.html) and serves branded versions, then proxies the rest to the OpenClaw backend.

## What Was Done
1. Generated custom avatars and favicons for Harry (blue) and Suzy (teal).
2. Created branded `index.html` and `manifest.webmanifest` for each agent.
3. Uploaded assets to `/opt/openclaw-branding/[agent-name]/` on the VPS.
4. Configured Nginx to listen on new ports:
   - Harry: `18880` (proxies to `18789`)
   - Suzy: `18881` (proxies to `18790`)
5. Updated `openclaw.json` for both agents to include the new ports in `controlUi.allowedOrigins`.
6. Restarted services and verified branding.

## Known Limitations
The browser tab title will revert to "OpenClaw Control" once the JS app loads the `/chat` route. This is a limitation of the compiled SPA. The favicon, manifest, and initial load title remain branded.

## Documentation Updated
The full step-by-step process has been added as Phase 5 to the [Agent-Creation-SOP-V2](https://www.notion.so/ee1a3e33d58183948bd58119d92c7d01) in Notion.
