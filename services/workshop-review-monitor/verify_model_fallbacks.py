#!/usr/bin/env python3
"""Print a secret-free verification summary for an OpenClaw model config."""

import argparse
import json
from pathlib import Path

from configure_model_fallbacks import GEMINI, PAID_DEEPSEEK, FREE_DEEPSEEK, MAX_TOKENS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--agent", required=True)
    args = parser.parse_args()

    data = json.loads(Path(args.config).read_text(encoding="utf-8"))
    defaults = data.get("agents", {}).get("defaults", {})
    model = defaults.get("model", {})
    fallbacks = model.get("fallbacks", [])
    available = defaults.get("models", {})
    result = {
        "agent": args.agent,
        "primary": model.get("primary"),
        "obsoleteFreeDeepSeek": FREE_DEEPSEEK in fallbacks,
        "paidDeepSeekFallback": PAID_DEEPSEEK in fallbacks,
        "geminiMaxTokens": available.get(GEMINI, {}).get("params", {}).get("maxTokens"),
        "deepSeekMaxTokens": available.get(PAID_DEEPSEEK, {}).get("params", {}).get("maxTokens"),
        "valid": (
            FREE_DEEPSEEK not in fallbacks
            and PAID_DEEPSEEK in fallbacks
            and available.get(GEMINI, {}).get("params", {}).get("maxTokens") == MAX_TOKENS
            and available.get(PAID_DEEPSEEK, {}).get("params", {}).get("maxTokens") == MAX_TOKENS
        ),
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
