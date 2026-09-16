#!/usr/bin/env python3
"""Replace a protected monitor token from DISCORD_BOT_TOKEN without printing it."""

import argparse
import json
import os
from pathlib import Path
import tempfile
import urllib.request


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    token = os.environ.get("DISCORD_BOT_TOKEN", "")
    if not token:
        raise SystemExit("DISCORD_BOT_TOKEN is empty")
    path = Path(args.config)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["discord_token"] = token
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    os.chmod(temp_name, 0o600)
    os.replace(temp_name, path)
    request = urllib.request.Request(
        "https://discord.com/api/v10/users/@me",
        headers={"Authorization": "Bot " + token, "User-Agent": "ZedBiz-Model-Monitor/1.1"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        identity = json.load(response)
    print(json.dumps({"discordBot": identity.get("username"), "configMode": oct(path.stat().st_mode & 0o777)}))


if __name__ == "__main__":
    main()
