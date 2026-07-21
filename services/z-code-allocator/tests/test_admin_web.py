from pathlib import Path

from app.database import Database


def test_controlled_admin_update_is_audited_and_mirrored(tmp_path: Path) -> None:
    db = Database(str(tmp_path / "zcode.db"))
    db.initialize()
    db.bootstrap([{"z_code": "Z1ST-80001-100001-050", "name_key": "Admin-Test", "page_type": "SOP", "notion_url": "https://notion.so/old"}], "edith")

    updated = db.admin_update_record(
        "Z1ST-80001-100001-050", "Evergreen SOP", "https://notion.so/new", "Correct metadata", "jack"
    )

    assert updated["page_type"] == "Evergreen SOP"
    assert updated["notion_url"] == "https://notion.so/new"
    assert db.admin_audit(1)[0]["event_type"] == "record_admin_updated"
    assert db.list_outbox(1)[0]["event_type"] == "record_admin_updated"


def test_admin_resync_requires_reason(tmp_path: Path) -> None:
    db = Database(str(tmp_path / "zcode.db"))
    db.initialize()
    db.bootstrap([{"z_code": "Z1ST-80001-100001-050", "name_key": "Admin-Test", "page_type": "SOP"}], "edith")
    db.admin_resync_record("Z1ST-80001-100001-050", "Verify mirror", "jack")
    assert db.list_outbox(1)[0]["event_type"] == "record_admin_resync"
