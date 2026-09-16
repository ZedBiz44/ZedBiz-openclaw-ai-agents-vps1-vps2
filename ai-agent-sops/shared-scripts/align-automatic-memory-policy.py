#!/usr/bin/env python3
"""Align one OpenClaw agent with the approved automatic-memory policy."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


AUTOMATIC_SECTION = """## Automatic Memory Capture Standard

- This agent's active external conversational-memory provider is {provider_label}.
- {sidecar_rule}
- Keep the active external provider's automatic capture or retain and automatic recall enabled when the provider supports them.
- Useful context from reviews, research, audits, diagnosis, planning, and ordinary questions may be saved automatically or explicitly when it can help future work.
- Memory capture does not authorize publishing or changing Notion, Memory Wiki, GitHub, Asana, production systems, or another authoritative record. Those actions still follow the assignment's work boundary.
- Store useful facts, decisions, verified results, preferences, project status, handoffs, and compact pointers. Do not store credentials, secrets, raw private logs, full documents, unsupported guesses, or needless duplicate chatter.
"""


def replace_memory_boundary_lines(text: str, provider_label: str, sidecar_rule: str) -> str:
    kept: list[str] = []
    skipping_automatic_section = False
    for line in text.splitlines():
        if line == "## Automatic Memory Capture Standard":
            skipping_automatic_section = True
            continue
        if skipping_automatic_section:
            if line.startswith("## "):
                skipping_automatic_section = False
            else:
                continue
        low = line.lower()
        memory_target = any(
            marker in low
            for marker in (
                "provider-memory",
                "local-memory",
                "memory write",
                "writing to the provider",
                "mem0, or local-memory",
                "provider, local-memory",
            )
        )
        review_boundary = any(
            marker in low
            for marker in (
                "review-only",
                "investigation-only",
                "diagnosis-only",
                "diagnostic",
                "draft-only",
                "meaningful assignment does not automatically authorize",
                "respect the work boundary",
            )
        )
        if memory_target and review_boundary:
            continue
        kept.append(line)

    insert_at = next((i for i, line in enumerate(kept) if line.startswith("## ")), len(kept))
    policy_lines = AUTOMATIC_SECTION.format(
        provider_label=provider_label,
        sidecar_rule=sidecar_rule,
    ).rstrip().splitlines()
    kept[insert_at:insert_at] = policy_lines + [""]
    return "\n".join(kept).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="OpenClaw JSON config. Omit for a non-OpenClaw runtime such as Hermes.")
    parser.add_argument("--agents", required=True)
    parser.add_argument("--provider", choices=("mem0", "lancedb", "hindsight"), required=True)
    parser.add_argument("--enable-native-sidecar", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config) if args.config else None
    agents_path = Path(args.agents)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for path in tuple(path for path in (config_path, agents_path) if path is not None):
        shutil.copy2(path, path.with_name(f"{path.name}.before-auto-memory-{stamp}"))

    if config_path is not None:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        entries = config.setdefault("plugins", {}).setdefault("entries", {})

        if args.provider == "mem0":
            provider = entries.setdefault("openclaw-mem0", {}).setdefault("config", {})
            provider["autoCapture"] = True
            provider["autoRecall"] = True
            # Mem0 skills/triage mode delegates saving decisions to the agent and
            # prevents the approved automatic-capture behavior from being the
            # single deciding path.
            provider.pop("skills", None)
            if args.enable_native_sidecar:
                entries.setdefault("memory-core", {})["enabled"] = True
        elif args.provider == "lancedb":
            provider = entries.setdefault("memory-lancedb", {}).setdefault("config", {})
            provider["autoCapture"] = True
            provider["autoRecall"] = True
        else:
            provider = entries.setdefault("hindsight-openclaw", {}).setdefault("config", {})
            provider["autoRetain"] = True
            provider["autoRecall"] = True

        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    labels = {"mem0": "Mem0", "lancedb": "LanceDB", "hindsight": "Hindsight"}
    sidecar_rule = (
        "Keep standard OpenClaw workspace memory and native Dreaming enabled beside Mem0. Mem0 remains the active external provider."
        if args.provider == "mem0"
        else "Keep standard workspace memory available beside the external provider."
    )
    agents_path.write_text(
        replace_memory_boundary_lines(
            agents_path.read_text(encoding="utf-8"), labels[args.provider], sidecar_rule
        ),
        encoding="utf-8",
    )
    print(json.dumps({"config": str(config_path) if config_path else None, "agents": str(agents_path), "provider": args.provider}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

