from __future__ import annotations

from app.mirror_worker import NotionMirror


class FakeNormalizedMirror(NotionMirror):
    def __init__(self) -> None:
        super().__init__("test-token", "record-database", "topic-database")
        self.calls: list[tuple[str, str, dict | None]] = []

    def request(self, method: str, path: str, payload: dict | None = None) -> dict:
        self.calls.append((method, path, payload))
        if method == "POST" and path == "/databases/record-database/query":
            return {"results": []}
        if method == "POST" and path == "/databases/topic-database/query":
            return {"results": []}
        if method == "GET" and path.startswith("/pages/"):
            return {
                "properties": {
                    "Page-Name": {
                        "type": "title",
                        "title": [{"plain_text": "Example Knowledge Record"}],
                    }
                }
            }
        if method == "POST" and path == "/pages":
            properties = (payload or {})["properties"]
            if "Topic-Name" in properties:
                return {"id": "topic-page-id"}
            return {"id": "record-page-id"}
        raise AssertionError((method, path, payload))


def test_normalized_registry_sets_record_title_and_topic_relation() -> None:
    mirror = FakeNormalizedMirror()
    record = {
        "z_code": "Z1ST-80001-100001-050",
        "name_key": "Example-Knowledge",
        "z_knowledge_core": "Z1ST",
        "knowledge_lane": "80001",
        "topic_identifier": "100001",
        "record_suffix": "050",
        "page_type": "SOP",
        "status": "active",
        "topic_status": "active",
        "reserved_by": "edith",
        "request_id": "example-request",
        "notion_url": "https://app.notion.com/p/1234567890abcdef1234567890abcdef",
    }

    mirror.upsert(record, "record_confirmed")

    record_create = [payload for method, path, payload in mirror.calls if method == "POST" and path == "/pages"][-1]
    properties = record_create["properties"]
    assert properties["Z-Code"]["rich_text"][0]["text"]["content"] == record["z_code"]
    assert "Registry-Entry" not in properties
    assert properties["Record-Title"]["rich_text"][0]["text"]["content"] == "Example Knowledge Record"
    assert properties["Topic"]["relation"] == [{"id": "topic-page-id"}]
    assert "Name-Key" not in properties


def test_topic_name_is_human_readable_on_initial_create() -> None:
    mirror = FakeNormalizedMirror()
    record = {
        "name_key": "Rocky-Mountain-Music-Culture",
        "z_knowledge_core": "ZVIM",
        "knowledge_lane": "20001",
        "topic_identifier": "100011",
        "topic_status": "active",
    }

    page_id = mirror.ensure_topic(record, "Allocator")

    assert page_id == "topic-page-id"
    topic_create = [
        payload
        for method, path, payload in mirror.calls
        if method == "POST" and path == "/pages"
    ][0]
    assert topic_create["properties"]["Topic-Name"]["title"][0]["text"]["content"] == (
        "Rocky Mountain Music Culture"
    )


def test_missing_linked_page_keeps_last_known_record_title() -> None:
    mirror = FakeNormalizedMirror()
    mirror.record_title = lambda _: (_ for _ in ()).throw(RuntimeError("Notion API 404: not found"))
    record = {
        "z_code": "Z1ST-80001-100001-050", "name_key": "Example-Knowledge",
        "topic_name": "Example Knowledge", "z_knowledge_core": "Z1ST",
        "knowledge_lane": "80001", "topic_identifier": "100001", "record_suffix": "050",
        "page_type": "SOP", "status": "active", "topic_status": "active",
        "reserved_by": "edith", "request_id": "example-request",
        "notion_url": "https://app.notion.com/p/1234567890abcdef1234567890abcdef",
        "record_title": "Last Known Title",
    }

    assert mirror.upsert(record, "record_admin_resync") == "Last Known Title"


