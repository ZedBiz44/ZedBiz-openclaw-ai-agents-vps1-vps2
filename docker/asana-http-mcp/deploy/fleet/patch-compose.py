#!/usr/bin/env python3
"""Add or update one agent's persistent standard Asana HTTP MCP sidecar."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml


IMAGE = "zedbiz/asana-http-mcp:1.1.0-standard-read-navigation"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("compose_file", type=Path)
    parser.add_argument("agent")
    parser.add_argument("--backup-suffix", required=True)
    args = parser.parse_args()

    compose_path = args.compose_file.resolve()
    backup_path = compose_path.with_name(
        f"{compose_path.name}.{args.backup_suffix}"
    )
    if not backup_path.exists():
        shutil.copy2(compose_path, backup_path)

    data = yaml.safe_load(compose_path.read_text(encoding="utf-8"))
    services = data.setdefault("services", {})
    if args.agent not in services:
        raise SystemExit(f"Main service {args.agent!r} is missing")

    sidecar = f"{args.agent}-asana-mcp"
    main_service = services[args.agent]
    depends_on = main_service.get("depends_on")
    if depends_on is None:
        depends_on = {}
    elif isinstance(depends_on, list):
        depends_on = {name: {"condition": "service_started"} for name in depends_on}
    elif not isinstance(depends_on, dict):
        raise SystemExit("Unsupported depends_on format")
    depends_on[sidecar] = {"condition": "service_healthy"}
    main_service["depends_on"] = depends_on

    services[sidecar] = {
        "build": {"context": "./asana-http-mcp"},
        "image": IMAGE,
        "container_name": sidecar,
        "restart": "unless-stopped",
        "mem_limit": "384m",
        "pids_limit": 64,
        "networks": ["openclaw"],
        "environment": {
            "ASANA_ACCESS_TOKEN": "${ASANA_ACCESS_TOKEN}",
            "MCP_AUTH_TOKEN": "${ASANA_ACCESS_TOKEN}",
            "MCP_ALLOWED_HOSTS": f"{sidecar},localhost,127.0.0.1",
            "MCP_MAX_SESSIONS": "64",
            "MCP_SESSION_TTL_MS": "900000",
            "PORT": "8080",
        },
    }

    rendered = yaml.safe_dump(
        data,
        sort_keys=False,
        default_flow_style=False,
        width=120,
    )
    yaml.safe_load(rendered)
    compose_path.write_text(rendered, encoding="utf-8")
    print(f"Configured {sidecar} in {compose_path}")


if __name__ == "__main__":
    main()
