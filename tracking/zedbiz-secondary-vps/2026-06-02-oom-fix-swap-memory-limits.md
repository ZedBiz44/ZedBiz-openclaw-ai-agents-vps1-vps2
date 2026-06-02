# VPS2 Incident: OOM Kill + Memory/Swap Fix
**Date:** 2026-06-02
**Logged by:** Manus
**Severity:** Medium (agents unresponsive, auto-recovered via systemd restart)

---

## Incident Summary

Harry, Edith, and Suzy all stopped responding after being instructed to run the `healthcheck` skill. Multiple `/restart` commands and hard refreshes did not resolve the issue on the first attempt. On the second attempt (sequential run), Harry was OOM-killed by the Linux kernel mid-execution.

---

## Root Cause

Two compounding issues:

### Issue 1 -- Health Check Skill: Parallel Tool Calls (First Hang)
The `healthcheck` skill instructed the agent to fire 8 `exec_command` calls simultaneously, including three with `yield_time_ms=30000`. This saturated the agent's tool call budget and locked the turn. The agent appeared frozen but was not crashed. All three agents (Harry, Edith, Suzy) hit this simultaneously.

### Issue 2 -- OOM Kill: Hard Memory Ceiling Too Low (Second Crash)
Each agent service had `MemoryMax=1.5G` hardcoded in its systemd unit file. When Harry ran the health check sequentially (as instructed on second attempt), the commands `openclaw security audit --deep` and `openclaw gateway status --deep` spiked Harry's process to 1.5 GB -- hitting the hard ceiling exactly. The Linux OOM killer terminated the process.

**Key log entry:**
```
Jun 02 12:38:25 srv1677638 systemd[1]: openclaw-harry.service: A process of this unit has been killed by the OOM killer.
Jun 02 12:38:25 srv1677638 systemd[1]: openclaw-harry.service: Failed with result 'oom-kill'.
Jun 02 12:38:25 srv1677638 systemd[1]: openclaw-harry.service: Consumed 41.950s CPU time, 1.5G memory peak
```

Systemd auto-restarted Harry (restart counter reached 7).

**Note:** The Hostinger dashboard showed normal RAM usage (~1.5-2 GB) because it shows averages, not instantaneous spikes. The OOM kill was a spike event, not sustained pressure.

---

## Fix Applied

### 1. Added 4 GB Swap File
```bash
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
sysctl vm.swappiness=10
echo 'vm.swappiness=10' >> /etc/sysctl.conf
```
- Swap is persistent across reboots via `/etc/fstab`
- `vm.swappiness=10` means swap is only used as a last resort, not aggressively

### 2. Raised Memory Limits -- Harry, Edith, Suzy
Drop-in override files created at `/etc/systemd/system/openclaw-[agent].service.d/memory.conf`:

```ini
[Service]
MemoryMax=2.5G
MemoryHigh=2.2G
```

Applied via `systemctl daemon-reload` -- no service restarts required.

| Setting | Before | After |
|---|---|---|
| `MemoryMax` | 1.5 GB | 2.5 GB |
| `MemoryHigh` | not set | 2.2 GB |

---

## Current State After Fix

| Item | Status |
|---|---|
| Swap | 4 GB active, 0 used |
| Harry | active (running) |
| Edith | active (running) |
| Suzy | active (running) |
| Memory available | ~2.4 GB |

---

## Pending

- Health check skill `--deep` flag patch deferred -- Jack wants to test agents first before patching the skill.

---

## Files Changed on VPS2

- `/swapfile` -- new 4 GB swap file
- `/etc/fstab` -- swap entry added
- `/etc/sysctl.conf` -- `vm.swappiness=10` added
- `/etc/systemd/system/openclaw-harry.service.d/memory.conf` -- new drop-in
- `/etc/systemd/system/openclaw-edith.service.d/memory.conf` -- new drop-in
- `/etc/systemd/system/openclaw-suzy.service.d/memory.conf` -- new drop-in
