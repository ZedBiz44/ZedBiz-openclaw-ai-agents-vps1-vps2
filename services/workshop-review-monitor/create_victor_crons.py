#!/usr/bin/env python3
"""Create Victor-owned, change-only Workshop review jobs."""

import json
import subprocess

CHANNEL_ID = "1546640814573101128"
CONFIG = "/home/node/.openclaw/workshop-review-monitor/config.json"
SCRIPT = "/opt/openclaw/shared/workshop-review-monitor/workshop_change.py"

# Each time is 30 minutes after that agent's system-owned main Workshop cleanup.
SCHEDULES = {
    "amanda": "45 23 * * 0",
    "edith": "17 16 * * 5",
    "gohzed": "8 18 * * 2",
    "grogar": "5 19 * * 4",
    "inga": "23 8 * * 3",
    "maggie": "59 0 * * 2",
    "marsha": "38 19 * * 0",
    "terry": "51 16 * * 6",
    "victor": "42 18 * * 3",
    "vivian": "12 10 * * 5",
    "wilma": "15 5 * * 6",
    "harry": "28 10 * * 3",
    "suzy": "59 10 * * 1",
    "frank": "6 19 * * 3",
    "rocky": "9 19 * * 1",
}


def run(*args):
    completed = subprocess.run(["openclaw", *args], text=True, capture_output=True, timeout=60)
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return completed.stdout


def prompt(agent):
    check = f"python3 {SCRIPT} check --config {CONFIG} --agent {agent}"
    read = f"python3 {SCRIPT} read --config {CONFIG} --agent {agent} --scope workspace --path <relative-path>"
    return f"""Victor, perform the read-only Workshop skill change review for {agent.capitalize()}.

Run this exact check command first:
{check}

If the result is exactly NO_CHANGE or BASELINED, respond with exactly NO_REPLY. Do not post a report.

If the result is a JSON change packet:
- Report every added, changed, or deleted Workshop file shown in the packet.
- Read the supplied changed Workshop text.
- Compare its purpose and instructions with the workspace-skill index in the packet.
- When a workspace skill might be related, read its complete SKILL.md using this command, replacing <relative-path> with its exact indexed path:
{read}
- Explain whether the Workshop change supports, overlaps, duplicates, or conflicts with each related workspace skill.
- Recommend what Jack should review next. Do not edit, merge, delete, move, or create any skill or other file.
- Do not report unrelated skills.

Return a short Discord report with this exact heading:
# Victor Workshop Skill Change Report

Include: Agent, What changed, Related workspace skills, How they connect or conflict, Recommended next decision, and `No skill files were changed by Victor.`"""


def main():
    current = json.loads(run("cron", "list", "--json"))
    existing = {job.get("declarationKey") for job in current.get("jobs", [])}
    for agent, expression in SCHEDULES.items():
        declaration = "zedbiz:workshop-change-review:" + agent
        if declaration in existing:
            print(json.dumps({"agent": agent, "status": "already-present"}))
            continue
        output = run(
            "cron", "add",
            "--declaration-key", declaration,
            "--name", "workshop-change-review-" + agent,
            "--display-name", f"Victor Workshop Change Review — {agent.capitalize()}",
            "--description", f"Change-only read-only review 30 minutes after {agent.capitalize()}'s main Workshop cleanup",
            "--agent", "main",
            "--cron", expression,
            "--tz", "America/Edmonton",
            "--exact",
            "--session", "isolated",
            "--message", prompt(agent),
            "--model", "openai/gpt-5.6-sol",
            "--fallbacks", "openrouter/deepseek/deepseek-v4-flash",
            "--thinking", "medium",
            "--timeout-seconds", "900",
            "--tools", "exec",
            "--announce",
            "--channel", "discord",
            "--to", CHANNEL_ID,
            "--json",
        )
        row = json.loads(output)
        print(json.dumps({"agent": agent, "status": "created", "jobId": row.get("id") or (row.get("job") or {}).get("id")}))


if __name__ == "__main__":
    main()
