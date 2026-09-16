#!/usr/bin/env python3
"""Restricted SSH entry point for read-only remote skill inspection."""

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

CONFIG = Path("/etc/zedbiz-workshop-reader.json")
READER = "/usr/local/lib/zedbiz-workshop-reader/remote_reader.py"


def fail(message):
    print(json.dumps({"error": message}, separators=(",", ":")))
    raise SystemExit(2)


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    try:
        parts = shlex.split(os.environ.get("SSH_ORIGINAL_COMMAND", ""))
    except ValueError:
        fail("invalid command")
    if len(parts) < 2 or parts[0] not in ("scan", "read"):
        fail("allowed commands are scan and read")
    action, agent = parts[:2]
    roots = config.get("agents", {}).get(agent)
    if not roots:
        fail("agent is not allowed")
    command = [
        sys.executable,
        READER,
        action,
        "--workshop-root",
        roots["workshop"],
        "--workspace-root",
        roots["workspace"],
    ]
    if action == "read":
        if len(parts) != 4 or parts[2] not in ("workshop", "workspace"):
            fail("read requires an allowed scope and relative path")
        command.extend(["--scope", parts[2], "--path", parts[3]])
    elif len(parts) != 2:
        fail("scan accepts only an agent name")
    completed = subprocess.run(command, check=False)
    raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
