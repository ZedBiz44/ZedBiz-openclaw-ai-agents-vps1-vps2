from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from app.database import Database, utc_now


NOTION_VERSION = "2022-06-28"


class NotionMirror:
    def __init__(self, token: str, database_id: str, topic_database_id: str | None = None):
        self.token = token
        self.database_id = database_id
        self.topic_database_id = topic_database_id

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
    def topic_key(record: dict[str, Any]) -> str:
        return "-".join(
            [record["z_knowledge_core"], record["knowledge_lane"], record["topic_identifier"]]
        )

    def find_topic_page(self, record: dict[str, Any]) -> str | None:
        if not self.topic_database_id:
            return None
        filters = [
            {"property": "Topic-Key", "rich_text": {"equals": self.topic_key(record)}},
            {"property": "Name-Key", "rich_text": {"equals": record["name_key"]}},
        ]
        for filter_payload in filters:
            result = self.request(
                "POST",
                f"/databases/{self.topic_database_id}/query",
                {"filter": filter_payload, "page_size": 1},
            )
            rows = result.get("results", [])
            if rows:
                return rows[0]["id"]
        return None

    def topic_properties(
        self,
        record: dict[str, Any],
        source: str,
        *,
        include_title: bool = True,
    ) -> dict[str, Any]:
        properties: dict[str, Any] = {
            "Name-Key": self.text(record["name_key"]),
            "Previous-Name-Keys": self.text(record.get("previous_name_keys", "")),
            "Topic-Key": self.text(self.topic_key(record)),
            "Z-Knowledge-Core": self.text(record["z_knowledge_core"]),
            "Knowledge-Lane": self.text(record["knowledge_lane"]),
            "Topic-Identifier": self.text(record["topic_identifier"]),
            "Status": {"select": {"name": str(record.get("topic_status", "active")).capitalize()}},
            "Last-Synced": {"date": {"start": utc_now()}},
            "Source": {"select": {"name": source}},
        }
        if include_title:
            properties["Topic-Name"] = {
                "title": [{"type": "text", "text": {"content": record.get("topic_name") or record["name_key"].replace("-", " ")}}]
            }
        return properties

    def ensure_topic(self, record: dict[str, Any], source: str) -> str | None:
        if not self.topic_database_id:
            return None
        page_id = self.find_topic_page(record)
        if page_id:
            self.request(
                "PATCH",
                f"/pages/{page_id}",
                {"properties": self.topic_properties(record, source)},
            )
            return page_id
        result = self.request(
            "POST",
            "/pages",
            {
                "parent": {"database_id": self.topic_database_id},
                "properties": self.topic_properties(record, source),
            },
        )
        return result["id"]

    @staticmethod
    def notion_page_id(notion_url: str | None) -> str | None:
        if not notion_url:
            return None
        path = urllib.parse.urlparse(notion_url).path.replace("-", "")
        matches = re.findall(r"[0-9a-fA-F]{32}", path)
        return matches[-1] if matches else None

    def record_title(self, notion_url: str | None) -> str:
        page_id = self.notion_page_id(notion_url)
        if not page_id:
            return ""
        page = self.request("GET", f"/pages/{page_id}")
        for value in page.get("properties", {}).values():
            if value.get("type") != "title":
                continue
            return "".join(part.get("plain_text", "") for part in value.get("title", []))
        return ""

    @staticmethod
    def text(value: str | None) -> dict[str, Any]:
        return {"rich_text": [{"type": "text", "text": {"content": value or ""}}]}

    def properties(
        self,
        record: dict[str, Any],
        event_type: str,
        source: str = "Allocator",
        *,
        topic_page_id: str | None = None,
        record_title: str = "",
    ) -> dict[str, Any]:
        properties: dict[str, Any] = {
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
        if self.topic_database_id:
            properties["Registry-Entry"] = {
                "title": [{"type": "text", "text": {"content": record["z_code"]}}]
            }
            properties["Record-Title"] = self.text(record_title)
            if topic_page_id:
                properties["Topic"] = {"relation": [{"id": topic_page_id}]}
        else:
            properties["Name-Key"] = {
                "title": [{"type": "text", "text": {"content": record["name_key"]}}]
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
    ) -> str:
        page_id = self.find_page(record["z_code"])
        if not page_id and old_z_code:
            page_id = self.find_page(old_z_code)
        topic_page_id = self.ensure_topic(record, source)
        record_title = self.record_title(record.get("notion_url")) if self.topic_database_id else ""
        properties = self.properties(
            record,
            event_type,
            source,
            topic_page_id=topic_page_id,
            record_title=record_title,
        )
        if page_id:
            self.request("PATCH", f"/pages/{page_id}", {"properties": properties})
        else:
            self.request("POST", "/pages", {"parent": {"database_id": self.database_id}, "properties": properties})
        return record_title


def process_event(database: Database, mirror: NotionMirror, item: dict[str, Any]) -> None:
    if item["event_type"] == "topic_reassigned":
        for mapping in item["payload"].get("mappings", []):
            record = database.record_details(mapping["new_z_code"])
            if record:
                mirror.upsert(record, item["event_type"], old_z_code=mapping["old_z_code"])
        return
    if item["event_type"] in {"topic_renamed", "topic_name_updated"}:
        for z_code in item["payload"].get("z_codes", []):
            record = database.record_details(z_code)
            if record:
                title = mirror.upsert(record, item["event_type"])
                if title:
                    database.update_record_title_from_mirror(record["z_code"], title)
        return
    record = database.record_details(item["aggregate_key"])
    if not record:
        raise RuntimeError(f"Allocator record not found for {item['aggregate_key']}")
    title = mirror.upsert(record, item["event_type"])
    if title:
        database.update_record_title_from_mirror(record["z_code"], title)


def main() -> None:
    token = os.getenv("NOTION_API_TOKEN", "").strip()
    database_id = os.getenv("NOTION_ZCODE_DATABASE_ID", "").strip()
    topic_database_id = os.getenv("NOTION_ZCODE_TOPIC_DATABASE_ID", "").strip()
    poll_seconds = max(5, int(os.getenv("ZCODE_MIRROR_POLL_SECONDS", "15")))
    auth_backoff_minutes = max(15, int(os.getenv("ZCODE_MIRROR_AUTH_BACKOFF_MINUTES", "60")))
    if not token or not database_id:
        raise RuntimeError("NOTION_API_TOKEN and NOTION_ZCODE_DATABASE_ID are required")
    database = Database(os.getenv("ZCODE_DATABASE_PATH", "/data/zcode.db"))
    database.initialize()
    mirror = NotionMirror(token, database_id, topic_database_id or None)
    while True:
        for item in database.list_outbox(limit=25):
            try:
                process_event(database, mirror, item)
                database.complete_outbox(item["id"])
                print(json.dumps({"event_id": item["id"], "status": "completed"}), flush=True)
            except Exception as exc:
                error = str(exc)
                if "Notion API 401" in error or "Notion API 403" in error:
                    database.fail_outbox(item["id"], error, auth_backoff_minutes)
                    database.defer_outbox("Mirror paused after Notion authentication failure", auth_backoff_minutes)
                    print(json.dumps({"event_id": item["id"], "status": "auth-paused", "error": error[:300]}), flush=True)
                    break
                database.fail_outbox(item["id"], error)
                print(json.dumps({"event_id": item["id"], "status": "retry", "error": str(exc)[:300]}), flush=True)
        time.sleep(poll_seconds)


if __name__ == "__main__":
    main()


