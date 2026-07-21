from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from app.database import Database, utc_now


NOTION_VERSION = "2022-06-28"


class NotionMirror:
    def __init__(self, token: str, database_id: str):
        self.token = token
        self.database_id = database_id

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        for attempt in range(6):
            request = urllib.request.Request(
                f"https://api.notion.com/v1{path}",
                data=body,
                method=method,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Notion-Version": NOTION_VERSION,
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                if attempt < 5 and (exc.code == 429 or exc.code >= 500):
                    retry_after = exc.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else min(2**attempt, 15)
                    time.sleep(max(delay, 0.5))
                    continue
                raise RuntimeError(f"Notion API {exc.code}: {detail[:500]}") from exc
        raise RuntimeError("Notion API retry limit exhausted")

    def find_page(self, z_code: str) -> str | None:
        result = self.request(
            "POST",
            f"/databases/{self.database_id}/query",
            {"filter": {"property": "Z-Code", "rich_text": {"equals": z_code}}, "page_size": 1},
        )
        rows = result.get("results", [])
        return rows[0]["id"] if rows else None

    @staticmethod
    def text(value: str | None) -> dict[str, Any]:
        return {"rich_text": [{"type": "text", "text": {"content": value or ""}}]}

    def properties(self, record: dict[str, Any], event_type: str, source: str = "Allocator") -> dict[str, Any]:
        properties: dict[str, Any] = {
            "Name-Key": {"title": [{"type": "text", "text": {"content": record["name_key"]}}]},
            "Z-Code": self.text(record["z_code"]),
            "Z-Knowledge-Core": self.text(record["z_knowledge_core"]),
            "Knowledge-Lane": self.text(record["knowledge_lane"]),
            "Topic-Identifier": self.text(record["topic_identifier"]),
            "Record-Suffix": self.text(record["record_suffix"]),
            "Page-Type": self.text(record["page_type"]),
            "Status": {"select": {"name": str(record["status"]).capitalize()}},
            "Reserved-By": self.text(record["reserved_by"]),
            "Request-ID": self.text(record["request_id"]),
            "Last-Event": self.text(event_type),
            "Last-Synced": {"date": {"start": utc_now()}},
            "Source": {"select": {"name": source}},
        }
        if record.get("notion_url"):
            properties["Notion-URL"] = {"url": record["notion_url"]}
        return properties

    def upsert(
        self,
        record: dict[str, Any],
        event_type: str,
        old_z_code: str | None = None,
        source: str = "Allocator",
    ) -> None:
        page_id = self.find_page(record["z_code"])
        if not page_id and old_z_code:
            page_id = self.find_page(old_z_code)
        properties = self.properties(record, event_type, source)
        if page_id:
            self.request("PATCH", f"/pages/{page_id}", {"properties": properties})
        else:
            self.request("POST", "/pages", {"parent": {"database_id": self.database_id}, "properties": properties})


def process_event(database: Database, mirror: NotionMirror, item: dict[str, Any]) -> None:
    if item["event_type"] == "topic_reassigned":
        for mapping in item["payload"].get("mappings", []):
            record = database.record_details(mapping["new_z_code"])
            if record:
                mirror.upsert(record, item["event_type"], old_z_code=mapping["old_z_code"])
        return
    record = database.record_details(item["aggregate_key"])
    if not record:
        raise RuntimeError(f"Allocator record not found for {item['aggregate_key']}")
    mirror.upsert(record, item["event_type"])


def main() -> None:
    token = os.getenv("NOTION_API_TOKEN", "").strip()
    database_id = os.getenv("NOTION_ZCODE_DATABASE_ID", "").strip()
    poll_seconds = max(5, int(os.getenv("ZCODE_MIRROR_POLL_SECONDS", "15")))
    if not token or not database_id:
        raise RuntimeError("NOTION_API_TOKEN and NOTION_ZCODE_DATABASE_ID are required")
    database = Database(os.getenv("ZCODE_DATABASE_PATH", "/data/zcode.db"))
    database.initialize()
    mirror = NotionMirror(token, database_id)
    while True:
        for item in database.list_outbox(limit=25):
            try:
                process_event(database, mirror, item)
                database.complete_outbox(item["id"])
                print(json.dumps({"event_id": item["id"], "status": "completed"}), flush=True)
            except Exception as exc:
                database.fail_outbox(item["id"], str(exc))
                print(json.dumps({"event_id": item["id"], "status": "retry", "error": str(exc)[:300]}), flush=True)
        time.sleep(poll_seconds)


if __name__ == "__main__":
    main()
