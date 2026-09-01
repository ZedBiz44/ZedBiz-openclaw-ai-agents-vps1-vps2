# VPS1 OpenClaw 2026.8.2 Control UI Branding Correction

## Problem

- The 2026.8.2 Control UI showed the fallback name `Assistant` and a generic letter or OpenClaw mascot on VPS1 agents.
- The pre-upgrade hook only patched static Control UI files under `/app/dist/control-ui`.

## Root cause

- OpenClaw 2026.8.2 reads the agent display name from `agents.entries.main.identity`.
- The sidebar image is resolved from a conventional icon inside the active workspace and cached when the gateway starts.
- VPS1 stored the avatar outside the workspace, so the new identity and workspace-icon paths were empty.

## Correction

- Set each agent's supported runtime identity with `openclaw agents set-identity`.
- Copy each existing branded image to the workspace avatar and conventional icon paths.
- Add the same idempotent correction to every agent's `post-start.sh` so rebuilds preserve it.
- Restart one container at a time and require a healthy result before continuing.

## Validation standard

- Exact `identityName` returned by `openclaw agents list --json`.
- Workspace avatar and icon files exist and are non-empty.
- Agent container is healthy after the restart.
- Browser proof on the one-agent test includes the branded icon, agent name, agent-specific message placeholder, and agent-specific browser title.

## Automation

- `scripts/repair-vps1-control-ui-branding.sh`

## Completed evidence

- GitHub issue: `#239`
- Amanda one-agent browser proof: branded image, `Amanda`, `Message Amanda`, and `Amanda — OpenClaw` all rendered after the supported identity and workspace-icon correction.
- Fleet read-back: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma returned their exact `identityName`.
- Every agent has one persistent post-start correction marker and non-empty workspace icon/avatar files.
- Every agent returned `healthy` with Docker restart count `0` after the controlled sequential restart.
