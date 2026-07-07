#!/usr/bin/env python3
"""Small 1Password Connect helper for Victor.

The default output redacts field values. Use this for metadata-safe create and
update workflows, not for printing secrets back to chat.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_HOST = "http://172.18.0.3:8080"
DEFAULT_TOKEN_FILE = Path.home() / ".openclaw" / "credentials" / "1password-connect-token"
REDACTED = "[redacted]"


def load_secret_value(args: argparse.Namespace) -> str:
    sources = [bool(args.value_file), bool(args.value_env), bool(args.value_stdin)]
    if sum(sources) != 1:
        raise SystemExit("Choose exactly one of --value-file, --value-env, or --value-stdin.")
    if args.value_file:
        return Path(args.value_file).read_text(encoding="utf-8").rstrip("\r\n")
    if args.value_env:
        value = os.environ.get(args.value_env)
        if value is None:
            raise SystemExit(f"Environment variable is not set: {args.value_env}")
        return value
    return sys.stdin.read().rstrip("\r\n")


def load_token(args: argparse.Namespace) -> str:
    token = args.token or os.environ.get("OP_CONNECT_TOKEN") or os.environ.get("ONEPASSWORD_CONNECT_TOKEN")
    if token:
        return token.strip()

    token_file = Path(args.token_file or os.environ.get("OP_CONNECT_TOKEN_FILE") or DEFAULT_TOKEN_FILE).expanduser()
    if not token_file.exists():
        raise SystemExit(f"Connect token file not found: {token_file}")
    return token_file.read_text(encoding="utf-8").strip()


def request_json(args: argparse.Namespace, method: str, path: str, body: object | None = None, auth: bool = True) -> object:
    host = (args.host or os.environ.get("OP_CONNECT_HOST") or DEFAULT_HOST).rstrip("/")
    url = f"{host}{path}"
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["Authorization"] = f"Bearer {load_token(args)}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code} from 1Password Connect: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach 1Password Connect: {exc.reason}") from exc

    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def print_json(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def redact_item(item: dict) -> dict:
    copy = json.loads(json.dumps(item))
    for field in copy.get("fields", []):
        if "value" in field:
            field["value"] = REDACTED
        if "passwordDetails" in field:
            field["passwordDetails"] = REDACTED
    return copy


def command_health(args: argparse.Namespace) -> None:
    print_json(request_json(args, "GET", "/health", auth=False))


def command_vaults(args: argparse.Namespace) -> None:
    print_json(request_json(args, "GET", "/v1/vaults"))


def command_items(args: argparse.Namespace) -> None:
    query = ""
    if args.filter:
        query = "?" + urllib.parse.urlencode({"filter": args.filter})
    print_json(request_json(args, "GET", f"/v1/vaults/{args.vault}/items{query}"))


def command_get_item(args: argparse.Namespace) -> None:
    item = request_json(args, "GET", f"/v1/vaults/{args.vault}/items/{args.item}")
    print_json(item if args.show_values else redact_item(item))


def command_create_password(args: argparse.Namespace) -> None:
    value = load_secret_value(args)
    fields = [{"type": "CONCEALED", "label": args.label, "value": value}]
    if args.username:
        fields.insert(0, {"purpose": "USERNAME", "value": args.username})
    if args.notes:
        fields.append({"purpose": "NOTES", "value": args.notes})

    body = {
        "vault": {"id": args.vault},
        "title": args.title,
        "category": "PASSWORD",
        "tags": args.tag or [],
        "fields": fields,
    }
    item = request_json(args, "POST", f"/v1/vaults/{args.vault}/items", body)
    print_json(redact_item(item))


def command_update_field(args: argparse.Namespace) -> None:
    value = load_secret_value(args)
    item = request_json(args, "GET", f"/v1/vaults/{args.vault}/items/{args.item}")

    target = None
    for field in item.get("fields", []):
        if field.get("label") == args.label or field.get("id") == args.label:
            target = field
            break

    if target is None:
        item.setdefault("fields", []).append({"type": args.field_type, "label": args.label, "value": value})
    else:
        target["value"] = value
        target.setdefault("type", args.field_type)

    updated = request_json(args, "PUT", f"/v1/vaults/{args.vault}/items/{args.item}", item)
    print_json(redact_item(updated))


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", default=None, help=f"Connect host. Default: {DEFAULT_HOST}")
    parser.add_argument("--token", default=None, help="Connect bearer token. Prefer a token file or environment variable.")
    parser.add_argument("--token-file", default=None, help=f"Connect bearer token file. Default: {DEFAULT_TOKEN_FILE}")


def add_value_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--value-file", default=None, help="Read secret value from this file.")
    parser.add_argument("--value-env", default=None, help="Read secret value from this environment variable.")
    parser.add_argument("--value-stdin", action="store_true", help="Read secret value from stdin.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Victor helper for 1Password Connect.")
    add_common_args(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    health = subparsers.add_parser("health", help="Check Connect health without a token.")
    health.set_defaults(func=command_health)

    vaults = subparsers.add_parser("vaults", help="List visible vaults.")
    vaults.set_defaults(func=command_vaults)

    items = subparsers.add_parser("items", help="List items in a vault.")
    items.add_argument("--vault", required=True)
    items.add_argument("--filter", default=None)
    items.set_defaults(func=command_items)

    get_item = subparsers.add_parser("get-item", help="Get an item. Values are redacted by default.")
    get_item.add_argument("--vault", required=True)
    get_item.add_argument("--item", required=True)
    get_item.add_argument("--show-values", action="store_true")
    get_item.set_defaults(func=command_get_item)

    create_password = subparsers.add_parser("create-password", help="Create a PASSWORD item with a concealed field.")
    create_password.add_argument("--vault", required=True)
    create_password.add_argument("--title", required=True)
    create_password.add_argument("--label", required=True)
    create_password.add_argument("--username", default=None)
    create_password.add_argument("--notes", default=None)
    create_password.add_argument("--tag", action="append")
    add_value_args(create_password)
    create_password.set_defaults(func=command_create_password)

    update_field = subparsers.add_parser("update-field", help="Update or add one field on an existing item.")
    update_field.add_argument("--vault", required=True)
    update_field.add_argument("--item", required=True)
    update_field.add_argument("--label", required=True)
    update_field.add_argument("--field-type", default="CONCEALED", choices=["STRING", "EMAIL", "CONCEALED", "URL", "OTP", "DATE", "MONTH_YEAR", "MENU"])
    add_value_args(update_field)
    update_field.set_defaults(func=command_update_field)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
