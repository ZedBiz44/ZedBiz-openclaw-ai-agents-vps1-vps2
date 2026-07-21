from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def build_client(tmp_path: Path, ttl: int = 60) -> TestClient:
    app = create_app(
        Settings(
            database_path=str(tmp_path / "zcode.db"),
            api_keys={"marsha": "marsha-key", "edith": "edith-key"},
            admin_agents={"edith"},
            reservation_ttl_minutes=ttl,
            sweeper_interval_seconds=0,
            allocation_enabled=True,
        )
    )
    return TestClient(app)


def auth(agent: str = "marsha") -> dict[str, str]:
    return {"Authorization": f"Bearer {agent}-key"}


def allocation(request_id: str, page_type: str = "Brief", name_key: str = "Biz-Plan-Template") -> dict[str, str]:
    return {
        "request_id": request_id,
        "name_key": name_key,
        "z_knowledge_core": "Z1ST",
        "knowledge_lane": "80001",
        "page_type": page_type,
        "requested_by": "marsha",
    }


def test_allocation_ranges_idempotency_and_confirmation(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        first = client.post("/v1/allocate", json=allocation("request-0001"), headers=auth())
        assert first.status_code == 200
        assert first.json()["z_code"] == "Z1ST-80001-100001-010"
        assert first.json()["new_topic"] is True

        replay = client.post("/v1/allocate", json=allocation("request-0001"), headers=auth())
        assert replay.status_code == 200
        assert replay.json()["z_code"] == first.json()["z_code"]
        assert replay.json()["replayed"] is True

        second = client.post("/v1/allocate", json=allocation("request-0002"), headers=auth())
        plan = client.post("/v1/allocate", json=allocation("request-0003", "Biz-Plan"), headers=auth())
        other = client.post("/v1/allocate", json=allocation("request-0004", "SOP"), headers=auth())
        assert second.json()["record_suffix"] == "011"
        assert plan.json()["record_suffix"] == "020"
        assert other.json()["record_suffix"] == "050"

        confirmed = client.post(
            "/v1/confirm",
            json={"z_code": plan.json()["z_code"], "notion_url": "https://www.notion.so/example"},
            headers=auth(),
        )
        assert confirmed.status_code == 200
        assert confirmed.json()["status"] == "active"


def test_name_key_conflict_enters_review_queue(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        assert client.post("/v1/allocate", json=allocation("request-1001"), headers=auth()).status_code == 200
        conflict = allocation("request-1002") | {"knowledge_lane": "70001"}
        response = client.post("/v1/allocate", json=conflict, headers=auth())
        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "requires_review"
        queue = client.get("/v1/admin/queue", headers=auth("edith"))
        assert len(queue.json()["items"]) == 1


def test_failed_and_stale_codes_are_not_reused(tmp_path: Path) -> None:
    with build_client(tmp_path, ttl=0) as client:
        first = client.post("/v1/allocate", json=allocation("request-2001", "SOP"), headers=auth()).json()
        sweep = client.post("/v1/admin/stale/sweep", headers=auth("edith"))
        assert first["z_code"] in sweep.json()["z_codes"]
        second = client.post("/v1/allocate", json=allocation("request-2002", "SOP"), headers=auth()).json()
        assert first["record_suffix"] == "050"
        assert second["record_suffix"] == "051"
        failed = client.post(
            "/v1/confirm",
            json={"z_code": second["z_code"], "status": "failed", "reason": "Notion creation failed"},
            headers=auth(),
        )
        assert failed.json()["status"] == "abandoned"
        third = client.post("/v1/allocate", json=allocation("request-2003", "SOP"), headers=auth()).json()
        assert third["record_suffix"] == "052"


def test_concurrent_allocations_are_unique(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        def reserve(number: int) -> str:
            response = client.post(
                "/v1/allocate",
                json=allocation(f"concurrent-{number:04d}", "SOP", "Concurrent-Topic"),
                headers=auth(),
            )
            assert response.status_code == 200, response.text
            return response.json()["z_code"]

        with ThreadPoolExecutor(max_workers=8) as pool:
            codes = list(pool.map(reserve, range(12)))
        assert len(codes) == len(set(codes)) == 12


def test_topic_reassignment_changes_all_codes_and_preserves_aliases(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        brief = client.post("/v1/allocate", json=allocation("request-3001"), headers=auth()).json()
        plan = client.post("/v1/allocate", json=allocation("request-3002", "Biz-Plan"), headers=auth()).json()
        reassigned = client.post(
            "/v1/admin/reassign-topic",
            json={
                "name_key": "Biz-Plan-Template",
                "new_z_knowledge_core": "Z1ST",
                "new_knowledge_lane": "70001",
                "reason": "Corrected from Templates to Systems",
            },
            headers=auth("edith"),
        )
        assert reassigned.status_code == 200, reassigned.text
        mappings = reassigned.json()["mappings"]
        assert {item["old_z_code"] for item in mappings} == {brief["z_code"], plan["z_code"]}
        assert all("-70001-" in item["new_z_code"] for item in mappings)


def test_authentication_and_agent_identity_are_enforced(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        assert client.post("/v1/allocate", json=allocation("request-4001")).status_code == 401
        mismatched = allocation("request-4002") | {"requested_by": "edith"}
        assert client.post("/v1/allocate", json=mismatched, headers=auth()).status_code == 409


def test_bootstrap_lock_and_existing_code_import(tmp_path: Path) -> None:
    database_path = str(tmp_path / "zcode.db")
    locked_app = create_app(
        Settings(
            database_path=database_path,
            api_keys={"marsha": "marsha-key", "edith": "edith-key"},
            admin_agents={"edith"},
            sweeper_interval_seconds=0,
            allocation_enabled=False,
        )
    )
    with TestClient(locked_app) as locked:
        blocked = locked.post("/v1/allocate", json=allocation("request-5001"), headers=auth())
        assert blocked.status_code == 503
        imported = locked.post(
            "/v1/admin/bootstrap",
            json={
                "records": [
                    {
                        "z_code": "Z1ST-80001-100042-050",
                        "name_key": "Existing-Template",
                        "page_type": "Template",
                        "notion_url": "https://www.notion.so/existing",
                    }
                ]
            },
            headers=auth("edith"),
        )
        assert imported.status_code == 200, imported.text
        assert imported.json()["imported"] == 1

    enabled_app = create_app(
        Settings(
            database_path=database_path,
            api_keys={"marsha": "marsha-key", "edith": "edith-key"},
            admin_agents={"edith"},
            sweeper_interval_seconds=0,
            allocation_enabled=True,
        )
    )
    with TestClient(enabled_app) as enabled:
        new_topic = enabled.post(
            "/v1/allocate",
            json=allocation("request-5002", "Template", "New-Template"),
            headers=auth(),
        )
        assert new_topic.status_code == 200, new_topic.text
        assert new_topic.json()["topic_identifier"] == "100043"
