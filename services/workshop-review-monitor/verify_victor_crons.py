#!/usr/bin/env python3
"""Verify Victor's Workshop change-review cron jobs without printing prompts."""

import datetime as dt
import json
import subprocess
from zoneinfo import ZoneInfo

from create_victor_crons import CHANNEL_ID, SCHEDULES


def main():
    raw = subprocess.run(
        ["openclaw", "cron", "list", "--json"],
        check=True,
        text=True,
        capture_output=True,
        timeout=60,
    ).stdout
    jobs = json.loads(raw).get("jobs", [])
    keyed = {job.get("declarationKey"): job for job in jobs}
    valid = True
    for agent, expression in SCHEDULES.items():
        key = "zedbiz:workshop-change-review:" + agent
        job = keyed.get(key, {})
        payload = job.get("payload", {})
        delivery = job.get("delivery", {})
        schedule = job.get("schedule", {})
        next_ms = job.get("nextRunAtMs") or job.get("state", {}).get("nextRunAtMs")
        next_run = None
        if next_ms:
            next_run = dt.datetime.fromtimestamp(
                next_ms / 1000, tz=dt.timezone.utc
            ).astimezone(ZoneInfo("America/Edmonton")).isoformat(timespec="minutes")
        row_valid = bool(job) and all(
            (
                job.get("enabled") is True,
                job.get("agentId") == "main",
                schedule.get("expr") == expression,
                schedule.get("tz") == "America/Edmonton",
                schedule.get("staggerMs") == 0,
                payload.get("model") == "openai/gpt-5.6-sol",
                payload.get("fallbacks") == ["openrouter/deepseek/deepseek-v4-flash"],
                payload.get("toolsAllow") == ["exec"],
                delivery.get("mode") == "announce",
                delivery.get("channel") == "discord",
                delivery.get("to") == CHANNEL_ID,
            )
        )
        valid = valid and row_valid
        print(json.dumps({
            "agent": agent,
            "jobId": job.get("id"),
            "schedule": expression,
            "nextMountain": next_run,
            "valid": row_valid,
        }, separators=(",", ":")))
    print(json.dumps({"count": len(SCHEDULES), "valid": valid}, separators=(",", ":")))
    raise SystemExit(0 if valid else 1)


if __name__ == "__main__":
    main()
