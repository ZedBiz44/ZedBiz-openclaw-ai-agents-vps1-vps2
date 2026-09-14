from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_page_type(value: str) -> str:
    return "-".join(value.strip().lower().replace("_", "-").split())


class AllocationConflict(Exception):
    def __init__(self, message: str, queue_id: str | None = None):
        super().__init__(message)
        self.message = message
        self.queue_id = queue_id


class NotFound(Exception):
    pass


class InvalidState(Exception):
    pass


SCHEMA = """
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_identifier INTEGER NOT NULL CHECK(topic_identifier BETWEEN 100000 AND 999999),
    name_key TEXT NOT NULL,
    topic_name TEXT NOT NULL DEFAULT '',
    z_knowledge_core TEXT NOT NULL,
    knowledge_lane TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'retired')),
    version INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(z_knowledge_core, knowledge_lane, topic_identifier)
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_topics_name_key ON topics(lower(name_key));

CREATE TABLE IF NOT EXISTS name_key_aliases (
    old_name_key TEXT PRIMARY KEY COLLATE NOCASE,
    topic_pk INTEGER NOT NULL REFERENCES topics(id),
    reason TEXT NOT NULL,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS page_type_ranges (
    range_key TEXT PRIMARY KEY,
    minimum_suffix INTEGER NOT NULL,
    maximum_suffix INTEGER NOT NULL,
    CHECK(minimum_suffix BETWEEN 0 AND 999),
    CHECK(maximum_suffix BETWEEN minimum_suffix AND 999)
);

CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    z_code TEXT NOT NULL UNIQUE,
    topic_pk INTEGER NOT NULL REFERENCES topics(id),
    page_type TEXT NOT NULL,
    record_suffix INTEGER NOT NULL CHECK(record_suffix BETWEEN 0 AND 999),
    request_id TEXT NOT NULL UNIQUE,
    reserved_by TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'reserved'
        CHECK(status IN ('reserved', 'active', 'stale', 'abandoned', 'reassigned')),
    notion_url TEXT,
    record_title TEXT NOT NULL DEFAULT '',
    failure_reason TEXT,
    previous_z_code TEXT,
    reserved_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    confirmed_at TEXT,
    updated_at TEXT NOT NULL,
    UNIQUE(topic_pk, record_suffix)
);
CREATE INDEX IF NOT EXISTS idx_records_topic_suffix ON records(topic_pk, record_suffix);
CREATE INDEX IF NOT EXISTS idx_records_status_expiry ON records(status, expires_at);

CREATE TABLE IF NOT EXISTS review_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    queue_id TEXT NOT NULL UNIQUE,
    request_id TEXT NOT NULL UNIQUE,
    requested_by TEXT NOT NULL,
    reason TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending', 'dismissed', 'retry_allowed')),
    resolution_notes TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT,
    resolved_by TEXT
);

CREATE TABLE IF NOT EXISTS sync_outbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    aggregate_key TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending', 'processing', 'retry', 'completed')),
    attempts INTEGER NOT NULL DEFAULT 0,
    available_at TEXT NOT NULL,
    last_error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_outbox_ready ON sync_outbox(status, available_at);

CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    actor TEXT NOT NULL,
    z_code TEXT,
    request_id TEXT,
    details_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_z_code ON audit_events(z_code, created_at);

CREATE TABLE IF NOT EXISTS z_code_aliases (
    old_z_code TEXT PRIMARY KEY,
    new_z_code TEXT NOT NULL,
    reason TEXT NOT NULL,
    changed_by TEXT NOT NULL,
    changed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS issued_topic_identifiers (
    z_knowledge_core TEXT NOT NULL,
    knowledge_lane TEXT NOT NULL,
    topic_identifier INTEGER NOT NULL CHECK(topic_identifier BETWEEN 100000 AND 999999),
    first_issued_at TEXT NOT NULL,
    source TEXT NOT NULL,
    PRIMARY KEY(z_knowledge_core, knowledge_lane, topic_identifier)
);

CREATE TABLE IF NOT EXISTS issued_z_codes (
    z_code TEXT PRIMARY KEY,
    first_issued_at TEXT NOT NULL,
    source TEXT NOT NULL
);
"""


