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


def test_topic_name_is_single_source_and_queued_for_mirror(tmp_path: Path) -> None:
    db = Database(str(tmp_path / "zcode.db"))
    db.initialize()
    db.bootstrap([{"z_code": "Z1ST-80001-100001-050", "name_key": "Admin-Test", "page_type": "SOP"}], "edith")

    updated = db.admin_update_topic_name("Admin-Test", "Admin Test Knowledge", "Use clear human title", "jack")

    assert updated["topic_name"] == "Admin Test Knowledge"
    assert db.record_details("Z1ST-80001-100001-050")["topic_name"] == "Admin Test Knowledge"
    assert db.list_outbox(1)[0]["event_type"] == "topic_name_updated"


def test_record_title_is_saved_without_creating_an_outbox_loop(tmp_path: Path) -> None:
    db = Database(str(tmp_path / "zcode.db"))
    db.initialize()
    db.bootstrap([{"z_code": "Z1ST-80001-100001-050", "name_key": "Admin-Test", "page_type": "SOP"}], "edith")
    before = db.metrics()["sync_outbox"]

    db.update_record_title_from_mirror("Z1ST-80001-100001-050", "The Actual Notion Page")

    assert db.record_details("Z1ST-80001-100001-050")["record_title"] == "The Actual Notion Page"
    assert db.metrics()["sync_outbox"] == before


def test_retired_codes_remain_in_permanent_history_after_reassignment(tmp_path: Path) -> None:
    db = Database(str(tmp_path / "zcode.db"))
    db.initialize()
    db.bootstrap([{"z_code": "Z1ST-80001-100001-050", "name_key": "Admin-Test", "page_type": "SOP"}], "edith")

    result = db.reassign_topic({"name_key": "Admin-Test", "new_z_knowledge_core": "Z2ND", "new_knowledge_lane": "80002", "reason": "Correct family"}, "jack")
    history = db.admin_retirement_history("Z1ST-80001-100001-050")

    assert result["mappings"][0]["new_z_code"] == "Z2ND-80002-100001-050"
    assert history[0]["new_z_code"] == "Z2ND-80002-100001-050"


def test_auth_circuit_breaker_defers_all_pending_work(tmp_path: Path) -> None:
    db = Database(str(tmp_path / "zcode.db"))
    db.initialize()
    db.bootstrap([{"z_code": "Z1ST-80001-100001-050", "name_key": "Admin-Test", "page_type": "SOP"}], "edith")
    db.admin_resync_record("Z1ST-80001-100001-050", "Test circuit breaker", "jack")

    changed = db.defer_outbox("Mirror paused after Notion authentication failure", 60)

    assert changed == 1
    item = db.admin_outbox(1)[0]
    assert item["status"] == "retry"
    assert item["last_error"] == "Mirror paused after Notion authentication failure"

