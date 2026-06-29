# 2026-06-29 - Maggie And Gohzed Outage Diagnosis

Date: 2026-06-29 MDT | Agent Name: Cody | Status: Diagnose

## Summary

- Investigated why Maggie was offline today.
- Reviewed yesterday's Gohzed outage pattern against the live VPS1 state and Victor's Notion job description.
- No server config was changed during this pass.

## Live Status

- VPS1 host responded as `srv1404026`.
- Maggie was running and healthy at the end of the check.
- Gohzed was running and healthy at the end of the check.
- Public checks returned `200` for both `https://maggie.zbiz.ca/` and `https://gohzed.zbiz.ca/`.
- Host memory was healthy during the check, with about 9 GiB available.

## Maggie Finding

- Maggie crashed at about `2026-06-29 06:18 MDT`.
- Logs showed DNS failures during Discord voice reconnect:
  - `getaddrinfo ENOTFOUND api.openai.com`
  - `getaddrinfo ENOTFOUND c-ewr08-a2a3bbb8.discord.media`
- The Discord voice connection emitted an unhandled error and Node exited.
- This was not confirmed as an OOM kill from the evidence checked.
- Maggie was started again at about `2026-06-29 15:16 MDT`.

## Gohzed Finding

- Gohzed logs support the prior report of a forced kill because the log contains a plain `Killed` line before restart.
- This is consistent with Ruby's reported exit-code-137/OOM-kill explanation.
- Gohzed was healthy during this follow-up check.

## Resilience Gap

- Maggie and Gohzed both currently have `restart: "no"` in their Compose source files.
- The same `restart: "no"` setting is present across the VPS1 OpenClaw agent Compose files.
- A previous live-only restart-policy change can be lost when Compose recreates containers.
- The durable control surface is the Compose file under `/opt/openclaw/agents/{agent}/docker-compose.yml`.

## Recommendation

- Victor should own this as part of VPS1 caretaker duties.
- Maggie one-agent test was approved and completed.
- Proposed next action, pending user confirmation:
  - Roll the same Compose restart policy across the remaining agent fleet.
  - Add or verify Uptime Kuma monitors for agent public URLs.
  - Add a lightweight daily Victor check for stopped containers, non-healthy containers, and high memory pressure.

## Maggie One-Agent Restart Policy Test

- Backed up Maggie's Compose file at `/opt/openclaw/agents/maggie/docker-compose.yml.bak-20260629-1528`.
- Changed `/opt/openclaw/agents/maggie/docker-compose.yml` from `restart: "no"` to `restart: "unless-stopped"`.
- Ran Compose config validation and recreated only the `maggie` container.
- Verified Maggie after recreate:
  - Docker status: `running`
  - Docker health: `healthy`
  - Restart policy: `unless-stopped`
  - Public URL: `HTTP/1.1 200 OK`
- Tested restart behavior:
  - `docker kill maggie` did not auto-restart because Docker treats that as a manual operator stop.
  - Maggie was immediately started again and returned to healthy.
  - Killing the internal `openclaw` process inside the container did trigger Docker's restart policy.
  - Maggie returned to `running` and `healthy` with `restarts=1`.
  - Local health endpoint returned OK and the public URL returned `HTTP/1.1 200 OK`.

## Result

- The one-agent test passed.
- The durable fix needs to be made in each agent's Compose file, not just by changing a live container policy.

## Fleet Rollout

- User approved rolling the same restart policy across the remaining VPS1 agents.
- Updated the remaining ten agent Compose files from `restart: "no"` to `restart: "unless-stopped"`:
  - Amanda
  - Edith
  - Gohzed
  - Grogar
  - Inga
  - Marsha
  - Terry
  - Victor
  - Vivian
  - Wilma
- Maggie already had the tested `restart: "unless-stopped"` setting.
- Created timestamped Compose backups for the rollout batch:
  - `/opt/openclaw/agents/{agent}/docker-compose.yml.bak-20260629-1548`
- Ran Compose config validation for each updated agent before recreating it.
- Recreated each updated agent one at a time.

## Fleet Verification

- Verified all eleven VPS1 agents are running, healthy, and using restart policy `unless-stopped`.
- Docker restart count after rollout:
  - Maggie: `1` from the earlier crash-style restart-policy proof.
  - All other agents: `0` after recreate.
- Public URL verification returned `HTTP/1.1 200 OK` for:
  - `https://amanda.zbiz.ca/`
  - `https://edith.zbiz.ca/`
  - `https://gohzed.zbiz.ca/`
  - `https://grogar.zbiz.ca/`
  - `https://inga.zbiz.ca/`
  - `https://maggie.zbiz.ca/`
  - `https://marsha.zbiz.ca/`
  - `https://terry.zbiz.ca/`
  - `https://victor.zbiz.ca/`
  - `https://vivian.zbiz.ca/`
  - `https://wilma.zbiz.ca/`
