#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path


OLD = """edith.zbiz.ca {
    reverse_proxy edith:3011
}
"""

NEW = """edith.zbiz.ca {
    # Z-Code Allocator pilot route. handle_path strips the public prefix.
    handle_path /_zedbiz-zcode/* {
        reverse_proxy z-code-allocator:8788
    }

    handle {
        reverse_proxy edith:3011
    }
}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("caddyfile", type=Path)
    args = parser.parse_args()
    text = args.caddyfile.read_text(encoding="utf-8")
    if NEW in text:
        print("Caddy route already present")
        return 0
    if text.count(OLD) != 1:
        raise SystemExit("Expected the exact Edith Caddy block once; no change made")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = args.caddyfile.with_name(f"{args.caddyfile.name}.bak-zcode-{stamp}")
    shutil.copy2(args.caddyfile, backup)
    args.caddyfile.write_text(text.replace(OLD, NEW), encoding="utf-8")
    print(f"Caddy route added; backup={backup.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

