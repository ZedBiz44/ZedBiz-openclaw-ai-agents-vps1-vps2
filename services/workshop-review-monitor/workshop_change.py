#!/usr/bin/env python3
"""Detect Workshop skill changes and provide read-only review material to Victor."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

DEFAULT_CONFIG = Path("/home/node/.openclaw/workshop-review-monitor/config.json")
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh", ".js", ".mjs", ".ts"}
MAX_CHANGED_FILE_BYTES = 80_000


def run_json(command):
    completed = subprocess.run(command, text=True, capture_output=True, timeout=90)
    if completed.returncode:
        message = completed.stderr.strip() or completed.stdout.strip() or "reader failed"
        raise RuntimeError(message[:1000])
    return json.loads(completed.stdout)


def source_command(config, agent, action, scope=None, relative=None):
    source = config["agents"][agent]
    if source["type"] == "docker":
        command = [
            "docker", "exec", source["container"], "python3", source["reader"], action,
            "--workshop-root", source["workshop"],
            "--workspace-root", source["workspace"],
        ]
        if action == "read":
            command.extend(["--scope", scope, "--path", relative])
        return command
    command = [
        "ssh", "-F", config["sshConfig"], "-o", "BatchMode=yes",
        source["host"], action, source["remoteAgent"],
    ]
    if action == "read":
        command.extend([scope, relative])
    return command


def scan(config, agent):
    return run_json(source_command(config, agent, "scan"))


def read(config, agent, scope, relative):
    return run_json(source_command(config, agent, "read", scope, relative))


def load_state(path):
    if not path.exists():
        return {"agents": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, 0o600)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def manifest_map(rows):
    return {row["path"]: row for row in rows}


def changed_paths(previous, current):
    before = manifest_map(previous)
    after = manifest_map(current)
    return {
        "added": sorted(set(after) - set(before)),
        "changed": sorted(path for path in set(after) & set(before) if after[path]["sha256"] != before[path]["sha256"]),
        "deleted": sorted(set(before) - set(after)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("baseline", "check", "read"))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--agent")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--scope", choices=("workshop", "workspace"))
    parser.add_argument("--path")
    args = parser.parse_args()

    config_path = Path(args.config)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    state_path = Path(config["stateFile"])
    state = load_state(state_path)

    if args.action == "read":
        if not args.agent or not args.scope or not args.path:
            raise SystemExit("read requires --agent, --scope and --path")
        print(json.dumps(read(config, args.agent, args.scope, args.path), ensure_ascii=False))
        return

    agents = sorted(config["agents"]) if args.all else [args.agent]
    if not agents or agents == [None]:
        raise SystemExit("choose --agent or --all")

    if args.action == "baseline":
        for agent in agents:
            current = scan(config, agent)
            state.setdefault("agents", {})[agent] = {"workshop": current["workshop"]}
            print("BASELINED " + agent)
        save_state(state_path, state)
        return

    agent = agents[0]
    current = scan(config, agent)
    previous_row = state.setdefault("agents", {}).get(agent)
    if previous_row is None:
        state["agents"][agent] = {"workshop": current["workshop"]}
        save_state(state_path, state)
        print("BASELINED")
        return
    changes = changed_paths(previous_row.get("workshop", []), current["workshop"])
    if not any(changes.values()):
        print("NO_CHANGE")
        return

    details = []
    for relative in changes["added"] + changes["changed"]:
        if Path(relative).suffix.lower() not in TEXT_SUFFIXES:
            continue
        current_row = manifest_map(current["workshop"])[relative]
        if current_row["bytes"] > MAX_CHANGED_FILE_BYTES:
            details.append({"path": relative, "content": "[File is too large for the automatic report.]"})
            continue
        details.append(read(config, agent, "workshop", relative))

    packet = {
        "agent": agent,
        "changes": changes,
        "changedFileContents": details,
        "workspaceSkillIndex": current["workspaceSkills"],
    }
    state["agents"][agent] = {"workshop": current["workshop"]}
    save_state(state_path, state)
    print(json.dumps(packet, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
