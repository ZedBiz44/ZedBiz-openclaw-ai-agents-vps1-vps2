#!/usr/bin/env python3
"""Read Harry's one dated journal using the approved Notion CLI login."""
import datetime,json,os,subprocess,sys
from zoneinfo import ZoneInfo
value=sys.argv[1] if len(sys.argv)==2 else datetime.datetime.now(ZoneInfo("America/Edmonton")).date().isoformat()
if len(sys.argv)>2 or datetime.date.fromisoformat(value).isoformat()!=value:
    raise SystemExit("Use YYYY-MM-DD or no argument")
env=os.environ.copy();env.pop("NOTION_API_TOKEN",None)
env.update(NOTION_KEYRING="0",NOTION_HOME="/root/.openclaw-harry/notion-cli")
f={"property":"Name","title":{"equals":value+" | Harry-daily-report"}}
r=subprocess.run(["/usr/bin/ntn","datasources","query","d40a3e33-d581-821a-9940-8740c397846b","--filter",json.dumps(f),"--json"],env=env,capture_output=True,text=True)
if r.returncode:
    print("Notion journal lookup failed; no journal was changed.",file=sys.stderr);raise SystemExit(r.returncode)
v=json.loads(r.stdout)
print(json.dumps(v))
