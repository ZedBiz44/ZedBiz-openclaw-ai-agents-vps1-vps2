#!/usr/bin/env python3
"""Repair OpenRouter fallbacks used by OpenClaw Workshop cleanup jobs."""

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import tempfile

FREE_DEEPSEEK = "openrouter/deepseek/deepseek-v4-flash:free"
PAID_DEEPSEEK = "openrouter/deepseek/deepseek-v4-flash"
GEMINI = "openrouter/google/gemini-3.1-flash-lite"
MAX_TOKENS = 8192


def model_lists(data):
    agents = data.setdefault("agents", {})
    defaults = agents.setdefault("defaults", {})
    yield defaults.setdefault("model", {})
    entries = agents.get("entries", {})
    if isinstance(entries, dict):
        for entry in entries.values():
            if isinstance(entry, dict) and isinstance(entry.get("model"), dict):
                yield entry["model"]


def configure(data, prefer_deepseek=False):
    defaults = data.setdefault("agents", {}).setdefault("defaults", {})
    available = defaults.setdefault("models", {})
    for name in (GEMINI, PAID_DEEPSEEK):
        row = available.setdefault(name, {})
        row.setdefault("params", {})["maxTokens"] = MAX_TOKENS

    changed_lists = 0
    for model in model_lists(data):
        fallbacks = model.get("fallbacks")
        if not isinstance(fallbacks, list):
            continue
        revised = []
        for item in fallbacks:
            if item == FREE_DEEPSEEK or (prefer_deepseek and item == "openrouter/deepseek/deepseek-v4-pro"):
                item = PAID_DEEPSEEK
            if item not in revised:
                revised.append(item)
        if prefer_deepseek and PAID_DEEPSEEK in revised:
            revised.remove(PAID_DEEPSEEK)
            revised.insert(0, PAID_DEEPSEEK)
        if revised != fallbacks:
            model["fallbacks"] = revised
            changed_lists += 1
    return changed_lists


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
    parser.add_argument("--prefer-deepseek", action="store_true")
    args = parser.parse_args()
    path = Path(args.config)
    data = json.loads(path.read_text(encoding="utf-8"))
    original = json.dumps(data, sort_keys=True)
    changed_lists = configure(data, args.prefer_deepseek)
    if json.dumps(data, sort_keys=True) == original:
        print(json.dumps({"changed": False, "fallbackListsChanged": 0}))
        return
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(path.name + ".bak-workshop-route-" + stamp)
    shutil.copy2(path, backup)
    atomic_write(path, data)
    print(json.dumps({
        "changed": True,
        "fallbackListsChanged": changed_lists,
        "backup": str(backup),
        "deepseek": PAID_DEEPSEEK,
        "maxTokens": MAX_TOKENS,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
