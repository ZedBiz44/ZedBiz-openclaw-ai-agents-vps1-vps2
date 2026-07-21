#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path


def call(url: str, token: str | None = None, payload: dict | None = None) -> tuple[int, dict]:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    if body:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method="POST" if body else "GET")
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--keys-file", type=Path, default=Path("/run/secrets/api_keys.json"))
    parser.add_argument("--agent", default="marsha")
    parser.add_argument("--expect-locked", action="store_true")
    args = parser.parse_args()
    keys = json.loads(args.keys_file.read_text(encoding="utf-8"))
    health_status, health = call(f"{args.base_url.rstrip('/')}/health")
    if health_status != 200 or not health.get("ok"):
        raise SystemExit(f"Health failed: {health_status} {health}")
    unauthorized_status, _ = call(
        f"{args.base_url.rstrip('/')}/v1/allocate",
        payload={
            "request_id": "smoke-test-unauthorized",
            "name_key": "Smoke-Test",
            "z_knowledge_core": "Z1ST",
            "knowledge_lane": "70001",
            "page_type": "Test",
            "requested_by": args.agent,
        },
    )
    if unauthorized_status != 401:
        raise SystemExit(f"Expected unauthenticated request to return 401, got {unauthorized_status}")
    if args.expect_locked:
        locked_status, locked = call(
            f"{args.base_url.rstrip('/')}/v1/allocate",
            token=keys[args.agent],
            payload={
                "request_id": "smoke-test-bootstrap-lock",
                "name_key": "Smoke-Test",
                "z_knowledge_core": "Z1ST",
                "knowledge_lane": "70001",
                "page_type": "Test",
                "requested_by": args.agent,
            },
        )
        if locked_status != 503 or locked.get("detail", {}).get("code") != "bootstrap_required":
            raise SystemExit(f"Bootstrap lock failed: {locked_status} {locked}")
    print(json.dumps({"health": "ok", "unauthorized": "blocked", "bootstrap_lock": "verified" if args.expect_locked else "not_checked"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

