#!/usr/bin/env python3
"""Read-only skill-tree scanner used by Victor's Workshop change reviews."""

import argparse
import hashlib
import json
from pathlib import Path

MAX_READ_BYTES = 200_000


def safe_file(root_text, relative):
    try:
        root = Path(root_text).resolve(strict=True)
        candidate = (root / relative).resolve(strict=True)
    except OSError as exc:
        raise ValueError("requested path does not exist") from exc
    if candidate == root or root not in candidate.parents:
        raise ValueError("path is outside the allowed skill folder")
    if not candidate.is_file():
        raise ValueError("requested path is not a file")
    return candidate


def files_under(root_text):
    root = Path(root_text)
    if not root.exists():
        return []
    root = root.resolve(strict=True)
    rows = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        resolved = path.resolve(strict=True)
        if root not in resolved.parents:
            continue
        raw = resolved.read_bytes()
        rows.append({
            "path": resolved.relative_to(root).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "mtimeNs": resolved.stat().st_mtime_ns,
        })
    return rows


def skill_summary(path):
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {"name": path.parent.name, "description": ""}
    name = path.parent.name
    description = ""
    if text.startswith("---"):
        for line in text.splitlines()[1:]:
            if line.strip() == "---":
                break
            key, sep, value = line.partition(":")
            if not sep:
                continue
            if key.strip() == "name":
                name = value.strip().strip("'\"") or name
            elif key.strip() == "description":
                description = value.strip().strip("'\"")
    return {"name": name, "description": description}


def workspace_index(root_text):
    root = Path(root_text)
    if not root.exists():
        return []
    root = root.resolve(strict=True)
    rows = []
    for path in sorted(root.rglob("SKILL.md")):
        if path.is_symlink() or not path.is_file():
            continue
        resolved = path.resolve(strict=True)
        if root not in resolved.parents:
            continue
        summary = skill_summary(resolved)
        rows.append({
            "path": resolved.relative_to(root).as_posix(),
            "name": summary["name"],
            "description": summary["description"],
        })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("scan", "read"))
    parser.add_argument("--workshop-root", required=True)
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--scope", choices=("workshop", "workspace"))
    parser.add_argument("--path")
    args = parser.parse_args()

    if args.action == "scan":
        print(json.dumps({
            "workshop": files_under(args.workshop_root),
            "workspaceSkills": workspace_index(args.workspace_root),
        }, separators=(",", ":")))
        return

    if not args.scope or not args.path:
        raise SystemExit("read requires --scope and --path")
    root = args.workshop_root if args.scope == "workshop" else args.workspace_root
    path = safe_file(root, args.path)
    raw = path.read_bytes()
    if len(raw) > MAX_READ_BYTES:
        raise SystemExit("file exceeds the read limit")
    print(json.dumps({
        "path": args.path,
        "scope": args.scope,
        "content": raw.decode("utf-8", errors="replace"),
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
