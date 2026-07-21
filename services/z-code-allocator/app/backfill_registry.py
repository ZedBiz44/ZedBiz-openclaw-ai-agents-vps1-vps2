from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from app.database import Database
from app.mirror_worker import NotionMirror


def record_rows(database: Database) -> list[dict[str, Any]]:
    with database.connect() as connection:
        rows = connection.execute(
            """
            SELECT r.*, t.name_key, t.z_knowledge_core, t.knowledge_lane, t.topic_identifier
            FROM records r
            JOIN topics t ON t.id = r.topic_pk
            ORDER BY r.id
            """
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["topic_identifier"] = f"{row['topic_identifier']:06d}"
        item["record_suffix"] = f"{row['record_suffix']:03d}"
        result.append(item)
    return result


def notion_text(page: dict[str, Any], property_name: str) -> str:
    value = page.get("properties", {}).get(property_name, {})
    value_type = value.get("type")
    if value_type in {"title", "rich_text"}:
        return "".join(
            part.get("plain_text") or part.get("text", {}).get("content", "")
            for part in value.get(value_type, [])
        )
    if value_type == "select":
        selected = value.get("select")
        return selected.get("name", "") if selected else ""
    if value_type == "url":
        return value.get("url") or ""
    return ""


def registry_pages(mirror: NotionMirror) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        payload: dict[str, Any] = {"page_size": 100}
        if cursor:
            payload["start_cursor"] = cursor
        response = mirror.request("POST", f"/databases/{mirror.database_id}/query", payload)
        pages.extend(response.get("results", []))
        if not response.get("has_more"):
            return pages
        cursor = response.get("next_cursor")
        if not cursor:
            raise RuntimeError("Notion returned has_more without next_cursor")


def registry_summary(pages: list[dict[str, Any]]) -> dict[str, Any]:
    codes = [notion_text(page, "Z-Code") for page in pages]
    codes = [code for code in codes if code]
    counts = Counter(codes)
    return {
        "rows": len(pages),
        "codes": codes,
        "duplicates": sorted(code for code, count in counts.items() if count > 1),
        "sources": dict(sorted(Counter(notion_text(page, "Source") or "Blank" for page in pages).items())),
    }


def backfill(
    database: Database,
    mirror: NotionMirror,
    *,
    z_code: str | None = None,
    limit: int | None = None,
    dry_run: bool = False,
    backup_path: str | None = None,
) -> dict[str, Any]:
    authoritative = record_rows(database)
    authoritative_by_code = {record["z_code"]: record for record in authoritative}
    bootstrap = [record for record in authoritative if record["request_id"].startswith("bootstrap:")]
    before_pages = registry_pages(mirror)
    before = registry_summary(before_pages)
    if before["duplicates"]:
        raise RuntimeError(f"Registry already contains duplicate Z-Codes: {before['duplicates'][:10]}")
    if backup_path:
        backup = Path(backup_path)
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(json.dumps(before_pages, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    existing = set(before["codes"])
    candidates = [record for record in bootstrap if record["z_code"] not in existing]
    if z_code:
        candidates = [record for record in candidates if record["z_code"] == z_code]
        if z_code not in authoritative_by_code:
            raise RuntimeError(f"Z-Code is not present in SQLite: {z_code}")
        if not authoritative_by_code[z_code]["request_id"].startswith("bootstrap:"):
            raise RuntimeError(f"Z-Code is not a bootstrap record: {z_code}")
    if limit is not None:
        candidates = candidates[:limit]

    created = 0
    if not dry_run:
        for record in candidates:
            mirror.request(
                "POST",
                "/pages",
                {
                    "parent": {"database_id": mirror.database_id},
                    "properties": mirror.properties(record, "bootstrap_backfill", source="Bootstrap"),
                },
            )
            created += 1

    after_pages = registry_pages(mirror) if not dry_run else before_pages
    after = registry_summary(after_pages)
    after_codes = set(after["codes"])
    authoritative_codes = set(authoritative_by_code)
    bootstrap_codes = {record["z_code"] for record in bootstrap}
    return {
        "dry_run": dry_run,
        "authoritative_records": len(authoritative),
        "bootstrap_records": len(bootstrap),
        "registry_before": before["rows"],
        "selected": len(candidates),
        "created": created,
        "registry_after": after["rows"],
        "source_counts": after["sources"],
        "duplicate_z_codes": after["duplicates"],
        "missing_bootstrap": sorted(bootstrap_codes - after_codes),
        "missing_authoritative": sorted(authoritative_codes - after_codes),
        "extra_registry": sorted(after_codes - authoritative_codes),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill historical SQLite records into Notion Z-Code-Registry")
    parser.add_argument("--z-code")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backup-path")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    token = os.getenv("NOTION_API_TOKEN", "").strip()
    database_id = os.getenv("NOTION_ZCODE_DATABASE_ID", "").strip()
    if not token or not database_id:
        raise RuntimeError("NOTION_API_TOKEN and NOTION_ZCODE_DATABASE_ID are required")
    database = Database(os.getenv("ZCODE_DATABASE_PATH", "/data/zcode.db"))
    database.initialize()
    result = backfill(
        database,
        NotionMirror(token, database_id),
        z_code=args.z_code,
        limit=args.limit,
        dry_run=args.dry_run,
        backup_path=args.backup_path,
    )
    print(json.dumps(result, sort_keys=True))
    if result["duplicate_z_codes"] or result["extra_registry"]:
        raise SystemExit(2)
    if args.require_complete and (result["missing_bootstrap"] or result["missing_authoritative"]):
        raise SystemExit(3)


if __name__ == "__main__":
    main()
