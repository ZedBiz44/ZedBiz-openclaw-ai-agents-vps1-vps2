# Z-Code Allocator Fleet Runtime Repair

Date: 2026-07-21  
Agent: Cody  
GitHub issue: #79

## Incident

Victor correctly refused to publish a new xAI Business record because his running OpenClaw runtime did not have an authorized `request-z-code` identity. Fleet inspection found that other agents also had incomplete installations.

## Root Cause

The allocator client has four inseparable runtime requirements:

- The canonical `request-z-code` skill in the agent's active skill directory.
- `ZCODE_ALLOCATOR_URL` loaded into the running process.
- An individual `ZCODE_API_KEY` registered to that agent.
- `ZCODE_AGENT_NAME` matching the authenticated key owner.

Copying Marsha's key to Victor produced HTTP 409: `requested_by must match the authenticated agent`. This was correct allocator behavior and demonstrated that keys are agent-specific.

On VPS2, Frank, Harry, and Suzy already had correct values in their protected `.env` files, but systemd was not loading those files into the running services.

## Repair Applied

### VPS1

- Added unique registered keys and runtime settings for missing agents.
- Installed the canonical skill for each affected agent.
- Added compose environment pass-through where missing.
- Recreated affected agent containers.
- Restarted the allocator after updating its protected key registry.

Active VPS1 allocator clients are Grogar, Edith, GoHzed, Terry, Maggie, Inga, Marsha, Vivian, Victor, Amanda, and Wilma.

The internal allocator endpoint is `http://z-code-allocator:8788`.

### VPS2

Added these systemd drop-ins:

- `/etc/systemd/system/openclaw-frank.service.d/zcode-allocator.conf`
- `/etc/systemd/system/openclaw-harry.service.d/zcode-allocator.conf`
- `/etc/systemd/system/openclaw-suzy.service.d/zcode-allocator.conf`

Each drop-in loads the corresponding `/root/.openclaw-<agent>/.env`. Systemd was reloaded and all three services were restarted.

## Verification

All eleven VPS1 agents passed:

- Healthy agent runtime.
- Correct `ZCODE_AGENT_NAME`.
- Allocator health HTTP 200.
- Authenticated Name-Key lookup.
- Eligible and model-visible `request-z-code` skill.

Frank, Harry, and Suzy passed:

- Active systemd service.
- Skill present.
- URL, key, and matching identity loaded into the running process.
- Authenticated Name-Key lookup.

Victor completed a real reservation under his own identity. Synthetic test code `Z1ST-80001-100002-010` was immediately marked `abandoned` with a test-only reason and must never be reused.

## Repair Checklist

When an agent reports that the allocator is missing or unauthorized:

- Verify the exact running agent, not only files on disk.
- Confirm skill presence and eligibility.
- Confirm all three environment variables are loaded without printing the key.
- Confirm the identity matches the key owner.
- Check allocator health.
- Run an authenticated lookup.
- Restart or recreate the agent after any environment change.
- Run one real allocation only when required; immediately abandon synthetic test reservations.

Never bypass the allocator, invent a Z-Code, or share another agent's credential.
