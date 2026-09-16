#!/usr/bin/env python3
"""Give weekly Workshop cleanup a rooted OpenAI fallback without changing the primary."""

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import tempfile

TERRA = "openai/gpt-5.6-terra"
LUNA = "openai/gpt-5.6-luna"
CODEX = "codex"
OPENCLAW = "openclaw"


def configure(data):
    defaults = data["agents"]["defaults"]
    model = defaults["model"]
    primary = model["primary"]
    fallbacks = model["fallbacks"]
    models = defaults["models"]

    if primary not in models:
        raise ValueError(f"Primary model entry is missing: {primary}")
    if TERRA not in models or LUNA not in models:
        raise ValueError("Terra and Luna model entries are required")

    primary_runtime = models[primary].get("agentRuntime", {}).get("id")
    if primary_runtime != CODEX:
        raise ValueError(f"Primary must remain on Codex, found: {primary_runtime}")

    if primary == TERRA:
        model["fallbacks"] = [item for item in fallbacks if item != TERRA]
    elif TERRA not in fallbacks:
        raise ValueError("Terra must already be present in the fallback chain")

    if LUNA not in model["fallbacks"]:
        raise ValueError("Luna must already be present in the fallback chain")

    if primary != TERRA:
        models[TERRA].setdefault("agentRuntime", {})["id"] = OPENCLAW
    models[LUNA].setdefault("agentRuntime", {})["id"] = OPENCLAW

    if models[primary].get("agentRuntime", {}).get("id") != CODEX:
        raise AssertionError("Primary runtime changed unexpectedly")

    return {
        "primary": primary,
        "primaryRuntime": CODEX,
        "terraRuntime": models[TERRA].get("agentRuntime", {}).get("id"),
        "lunaRuntime": models[LUNA].get("agentRuntime", {}).get("id"),
        "fallbacks": model["fallbacks"],
    }


def atomic_write(path, data):
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, path.stat().st_mode & 0o777)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    path = Path(args.config)
    data = json.loads(path.read_text(encoding="utf-8"))
    original = json.dumps(data, sort_keys=True)
    result = configure(data)

    changed = json.dumps(data, sort_keys=True) != original
    result["changed"] = changed
    if args.check or not changed:
        print(json.dumps(result, separators=(",", ":")))
        return

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(path.name + ".bak-rooted-openai-" + stamp)
    shutil.copy2(path, backup)
    atomic_write(path, data)
    result["backup"] = str(backup)
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
