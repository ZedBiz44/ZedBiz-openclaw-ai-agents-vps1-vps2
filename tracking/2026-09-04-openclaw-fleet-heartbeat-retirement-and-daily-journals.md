# OpenClaw Fleet Heartbeat Retirement and Daily Journals

Date: 2026-09-04 | Agent: Cody | Status: Deployed and verified

## Purpose

Replace uncontrolled OpenClaw heartbeat turns with clear scheduled work. Every OpenClaw agent now creates or updates its own Notion journal at 6:00 a.m. Mountain Time.

## Agents Changed

- VPS1 Docker: Amanda, Edith, Gohzed, Grogar, Inga, Maggie, Marsha, Terry, Victor, Vivian, and Wilma.
- VPS2 systemd: Harry, Suzy, and Frank.
- VPS4 native: Rocky.
- Ruby was excluded because Ruby runs Hermes, not OpenClaw.

## Heartbeat Changes

For all 15 OpenClaw agents:

- Deleted any workspace file named `HEARTBEAT.md`, case-insensitively.
- Set `agents.defaults.heartbeat.every` to `0m`.
- Replaced Heartbeat (main) scratch with a comment-only, effectively empty value.
- Verified Heartbeat (main) reports `enabled: false` and `status: disabled`.
- Verified zero matching heartbeat files remain.

## Daily Journal Automation

Each agent has one enabled job with declaration key `zedbiz:daily-notion-journal`.

- Schedule: `0 6 * * *`
- Timezone: `America/Edmonton`
- Stagger: zero
- Session: isolated
- Delivery: none after successful internal completion
- Notion destination: that agent's existing inline daily-journal database under the appropriate VPS daily-journals page
- Duplicate control: search the exact date title before creating; update an existing date instead of creating a duplicate
- Content: confirmed work from the preceding 24 hours, available agent memory, recent sessions, and read-only assigned Asana work
- Verification: read the completed Notion page back before the job finishes

## Amanda Pilot

Amanda was tested first.

- Enabled semantic session-memory indexing for Amanda only.
- Limited session visibility to Amanda's own agent sessions.
- Rebuilt Amanda's memory and session index: 212 files.
- Verified Amanda's active LanceDB contained 62 memories.
- Required LanceDB `memory_recall`, memory/session search, PAT Asana identity verification, and read-only assigned-work review.
- First test wrote Notion successfully but the disabled session-memory source caused the run to be marked failed.
- After enabling and indexing Amanda's session memory, the second run completed with `status: ok` and `completionStatus: succeeded`.
- Verified Notion page: https://app.notion.com/p/3d1a3e33d58181ee8f35db5c9e951a2f
- Amanda Asana identity confirmed as `amanda@zedworks.com`, user GID `1213974002925107`, workspace GID `11298561585567`.

## Fleet Verification

Every agent returned all of the following:

- Heartbeat file count: `0`
- Heartbeat cadence: `0m`
- Safe comment-only scratch: `true`
- Heartbeat enabled: `false`
- Heartbeat status: `disabled`
- Journal enabled: `true`
- Journal schedule: `0 6 * * *`
- Journal timezone: `America/Edmonton`
- Journal stagger: `0`

## Rollback

For one agent:

- Change `agents.defaults.heartbeat.every` from `0m` to the approved interval only if heartbeat monitoring is deliberately restored.
- Replace the comment-only scratch with approved monitor instructions.
- Disable or remove that agent's `zedbiz:daily-notion-journal` job if scheduled journals are retired.
- Amanda's pre-session-memory config backup is stored inside Amanda's OpenClaw backup directory as `openclaw.json.before-amanda-session-memory-20260904T1300MDT`.

Do not restore deleted heartbeat instructions without Jack's approval.
