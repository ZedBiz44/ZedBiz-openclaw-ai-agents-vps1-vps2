from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Settings:
    database_path: str = "/data/zcode.db"
    api_keys: dict[str, str] = field(default_factory=dict)
    admin_agents: set[str] = field(default_factory=lambda: {"edith"})
    reservation_ttl_minutes: int = 60
    sweeper_interval_seconds: int = 60
    allocation_enabled: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        keys: dict[str, str] = {}
        key_file = os.getenv("ZCODE_API_KEYS_FILE", "/run/secrets/api_keys.json")
        if Path(key_file).is_file():
            keys.update(json.loads(Path(key_file).read_text(encoding="utf-8")))
        if raw := os.getenv("ZCODE_API_KEYS_JSON"):
            keys.update(json.loads(raw))
        return cls(
            database_path=os.getenv("ZCODE_DATABASE_PATH", "/data/zcode.db"),
            api_keys={str(k).lower(): str(v) for k, v in keys.items()},
            admin_agents={
                item.strip().lower()
                for item in os.getenv("ZCODE_ADMIN_AGENTS", "edith").split(",")
                if item.strip()
            },
            reservation_ttl_minutes=int(os.getenv("ZCODE_RESERVATION_TTL_MINUTES", "60")),
            sweeper_interval_seconds=int(os.getenv("ZCODE_SWEEPER_INTERVAL_SECONDS", "60")),
            allocation_enabled=os.getenv("ZCODE_ALLOCATION_ENABLED", "false").strip().lower() in {"1", "true", "yes"},
        )
