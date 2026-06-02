# 2026-06-02 - Incident - All Agents Tool Call Failures + Terry Unresponsive

## Summary
- **Date:** 2026-06-02 Mountain Time
- **Reported By:** Jack Zenert
- **Agent Diagnosing:** Manus
- **System:** main-vps, OpenClaw
- **Severity:** p1-high
- **Status:** open - awaiting Jack confirmation before fix

## What Happened

- **Symptom:** All OpenClaw agents on main-vps (Vivian, main, Terry, Inga, and others) are failing tool calls. Red error banners visible in Control UI for every agent. Terry is completely unresponsive -- returns "[assistant turn failed before producing content]" with no tool output at all.
- **Error messages observed in Control UI:**
  - `findmnt -no SOURCE,FSTYPE,OPTIONS / ~/.openclaw/workspace (agent) failed`
  - `run openclaw tasks (agent) failed`
  - `netstat -ltnup (agent) failed`
  - `ss -ltnup || ss -ltnp (agent) failed`
  - `run openclaw config (agent) failed`
  - `run openclaw secrets (agent) failed`
  - `jq 'walk(if type=="object" then with_entries(...)' (agent) failed`
  - `systemctl status ssh sshd --no-pager (agent) failed`
  - `run test /etc/apt/apt.conf.d/20auto-upgrades ... (agent) failed`
- **Terry specific:** `[assistant turn failed before producing content]` -- agent fails before generating any reply.
- **Affected agents:** All agents on main-vps (Terry, Vivian, main/Inga, Amanda, Wilma, Marsha, GohZed, Grogar, Maggie, Victor).

## Diagnosis

### Root Cause 1 (PRIMARY -- Terry and all agents): deepseek-v4-pro reasoning_effort conflict

**Evidence from Terry logs:**
```
error=LLM request failed: provider rejected the request schema or tool payload.
rawError=400 "reasoning_effort" and "reasoning.effort" are both provided with conflicting values
model=deepseek/deepseek-v4-pro provider=openrouter
decision=candidate_failed reason=format next=none
```

**What is happening:**
- All agents have `openrouter/deepseek/deepseek-v4-pro` set as their default model.
- OpenClaw is sending BOTH `reasoning_effort` (old parameter name) AND `reasoning.effort` (new parameter name) in the same API request to OpenRouter.
- OpenRouter/DeepSeek V4 Pro rejects this with HTTP 400.
- The failover logic has no fallback configured (`next=none`), so the entire agent turn fails.
- Terry's `thinkingDefault` is set to `minimal` -- this triggers the reasoning parameter to be sent, which causes the conflict.
- The fallback model is not configured, so there is no recovery path.

**Why it started now:** This is a version mismatch issue. Agent containers are running OpenClaw `v2026.5.28` but the **core gateway is still on `v2026.4.15`**. The gateway is the component that constructs the API payload. The older gateway version sends both the legacy `reasoning_effort` and the new `reasoning.effort` fields simultaneously when thinking mode is active, which the updated DeepSeek V4 Pro API now rejects.

### Root Cause 2 (SECONDARY -- all agents): Tool calls failing for system commands

**Evidence from screenshots:**
- Commands like `findmnt`, `netstat`, `ss`, `systemctl`, `openclaw tasks`, `openclaw config`, `openclaw secrets`, `jq` are all failing.
- These are host-level or privileged commands that the agents run as part of health check skills.
- The agents are containerized and do not have access to host-level tools (`ss`, `ufw`, `nft`, `systemctl`).
- This is a **known limitation** already noted in the health check output: "Host-level tools are limited from inside the container."
- These failures are expected behavior for containerized agents -- they are NOT new failures. They appear as errors in the UI because the health check skill attempts these commands.
- The `openclaw tasks/config/secrets` failures are likely a side effect of Root Cause 1 -- the agent fails before it can execute the openclaw CLI tool.

### Root Cause 3 (SECONDARY -- gateway): Version mismatch

| Component | Version |
|---|---|
| Agent containers (all agents) | `v2026.5.28` |
| Core OpenClaw gateway | `v2026.4.15` |
| Latest available image | `v2026.5.28` |

The gateway is 6 weeks behind the agents. The gateway log itself shows: `update available (latest): v2026.5.28 (current v2026.4.15)`.

### Root Cause 4 (TERTIARY -- gateway): 126% CPU spike

The gateway container `core-openclaw-gateway-1` was observed at **126.83% CPU** during the docker stats snapshot. This is abnormally high and may be related to repeated failed LLM requests looping or the version mismatch causing retry storms.

### What Was Ruled Out
- VPS resources: Memory is fine (6.1GB used of 15.6GB), disk is fine (9% used). Not a resource issue.
- Container crashes: All agent containers show `healthy` status with 0 restarts. Not a container crash issue.
- Network: Gateway is reachable, Caddy is running, agents are accessible via their ports.
- OpenRouter availability: `deepseek/deepseek-v4-pro` model IS listed as available on OpenRouter API.

## Proposed Fix

### Fix 1 (IMMEDIATE -- resolves Terry and all agent failures): Update gateway to v2026.5.28

The core gateway needs to be updated from `v2026.4.15` to `v2026.5.28` to match the agent containers. This should resolve the `reasoning_effort` dual-parameter conflict.

**Commands:**
```bash
# On main-vps
cd /opt/openclaw/core
# Update the gateway image tag in docker-compose.yml from 2026.4.15 to 2026.5.28
# Then recreate the container
docker compose pull
docker compose up -d --force-recreate
```

**Note:** The `latest` image tag is already `v2026.5.28` and has been pulled to the VPS.

### Fix 2 (IMMEDIATE -- resolves Terry specifically): Add fallback model

Even after the gateway update, Terry has no fallback model configured (`next=none`). If deepseek-v4-pro fails for any reason, Terry hard-fails. Add a fallback model to Terry's config.

### Fix 3 (OPTIONAL -- reduces noise): Suppress host-level tool failures in health check

The health check skill attempts `systemctl`, `ss`, `ufw`, `nft` which will always fail inside a container. These should be wrapped in error handling or removed from the containerized agent health check skill.

## Verification Plan
- After gateway update: Test Terry with a simple "hi" message -- should respond.
- After gateway update: Run health check skill on one agent -- tool call errors should be gone.
- Monitor gateway CPU -- should drop back to normal levels.

## Prevention
- Add gateway version check to the standard health check SOP.
- When updating agent container images, always update gateway at the same time.
- Add a fallback model to all agent configs so a single model failure does not hard-fail the agent.

## Links
- GitHub Issue: TBD
- Notion page: Technical Documentation
- Related commit: this file
