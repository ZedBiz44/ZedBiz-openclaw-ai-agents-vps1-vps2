#!/usr/bin/env python3
"""Print a concise, secret-free audit of system-owned Workshop cleanup jobs."""

import argparse
import datetime as dt
import json
import subprocess
from zoneinfo import ZoneInfo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True)
    args = parser.parse_args()
    raw = subprocess.run(
        ["openclaw", "cron", "list", "--json"],
        check=True,
        text=True,
        capture_output=True,
        timeout=60,
    ).stdout
    jobs = json.loads(raw).get("jobs", [])
    selected = [
        job for job in jobs
        if str(job.get("declarationKey", "")).startswith("skill-collection-review:")
    ]
    for job in sorted(selected, key=lambda item: item.get("declarationKey", "")):
        next_ms = job.get("nextRunAtMs") or job.get("state", {}).get("nextRunAtMs")
        local = None
        weekly = None
        if next_ms:
            moment = dt.datetime.fromtimestamp(next_ms / 1000, tz=dt.timezone.utc).astimezone(
                ZoneInfo("America/Edmonton")
            )
            local = moment.isoformat(timespec="minutes")
            weekly = moment.strftime("%A %H:%M")
        print(json.dumps({
            "agent": args.agent,
            "identity": job.get("agentId"),
            "jobId": job.get("id"),
            "enabled": job.get("enabled"),
            "weeklyMountain": weekly,
            "nextMountain": local,
            "lastStatus": job.get("lastRunStatus") or job.get("state", {}).get("lastRunStatus"),
        }, separators=(",", ":")))


if __name__ == "__main__":
    main()
