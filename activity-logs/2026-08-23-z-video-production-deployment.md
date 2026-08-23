# Z Video Production Skill Deployment

Date: 2026-08-23 | Agent: Cody | Status: Verified

## Change

- Deployed `z-video-production` to Terry and Vivian on VPS1.
- Canonical source: `ZedBiz44/z-video-production-Skill`, commit `099f10cf97155765afdccfb846639fa23b770fe3`.
- Runtime paths:
  - `/opt/openclaw/agents/terry/workspace/skills/z-video-production`
  - `/opt/openclaw/agents/vivian/workspace/skills/z-video-production`
- Runtime ownership: `1000:1000` for the `node` user.

## Files

- `SKILL.md`
- `references/advanced-production.md`

## Verification

- Canonical skill validator passed before deployment.
- Both running containers reported the skill as `openclaw-workspace`, eligible, model-visible, user-invocable, command-visible, and platform-compatible.
- The `node` runtime user read both files successfully in each container.
- SHA-256 checksums matched the canonical source on both agents:
  - `SKILL.md`: `8a712b4cd38fb23945459bb79d338913f37faec8e9eccc4222165e20ba0bc263`
  - `advanced-production.md`: `b66543489ef729675a4195fc25b82b611600d7ef91630203459deb2d064e87a9`
- Fresh, no-generation routing requests from Terry and Vivian each returned `z-video-production` without calling a media provider or spending generation credits.

## Rollback

Remove the `z-video-production` folder from each agent workspace and verify that `openclaw skills info z-video-production --json` reports it absent. Neither agent had a previous installation at deployment time.
