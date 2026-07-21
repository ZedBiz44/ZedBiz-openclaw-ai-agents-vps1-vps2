#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import secrets
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate one Z-Code allocator bearer token per agent")
    parser.add_argument("output", type=Path)
    parser.add_argument("agents", nargs="+")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.force:
        parser.error(f"Refusing to overwrite existing file: {args.output}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = {agent.strip().lower(): secrets.token_hex(32) for agent in args.agents}
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.chmod(args.output, 0o600)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

