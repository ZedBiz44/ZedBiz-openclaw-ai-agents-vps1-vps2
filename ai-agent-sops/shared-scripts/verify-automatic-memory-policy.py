#!/usr/bin/env python3
"""Read-only verification for the approved automatic-memory configuration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--agents", required=True)
    parser.add_argument("--provider", choices=("mem0", "lancedb", "hindsight"), required=True)
    parser.add_argument("--require-native-sidecar", action="store_true")
    args = parser.parse_args()

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    entries = config.get("plugins", {}).get("entries", {})
    checks: dict[str, bool] = {}

    if args.provider == "mem0":
        provider = entries.get("openclaw-mem0", {}).get("config", {})
        checks["autoCapture"] = provider.get("autoCapture") is True
        checks["autoRecall"] = provider.get("autoRecall") is True
        checks["skillsModeRemoved"] = "skills" not in provider
    elif args.provider == "lancedb":
        provider = entries.get("memory-lancedb", {}).get("config", {})
        checks["autoCapture"] = provider.get("autoCapture") is True
        checks["autoRecall"] = provider.get("autoRecall") is True
    else:
        provider = entries.get("hindsight-openclaw", {}).get("config", {})
        checks["autoRetain"] = provider.get("autoRetain") is True
        checks["autoRecall"] = provider.get("autoRecall") is True

    if args.require_native_sidecar:
        checks["memoryCoreSidecar"] = entries.get("memory-core", {}).get("enabled") is True

    agents_text = Path(args.agents).read_text(encoding="utf-8")
    checks["automaticPolicy"] = "## Automatic Memory Capture Standard" in agents_text
    labels = {"mem0": "Mem0", "lancedb": "LanceDB", "hindsight": "Hindsight"}
    checks["providerNamedEarly"] = (
        f"active external conversational-memory provider is {labels[args.provider]}" in agents_text[:4000]
    )
    checks["noReviewMemoryBan"] = not any(
        line.startswith("-")
        and "review-only" in line.lower()
        and any(marker in line.lower() for marker in ("memory write", "provider-memory", "local-memory", "writing to the provider"))
        for line in agents_text.splitlines()
    )

    print(json.dumps(checks, sort_keys=True))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