class Database:
    def __init__(self, path: str, reservation_ttl_minutes: int = 60):
        self.path = path
        self.reservation_ttl_minutes = reservation_ttl_minutes
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.executescript(SCHEMA)
            self._ensure_column(connection, "topics", "topic_name", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(connection, "records", "record_title", "TEXT NOT NULL DEFAULT ''")
            connection.execute(
                "UPDATE topics SET topic_name = replace(name_key, '-', ' ') WHERE trim(topic_name) = ''"
            )
            connection.executemany(
                "INSERT OR IGNORE INTO page_type_ranges(range_key, minimum_suffix, maximum_suffix) VALUES (?, ?, ?)",
                [("brief", 10, 19), ("biz-plan", 20, 49), ("other", 50, 999)],
            )
            self._backfill_issued_history(connection)

    @staticmethod
    def _ensure_column(connection: sqlite3.Connection, table: str, column: str, definition: str) -> None:
        columns = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}
        if column not in columns:
            connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    @staticmethod
    def parse_z_code(z_code: str) -> tuple[str, str, int, int]:
        core, lane, topic_text, suffix_text = z_code.split("-")
        return core, lane, int(topic_text), int(suffix_text)

    def _backfill_issued_history(self, connection: sqlite3.Connection) -> None:
        now = utc_now()
        connection.execute(
            """
            INSERT OR IGNORE INTO issued_topic_identifiers(
                z_knowledge_core, knowledge_lane, topic_identifier, first_issued_at, source
            )
            SELECT z_knowledge_core, knowledge_lane, topic_identifier, created_at, 'topic'
            FROM topics
            """
        )
        historical_codes: set[str] = set()
        for row in connection.execute("SELECT z_code, previous_z_code FROM records"):
            historical_codes.add(row["z_code"])
            if row["previous_z_code"]:
                historical_codes.add(row["previous_z_code"])
        for row in connection.execute("SELECT old_z_code, new_z_code FROM z_code_aliases"):
            historical_codes.add(row["old_z_code"])
            historical_codes.add(row["new_z_code"])
        for z_code in historical_codes:
            try:
                core, lane, topic_identifier, _ = self.parse_z_code(z_code)
            except (TypeError, ValueError):
                continue
            connection.execute(
                "INSERT OR IGNORE INTO issued_topic_identifiers VALUES (?, ?, ?, ?, 'history-backfill')",
                (core, lane, topic_identifier, now),
            )
            connection.execute(
                "INSERT OR IGNORE INTO issued_z_codes VALUES (?, ?, 'history-backfill')",
                (z_code, now),
            )

    @staticmethod
    def next_topic_identifier(connection: sqlite3.Connection, core: str, lane: str) -> int:
        highest = connection.execute(
            "SELECT MAX(topic_identifier) AS highest FROM issued_topic_identifiers WHERE z_knowledge_core = ? AND knowledge_lane = ?",
            (core, lane),
        ).fetchone()["highest"]
        topic_identifier = 100001 if highest is None else int(highest) + 1
        if topic_identifier > 999999:
            raise InvalidState("Topic Identifier range is exhausted for this Knowledge Lane")
        return topic_identifier

    @staticmethod
    def reserve_topic_identifier(
        connection: sqlite3.Connection,
        core: str,
        lane: str,
        topic_identifier: int,
        source: str,
    ) -> None:
        try:
            connection.execute(
                "INSERT INTO issued_topic_identifiers VALUES (?, ?, ?, ?, ?)",
                (core, lane, topic_identifier, utc_now(), source),
            )
        except sqlite3.IntegrityError as exc:
            raise AllocationConflict(
                f"Topic Identifier {topic_identifier:06d} is permanently reserved in {core}-{lane}"
            ) from exc

    @staticmethod
    def reserve_z_code(connection: sqlite3.Connection, z_code: str, source: str) -> None:
        try:
            connection.execute(
                "INSERT INTO issued_z_codes VALUES (?, ?, ?)",
                (z_code, utc_now(), source),
            )
        except sqlite3.IntegrityError as exc:
            raise AllocationConflict(f"Z-Code {z_code} was previously issued and cannot be reused") from exc

    @contextmanager
    def write_transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def row_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
        return dict(row) if row else None

    @staticmethod
    def format_z_code(core: str, lane: str, topic_identifier: int, suffix: int) -> str:
        return f"{core}-{lane}-{topic_identifier:06d}-{suffix:03d}"

    @staticmethod
    def find_topic(connection: sqlite3.Connection, name_key: str) -> sqlite3.Row | None:
        topic = connection.execute(
            "SELECT * FROM topics WHERE lower(name_key) = lower(?)", (name_key,)
        ).fetchone()
        if topic:
            return topic
        return connection.execute(
            """
            SELECT t.* FROM name_key_aliases a
            JOIN topics t ON t.id = a.topic_pk
            WHERE lower(a.old_name_key) = lower(?)
            """,
            (name_key,),
        ).fetchone()

    @staticmethod
    def add_audit(
        connection: sqlite3.Connection,
        event_type: str,
        actor: str,
        details: dict[str, Any],
        *,
        z_code: str | None = None,
        request_id: str | None = None,
    ) -> None:
        connection.execute(
            "INSERT INTO audit_events(event_type, actor, z_code, request_id, details_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (event_type, actor, z_code, request_id, json.dumps(details, sort_keys=True), utc_now()),
        )

    @staticmethod
    def add_outbox(
        connection: sqlite3.Connection,
        event_type: str,
        aggregate_key: str,
        payload: dict[str, Any],
    ) -> None:
        now = utc_now()
        connection.execute(
            "INSERT INTO sync_outbox(event_type, aggregate_key, payload_json, available_at, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (event_type, aggregate_key, json.dumps(payload, sort_keys=True), now, now, now),
        )

    def _record_response(self, connection: sqlite3.Connection, row: sqlite3.Row, replayed: bool) -> dict[str, Any]:
        topic = connection.execute("SELECT * FROM topics WHERE id = ?", (row["topic_pk"],)).fetchone()
        return {
            "z_code": row["z_code"],
            "status": row["status"],
            "request_id": row["request_id"],
            "name_key": topic["name_key"],
            "topic_name": topic["topic_name"],
            "z_knowledge_core": topic["z_knowledge_core"],
            "knowledge_lane": topic["knowledge_lane"],
            "topic_identifier": f"{topic['topic_identifier']:06d}",
            "record_suffix": f"{row['record_suffix']:03d}",
            "page_type": row["page_type"],
            "new_topic": False,
            "replayed": replayed,
            "expires_at": row["expires_at"],
            "notion_url": row["notion_url"],
            "record_title": row["record_title"],
        }

    def allocate(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        requested_by = payload["requested_by"].strip().lower()
        if requested_by != actor:
            raise InvalidState("requested_by must match the authenticated agent")
        core = payload["z_knowledge_core"].upper()
        lane = payload["knowledge_lane"]
        page_type = payload["page_type"].strip()
        name_key = payload["name_key"].strip()
        request_id = payload["request_id"]

        with self.write_transaction() as connection:
            existing = connection.execute(
                "SELECT * FROM records WHERE request_id = ?", (request_id,)
            ).fetchone()
            if existing:
                response = self._record_response(connection, existing, replayed=True)
                requested_topic = self.find_topic(connection, name_key)
                requested_name_key = requested_topic["name_key"] if requested_topic else name_key
                requested_shape = (requested_name_key.lower(), core, lane, normalize_page_type(page_type))
                existing_shape = (
                    response["name_key"].lower(),
                    response["z_knowledge_core"],
                    response["knowledge_lane"],
                    normalize_page_type(response["page_type"]),
                )
                if requested_shape != existing_shape:
                    raise AllocationConflict("request_id was already used with a different allocation payload")
                return response

            review = connection.execute(
                "SELECT * FROM review_requests WHERE request_id = ?", (request_id,)
            ).fetchone()
            if review:
                raise AllocationConflict(review["reason"], review["queue_id"])

            matching_topic = self.find_topic(connection, name_key)
            new_topic = False
            if matching_topic and (
                matching_topic["z_knowledge_core"] != core or matching_topic["knowledge_lane"] != lane
            ):
                queue_id = f"review-{request_id}"
                reason = "Name-Key exists under a different Z-Knowledge-Core or Knowledge Lane"
                connection.execute(
                    "INSERT INTO review_requests(queue_id, request_id, requested_by, reason, payload_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (queue_id, request_id, actor, reason, json.dumps(payload, sort_keys=True), utc_now()),
                )
                self.add_audit(connection, "review_required", actor, payload, request_id=request_id)
                # The durable review request must survive the 409 response.
                connection.commit()
                raise AllocationConflict(reason, queue_id)

            if matching_topic:
                topic = matching_topic
            else:
                topic_identifier = self.next_topic_identifier(connection, core, lane)
                now = utc_now()
                self.reserve_topic_identifier(connection, core, lane, topic_identifier, "allocation")
                cursor = connection.execute(
                    "INSERT INTO topics(topic_identifier, name_key, topic_name, z_knowledge_core, knowledge_lane, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (topic_identifier, name_key, name_key.replace("-", " "), core, lane, now, now),
                )
                topic = connection.execute("SELECT * FROM topics WHERE id = ?", (cursor.lastrowid,)).fetchone()
                new_topic = True

            range_key = normalize_page_type(page_type)
            range_row = connection.execute(
                "SELECT * FROM page_type_ranges WHERE range_key = ?", (range_key,)
            ).fetchone()
            if not range_row:
                range_row = connection.execute(
                    "SELECT * FROM page_type_ranges WHERE range_key = 'other'"
                ).fetchone()
            minimum, maximum = range_row["minimum_suffix"], range_row["maximum_suffix"]
            highest_suffix = connection.execute(
                "SELECT MAX(record_suffix) AS highest FROM records WHERE topic_pk = ? AND record_suffix BETWEEN ? AND ?",
                (topic["id"], minimum, maximum),
            ).fetchone()["highest"]
            suffix = minimum if highest_suffix is None else int(highest_suffix) + 1
            if suffix > maximum:
                raise InvalidState(f"No {page_type} suffixes remain for this topic")

            now_dt = datetime.now(timezone.utc)
            now = now_dt.isoformat().replace("+00:00", "Z")
            expires_at = (now_dt + timedelta(minutes=self.reservation_ttl_minutes)).isoformat().replace("+00:00", "Z")
            z_code = self.format_z_code(core, lane, topic["topic_identifier"], suffix)
            self.reserve_z_code(connection, z_code, "allocation")
            cursor = connection.execute(
                """INSERT INTO records(
                    z_code, topic_pk, page_type, record_suffix, request_id, reserved_by,
                    reserved_at, expires_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (z_code, topic["id"], page_type, suffix, request_id, actor, now, expires_at, now),
            )
            record = connection.execute("SELECT * FROM records WHERE id = ?", (cursor.lastrowid,)).fetchone()
            event = {
                "z_code": z_code,
                "request_id": request_id,
                "name_key": topic["name_key"],
                "z_knowledge_core": core,
                "knowledge_lane": lane,
                "topic_identifier": f"{topic['topic_identifier']:06d}",
                "record_suffix": f"{suffix:03d}",
                "page_type": page_type,
                "status": "reserved",
                "reserved_by": actor,
                "expires_at": expires_at,
            }
            self.add_outbox(connection, "record_reserved", z_code, event)
            self.add_audit(connection, "record_reserved", actor, event, z_code=z_code, request_id=request_id)
            response = self._record_response(connection, record, replayed=False)
            response["new_topic"] = new_topic
            return response

    def confirm(self, payload: dict[str, Any], actor: str, is_admin: bool) -> dict[str, Any]:
        with self.write_transaction() as connection:
            record = connection.execute("SELECT * FROM records WHERE z_code = ?", (payload["z_code"],)).fetchone()
            if not record:
                raise NotFound("Z-Code reservation was not found")
            if record["reserved_by"] != actor and not is_admin:
                raise InvalidState("Only the reserving agent or an administrator can confirm this Z-Code")
            if record["status"] in {"abandoned", "reassigned"}:
                if record["status"] == "abandoned" and payload["status"] == "failed":
                    return {
                        "z_code": record["z_code"],
                        "request_id": record["request_id"],
                        "status": "abandoned",
                        "notion_url": record["notion_url"],
                        "reason": record["failure_reason"],
                        "updated_by": actor,
                        "replayed": True,
                    }
                raise InvalidState(f"Cannot confirm a {record['status']} Z-Code")
            if record["status"] == "active":
                if payload["status"] == "active" and record["notion_url"] == payload["notion_url"]:
                    return {
                        "z_code": record["z_code"],
                        "request_id": record["request_id"],
                        "status": "active",
                        "notion_url": record["notion_url"],
                        "record_title": record["record_title"],
                        "reason": None,
                        "updated_by": actor,
                        "replayed": True,
                    }
                raise InvalidState("Active Z-Code confirmation does not match the existing Notion record")

            now = utc_now()
            if payload["status"] == "failed":
                connection.execute(
                    "UPDATE records SET status = 'abandoned', failure_reason = ?, updated_at = ? WHERE id = ?",
                    (payload["reason"], now, record["id"]),
                )
                event_type = "record_abandoned"
                status = "abandoned"
            else:
                connection.execute(
                    "UPDATE records SET status = 'active', notion_url = ?, record_title = ?, confirmed_at = ?, updated_at = ? WHERE id = ?",
                    (payload["notion_url"], payload.get("record_title") or "", now, now, record["id"]),
                )
                event_type = "record_confirmed"
                status = "active"
            event = {
                "z_code": record["z_code"],
                "request_id": record["request_id"],
                "status": status,
                "notion_url": payload.get("notion_url"),
                "record_title": payload.get("record_title") or "",
                "reason": payload.get("reason"),
                "updated_by": actor,
                "replayed": False,
            }
            self.add_outbox(connection, event_type, record["z_code"], event)
            self.add_audit(
                connection, event_type, actor, event, z_code=record["z_code"], request_id=record["request_id"]
            )
            return event

    def status(self, request_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            record = connection.execute("SELECT * FROM records WHERE request_id = ?", (request_id,)).fetchone()
            if record:
                return self._record_response(connection, record, replayed=True)
            review = connection.execute("SELECT * FROM review_requests WHERE request_id = ?", (request_id,)).fetchone()
            if review:
                return {
                    "request_id": request_id,
                    "status": "requires_review" if review["status"] == "pending" else review["status"],
                    "queue_id": review["queue_id"],
                    "reason": review["reason"],
                    "resolution_notes": review["resolution_notes"],
                }
        raise NotFound("Request was not found")

    def lookup(self, name_key: str) -> dict[str, Any]:
        with self.connect() as connection:
            topic = self.find_topic(connection, name_key)
            if not topic:
                raise NotFound("Name-Key was not found")
            records = connection.execute(
                "SELECT z_code, page_type, record_suffix, status, notion_url, reserved_by, updated_at FROM records WHERE topic_pk = ? ORDER BY record_suffix",
                (topic["id"],),
            ).fetchall()
            return {
                "name_key": topic["name_key"],
                "topic_name": topic["topic_name"],
                "z_knowledge_core": topic["z_knowledge_core"],
                "knowledge_lane": topic["knowledge_lane"],
                "topic_identifier": f"{topic['topic_identifier']:06d}",
                "status": topic["status"],
                "records": [dict(row) | {"record_suffix": f"{row['record_suffix']:03d}"} for row in records],
            }

    def sweep_stale(self, actor: str = "system") -> list[str]:
        now = utc_now()
        changed: list[str] = []
        with self.write_transaction() as connection:
            rows = connection.execute(
                "SELECT * FROM records WHERE status = 'reserved' AND expires_at <= ?", (now,)
            ).fetchall()
            for row in rows:
                connection.execute(
                    "UPDATE records SET status = 'stale', updated_at = ? WHERE id = ?", (now, row["id"])
                )
                event = {"z_code": row["z_code"], "request_id": row["request_id"], "status": "stale"}
                self.add_outbox(connection, "record_stale", row["z_code"], event)
                self.add_audit(
                    connection, "record_stale", actor, event, z_code=row["z_code"], request_id=row["request_id"]
                )
                changed.append(row["z_code"])
        return changed

    def list_reviews(self, status: str = "pending") -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM review_requests WHERE status = ? ORDER BY created_at", (status,)
            ).fetchall()
            return [dict(row) | {"payload": json.loads(row["payload_json"])} for row in rows]

    def resolve_review(self, queue_id: str, resolution: str, notes: str, actor: str) -> dict[str, Any]:
        with self.write_transaction() as connection:
            row = connection.execute("SELECT * FROM review_requests WHERE queue_id = ?", (queue_id,)).fetchone()
            if not row:
                raise NotFound("Review request was not found")
            if row["status"] != "pending":
                raise InvalidState("Review request has already been resolved")
            now = utc_now()
            connection.execute(
                "UPDATE review_requests SET status = ?, resolution_notes = ?, resolved_at = ?, resolved_by = ? WHERE id = ?",
                (resolution, notes, now, actor, row["id"]),
            )
            event = {"queue_id": queue_id, "request_id": row["request_id"], "status": resolution, "notes": notes}
            self.add_audit(connection, "review_resolved", actor, event, request_id=row["request_id"])
            return event

    def reassign_topic(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        name_key = payload["name_key"]
        new_core = payload["new_z_knowledge_core"].upper()
        new_lane = payload["new_knowledge_lane"]
        with self.write_transaction() as connection:
            topic = self.find_topic(connection, name_key)
            if not topic:
                raise NotFound("Name-Key was not found")
            if topic["z_knowledge_core"] == new_core and topic["knowledge_lane"] == new_lane:
                raise InvalidState("Topic is already assigned to that Z-Knowledge-Core and Knowledge Lane")
            new_identifier = self.next_topic_identifier(connection, new_core, new_lane)
            records = connection.execute("SELECT * FROM records WHERE topic_pk = ? ORDER BY record_suffix", (topic["id"],)).fetchall()
            mappings: list[dict[str, str]] = []
            for record in records:
                new_code = self.format_z_code(new_core, new_lane, new_identifier, record["record_suffix"])
                collision = connection.execute(
                    """
                    SELECT 1 FROM records WHERE z_code = ?
                    UNION ALL
                    SELECT 1 FROM z_code_aliases WHERE old_z_code = ? OR new_z_code = ?
                    UNION ALL
                    SELECT 1 FROM issued_z_codes WHERE z_code = ?
                    LIMIT 1
                    """,
                    (new_code, new_code, new_code, new_code),
                ).fetchone()
                if collision:
                    raise AllocationConflict(f"Reassignment would reuse existing or retired Z-Code {new_code}")
                mappings.append({"old_z_code": record["z_code"], "new_z_code": new_code})
            now = utc_now()
            self.reserve_topic_identifier(connection, new_core, new_lane, new_identifier, "topic-reassignment")
            for mapping in mappings:
                self.reserve_z_code(connection, mapping["new_z_code"], "topic-reassignment")
            connection.execute(
                "UPDATE topics SET topic_identifier = ?, z_knowledge_core = ?, knowledge_lane = ?, version = version + 1, updated_at = ? WHERE id = ?",
                (new_identifier, new_core, new_lane, now, topic["id"]),
            )
            for mapping, record in zip(mappings, records, strict=True):
                connection.execute(
                    "INSERT INTO z_code_aliases(old_z_code, new_z_code, reason, changed_by, changed_at) VALUES (?, ?, ?, ?, ?)",
                    (mapping["old_z_code"], mapping["new_z_code"], payload["reason"], actor, now),
                )
                connection.execute(
                    "UPDATE records SET previous_z_code = z_code, z_code = ?, updated_at = ? WHERE id = ?",
                    (mapping["new_z_code"], now, record["id"]),
                )
            event = {
                "name_key": topic["name_key"],
                "old_z_knowledge_core": topic["z_knowledge_core"],
                "old_knowledge_lane": topic["knowledge_lane"],
                "new_z_knowledge_core": new_core,
                "new_knowledge_lane": new_lane,
                "new_topic_identifier": f"{new_identifier:06d}",
                "mappings": mappings,
                "reason": payload["reason"],
            }
            self.add_outbox(connection, "topic_reassigned", topic["name_key"], event)
            self.add_audit(connection, "topic_reassigned", actor, event)
            return event

    def rename_topic(self, payload: dict[str, Any], actor: str) -> dict[str, Any]:
        requested_name_key = payload["name_key"].strip()
        new_name_key = payload["new_name_key"].strip()
        with self.write_transaction() as connection:
            topic = self.find_topic(connection, requested_name_key)
            if not topic:
                raise NotFound("Name-Key was not found")
            old_name_key = topic["name_key"]
            if old_name_key.lower() == new_name_key.lower():
                raise InvalidState("Topic already uses that Name-Key")
            collision = self.find_topic(connection, new_name_key)
            if collision and collision["id"] != topic["id"]:
                raise AllocationConflict("The new Name-Key already identifies a different topic")
            now = utc_now()
            connection.execute(
                "INSERT OR IGNORE INTO name_key_aliases(old_name_key, topic_pk, reason, changed_by, changed_at) VALUES (?, ?, ?, ?, ?)",
                (old_name_key, topic["id"], payload["reason"], actor, now),
            )
            connection.execute(
                "UPDATE topics SET name_key = ?, version = version + 1, updated_at = ? WHERE id = ?",
                (new_name_key, now, topic["id"]),
            )
            records = connection.execute(
                "SELECT z_code FROM records WHERE topic_pk = ? ORDER BY record_suffix", (topic["id"],)
            ).fetchall()
            event = {
                "old_name_key": old_name_key,
                "new_name_key": new_name_key,
                "z_knowledge_core": topic["z_knowledge_core"],
                "knowledge_lane": topic["knowledge_lane"],
                "topic_identifier": f"{topic['topic_identifier']:06d}",
                "z_codes": [row["z_code"] for row in records],
                "reason": payload["reason"],
            }
            self.add_outbox(connection, "topic_renamed", new_name_key, event)
            self.add_audit(connection, "topic_renamed", actor, event)
            return event

    def list_outbox(self, limit: int = 100) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM sync_outbox WHERE status IN ('pending', 'retry') AND available_at <= ? ORDER BY id LIMIT ?",
                (utc_now(), limit),
            ).fetchall()
            return [dict(row) | {"payload": json.loads(row["payload_json"])} for row in rows]

    def record_details(self, z_code: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT r.*, t.name_key, t.topic_name, t.z_knowledge_core, t.knowledge_lane,
                       t.topic_identifier, t.status AS topic_status
                FROM records r
                JOIN topics t ON t.id = r.topic_pk
                WHERE r.z_code = ?
                """,
                (z_code,),
            ).fetchone()
            if not row:
                return None
            result = dict(row)
            aliases = connection.execute(
                "SELECT old_name_key FROM name_key_aliases WHERE topic_pk = ? ORDER BY changed_at",
                (row["topic_pk"],),
            ).fetchall()
            result["previous_name_keys"] = ", ".join(alias["old_name_key"] for alias in aliases)
            result["topic_identifier"] = f"{row['topic_identifier']:06d}"
            result["record_suffix"] = f"{row['record_suffix']:03d}"
            return result

    def admin_records(self, search: str = "", limit: int = 200) -> list[dict[str, Any]]:
        with self.connect() as connection:
            pattern = f"%{search.strip()}%"
            rows = connection.execute(
                """
                SELECT r.z_code, r.page_type, r.status, r.notion_url, r.record_title,
                       r.record_suffix, r.reserved_by, r.request_id, r.updated_at,
                       t.name_key, t.topic_name, t.z_knowledge_core,
                       t.knowledge_lane, t.topic_identifier
                FROM records r JOIN topics t ON t.id = r.topic_pk
                WHERE ? = '' OR r.z_code LIKE ? OR t.name_key LIKE ? OR t.topic_name LIKE ?
                    OR r.record_title LIKE ? OR r.notion_url LIKE ?
                ORDER BY r.updated_at DESC LIMIT ?
                """,
                (search.strip(), pattern, pattern, pattern, pattern, pattern, limit),
            ).fetchall()
            return [dict(row) | {"topic_identifier": f"{row['topic_identifier']:06d}"} for row in rows]

    def admin_audit(self, limit: int = 100) -> list[dict[str, Any]]:
        with self.connect() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,)
                ).fetchall()
            ]

    def admin_topics(self, search: str = "", limit: int = 200) -> list[dict[str, Any]]:
        with self.connect() as connection:
            pattern = f"%{search.strip()}%"
            rows = connection.execute(
                """
                SELECT t.*, COUNT(r.id) AS record_count
                FROM topics t LEFT JOIN records r ON r.topic_pk = t.id
                WHERE ? = '' OR t.name_key LIKE ? OR t.topic_name LIKE ?
                    OR t.z_knowledge_core LIKE ? OR t.knowledge_lane LIKE ?
                GROUP BY t.id ORDER BY t.updated_at DESC LIMIT ?
                """,
                (search.strip(), pattern, pattern, pattern, pattern, limit),
            ).fetchall()
            return [dict(row) | {"topic_identifier": f"{row['topic_identifier']:06d}"} for row in rows]

    def admin_update_topic_name(self, name_key: str, topic_name: str, reason: str, actor: str) -> dict[str, Any]:
        topic_name, reason = topic_name.strip(), reason.strip()
        if not topic_name or not reason:
            raise InvalidState("Topic Name and change reason are required")
        with self.write_transaction() as connection:
            topic = self.find_topic(connection, name_key)
            if not topic:
                raise NotFound("Name-Key was not found")
            before = topic["topic_name"]
            now = utc_now()
            connection.execute(
                "UPDATE topics SET topic_name = ?, version = version + 1, updated_at = ? WHERE id = ?",
                (topic_name, now, topic["id"]),
            )
            codes = [row["z_code"] for row in connection.execute(
                "SELECT z_code FROM records WHERE topic_pk = ? ORDER BY record_suffix", (topic["id"],)
            )]
            event = {"name_key": topic["name_key"], "before": before, "after": topic_name,
                     "z_codes": codes, "reason": reason}
            self.add_outbox(connection, "topic_name_updated", topic["name_key"], event)
            self.add_audit(connection, "topic_name_updated", actor, event)
        return self.admin_topics(name_key, 1)[0]

    def update_record_title_from_mirror(self, z_code: str, record_title: str) -> None:
        with self.write_transaction() as connection:
            connection.execute(
                "UPDATE records SET record_title = ?, updated_at = ? WHERE z_code = ? AND record_title != ?",
                (record_title.strip(), utc_now(), z_code, record_title.strip()),
            )

    def admin_retirement_history(self, search: str = "", limit: int = 300) -> list[dict[str, Any]]:
        with self.connect() as connection:
            pattern = f"%{search.strip()}%"
            rows = connection.execute(
                """
                SELECT i.z_code, i.first_issued_at, i.source, a.new_z_code,
                       a.reason, a.changed_by, a.changed_at
                FROM issued_z_codes i LEFT JOIN z_code_aliases a ON a.old_z_code = i.z_code
                WHERE ? = '' OR i.z_code LIKE ? OR a.new_z_code LIKE ?
                ORDER BY i.first_issued_at DESC LIMIT ?
                """, (search.strip(), pattern, pattern, limit)
            ).fetchall()
            return [dict(row) for row in rows]

    def admin_outbox(self, limit: int = 200) -> list[dict[str, Any]]:
        with self.connect() as connection:
            return [dict(row) for row in connection.execute(
                "SELECT id, event_type, aggregate_key, status, attempts, available_at, last_error, updated_at "
                "FROM sync_outbox WHERE status IN ('pending','retry') ORDER BY updated_at DESC LIMIT ?", (limit,)
            )]

    def admin_update_record(
        self, z_code: str, page_type: str, notion_url: str | None, reason: str, actor: str
    ) -> dict[str, Any]:
        page_type = page_type.strip()
        notion_url = (notion_url or "").strip() or None
        reason = reason.strip()
        if not page_type or not reason:
            raise InvalidState("Page Type and change reason are required")
        with self.write_transaction() as connection:
            record = connection.execute("SELECT * FROM records WHERE z_code = ?", (z_code,)).fetchone()
            if not record:
                raise NotFound("Z-Code record was not found")
            before = {"page_type": record["page_type"], "notion_url": record["notion_url"]}
            now = utc_now()
            connection.execute(
                "UPDATE records SET page_type = ?, notion_url = ?, updated_at = ? WHERE id = ?",
                (page_type, notion_url, now, record["id"]),
            )
            after = {"page_type": page_type, "notion_url": notion_url}
            event = {"before": before, "after": after, "reason": reason}
            self.add_outbox(connection, "record_admin_updated", z_code, event)
            self.add_audit(connection, "record_admin_updated", actor, event, z_code=z_code, request_id=record["request_id"])
        return self.record_details(z_code) or {}

    def admin_resync_record(self, z_code: str, reason: str, actor: str) -> dict[str, Any]:
        reason = reason.strip()
        if not reason:
            raise InvalidState("Resync reason is required")
        with self.write_transaction() as connection:
            record = connection.execute("SELECT * FROM records WHERE z_code = ?", (z_code,)).fetchone()
            if not record:
                raise NotFound("Z-Code record was not found")
            event = {"reason": reason, "requested_by": actor}
            self.add_outbox(connection, "record_admin_resync", z_code, event)
            self.add_audit(connection, "record_admin_resync", actor, event, z_code=z_code, request_id=record["request_id"])
            return event

    def complete_outbox(self, event_id: int) -> None:
        with self.write_transaction() as connection:
            changed = connection.execute(
                "UPDATE sync_outbox SET status = 'completed', attempts = attempts + 1, updated_at = ? WHERE id = ?",
                (utc_now(), event_id),
            ).rowcount
            if not changed:
                raise NotFound("Outbox event was not found")

    def fail_outbox(self, event_id: int, error: str, delay_minutes: int | None = None) -> None:
        with self.write_transaction() as connection:
            row = connection.execute("SELECT attempts FROM sync_outbox WHERE id = ?", (event_id,)).fetchone()
            if not row:
                raise NotFound("Outbox event was not found")
            delay = delay_minutes if delay_minutes is not None else min(5 * (2 ** min(row["attempts"], 6)), 360)
            available = (datetime.now(timezone.utc) + timedelta(minutes=delay)).isoformat().replace("+00:00", "Z")
            changed = connection.execute(
                "UPDATE sync_outbox SET status = 'retry', attempts = attempts + 1, last_error = ?, available_at = ?, updated_at = ? WHERE id = ?",
                (error, available, utc_now(), event_id),
            ).rowcount
            if not changed:
                raise NotFound("Outbox event was not found")

    def defer_outbox(self, error: str, delay_minutes: int = 60) -> int:
        available = (datetime.now(timezone.utc) + timedelta(minutes=delay_minutes)).isoformat().replace("+00:00", "Z")
        with self.write_transaction() as connection:
            return connection.execute(
                "UPDATE sync_outbox SET status = 'retry', last_error = ?, available_at = ?, updated_at = ? "
                "WHERE status IN ('pending','retry')",
                (error, available, utc_now()),
            ).rowcount

    def metrics(self) -> dict[str, Any]:
        with self.connect() as connection:
            result: dict[str, Any] = {}
            for table in ("topics", "records", "review_requests", "sync_outbox"):
                result[table] = connection.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()["count"]
            result["record_status"] = {
                row["status"]: row["count"]
                for row in connection.execute("SELECT status, COUNT(*) AS count FROM records GROUP BY status")
            }
            result["pending_reviews"] = connection.execute(
                "SELECT COUNT(*) AS count FROM review_requests WHERE status = 'pending'"
            ).fetchone()["count"]
            result["pending_outbox"] = connection.execute(
                "SELECT COUNT(*) AS count FROM sync_outbox WHERE status IN ('pending', 'retry')"
            ).fetchone()["count"]
            result["retry_outbox"] = connection.execute(
                "SELECT COUNT(*) AS count FROM sync_outbox WHERE status = 'retry'"
            ).fetchone()["count"]
            return result

    def bootstrap(self, records: list[dict[str, Any]], actor: str) -> dict[str, Any]:
        imported = 0
        skipped = 0
        seen_codes: set[str] = set()
        with self.write_transaction() as connection:
            for item in records:
                z_code = item["z_code"]
                if z_code in seen_codes:
                    raise AllocationConflict(f"Duplicate Z-Code in bootstrap payload: {z_code}")
                seen_codes.add(z_code)
                core, lane, topic_identifier, suffix = self.parse_z_code(z_code)
                existing_code = connection.execute("SELECT * FROM records WHERE z_code = ?", (z_code,)).fetchone()
                if existing_code:
                    topic = connection.execute("SELECT * FROM topics WHERE id = ?", (existing_code["topic_pk"],)).fetchone()
                    if topic["name_key"].lower() != item["name_key"].lower() or normalize_page_type(existing_code["page_type"]) != normalize_page_type(item["page_type"]):
                        raise AllocationConflict(f"Existing Z-Code does not match bootstrap payload: {z_code}")
                    skipped += 1
                    continue

                topic = self.find_topic(connection, item["name_key"])
                if topic and (
                    topic["z_knowledge_core"] != core
                    or topic["knowledge_lane"] != lane
                    or topic["topic_identifier"] != topic_identifier
                ):
                    raise AllocationConflict(
                        f"Name-Key {item['name_key']} is already mapped to a different core, lane, or Topic Identifier"
                    )
                if not topic:
                    now = utc_now()
                    try:
                        self.reserve_topic_identifier(connection, core, lane, topic_identifier, "bootstrap")
                        cursor = connection.execute(
                            "INSERT INTO topics(topic_identifier, name_key, topic_name, z_knowledge_core, knowledge_lane, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (topic_identifier, item["name_key"], item["name_key"].replace("-", " "), core, lane, now, now),
                        )
                    except sqlite3.IntegrityError as exc:
                        raise AllocationConflict(f"Topic collision while importing {z_code}") from exc
                    topic = connection.execute("SELECT * FROM topics WHERE id = ?", (cursor.lastrowid,)).fetchone()
                suffix_collision = connection.execute(
                    "SELECT z_code FROM records WHERE topic_pk = ? AND record_suffix = ?", (topic["id"], suffix)
                ).fetchone()
                if suffix_collision:
                    raise AllocationConflict(
                        f"Suffix collision: {z_code} conflicts with {suffix_collision['z_code']}"
                    )
                now = utc_now()
                self.reserve_z_code(connection, z_code, "bootstrap")
                connection.execute(
                    """INSERT INTO records(
                        z_code, topic_pk, page_type, record_suffix, request_id, reserved_by, status,
                        notion_url, reserved_at, expires_at, confirmed_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?)""",
                    (
                        z_code,
                        topic["id"],
                        item["page_type"],
                        suffix,
                        f"bootstrap:{z_code}",
                        actor,
                        item.get("notion_url"),
                        now,
                        now,
                        now,
                        now,
                    ),
                )
                imported += 1
            event = {"imported": imported, "skipped": skipped, "submitted": len(records)}
            self.add_audit(connection, "bootstrap_import", actor, event)
            return event


