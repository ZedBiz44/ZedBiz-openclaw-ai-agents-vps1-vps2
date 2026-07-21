from __future__ import annotations

from pathlib import Path

from app.backfill_registry import backfill
from app.database import Database
from app.mirror_worker import NotionMirror


class FakeMirror(NotionMirror):
    def __init__(self) -> None:
        super().__init__("test-token", "test-database")
        self.pages: list[dict] = []

    def request(self, method: str, path: str, payload: dict | None = None) -> dict:
        if method == "POST" and path.endswith("/query"):
            return {"results": self.pages, "has_more": False}
        if method == "POST" and path == "/pages":
            properties = (payload or {})["properties"]
            self.pages.append(
                {
                    "id": f"page-{len(self.pages) + 1}",
                    "properties": {
                        name: value | {"type": next(iter(value))}
                        for name, value in properties.items()
                    },
                }
            )
            return {"id": self.pages[-1]["id"]}
        raise AssertionError((method, path, payload))


def test_bootstrap_backfill_is_idempotent_and_labels_source(tmp_path: Path) -> None:
    database = Database(str(tmp_path / "zcode.db"))
    database.initialize()
    imported = database.bootstrap(
        [
            {
                "z_code": "Z1ST-80001-100042-050",
                "name_key": "Existing-Template",
                "page_type": "Template",
                "notion_url": "https://www.notion.so/existing",
            }
        ],
        "edith",
    )
    assert imported["imported"] == 1
    mirror = FakeMirror()

    first = backfill(database, mirror)
    assert first["created"] == 1
    assert first["registry_after"] == 1
    assert first["source_counts"] == {"Bootstrap": 1}
    assert first["missing_authoritative"] == []

    second = backfill(database, mirror)
    assert second["created"] == 0
    assert second["registry_after"] == 1
    assert second["duplicate_z_codes"] == []
