from __future__ import annotations

import hmac
import html
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

from .database import AllocationConflict, Database, InvalidState, NotFound

security = HTTPBasic()
database = Database(os.getenv("ZCODE_DATABASE_PATH", "/data/zcode.db"))
database.initialize()
app = FastAPI(title="Z-Code Admin Dashboard", version="1.3.0", docs_url=None, redoc_url=None)


def authenticate(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    username = os.getenv("ZCODE_ADMIN_USERNAME", "jack")
    password = os.getenv("ZCODE_ADMIN_PASSWORD", "")
    valid = bool(password) and hmac.compare_digest(credentials.username, username) and hmac.compare_digest(credentials.password, password)
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid dashboard login", headers={"WWW-Authenticate": "Basic"})
    return credentials.username


class RecordUpdate(BaseModel):
    page_type: str = Field(min_length=1, max_length=128)
    notion_url: str | None = Field(default=None, max_length=2048)
    reason: str = Field(min_length=3, max_length=500)


class TopicNameUpdate(BaseModel):
    topic_name: str = Field(min_length=1, max_length=500)
    reason: str = Field(min_length=3, max_length=500)


class TopicRename(BaseModel):
    new_name_key: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9-]{0,127}$")
    reason: str = Field(min_length=3, max_length=500)


class TopicReassign(BaseModel):
    new_z_knowledge_core: str = Field(pattern=r"^Z[A-Z0-9]{2,7}$")
    new_knowledge_lane: str = Field(pattern=r"^[0-9]{5}$")
    reason: str = Field(min_length=3, max_length=500)


class ResyncRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def record_rows(rows: list[dict]) -> str:
    return "".join(f"""<tr><td><b>{esc(r['record_title'] or '(title pending sync)')}</b><br><small>{esc(r['z_code'])}</small></td>
    <td>{esc(r['topic_name'])}<br><small>{esc(r['name_key'])}</small></td><td>{esc(r['z_knowledge_core'])}<br>{esc(r['knowledge_lane'])}-{esc(r['topic_identifier'])}-{int(r['record_suffix']):03d}</td>
    <td><span class=badge>{esc(r['status'])}</span></td><td><input id=t-{i} value='{esc(r['page_type'])}'></td>
    <td><input id=u-{i} value='{esc(r['notion_url'])}' placeholder='Notion URL'></td><td><input id=r-{i} placeholder='Reason required'><button onclick="saveRecord({i},'{esc(r['z_code'])}')">Save</button><button class=secondary onclick="resync({i},'{esc(r['z_code'])}')">Resync</button></td></tr>""" for i, r in enumerate(rows))


def topic_rows(rows: list[dict]) -> str:
    return "".join(f"""<tr><td><input id=tn-{i} value='{esc(r['topic_name'])}'><br><small>{esc(r['name_key'])}</small></td>
    <td>{esc(r['z_knowledge_core'])}-{esc(r['knowledge_lane'])}-{esc(r['topic_identifier'])}</td><td>{r['record_count']}</td><td>{esc(r['status'])}</td>
    <td><input id=tr-{i} placeholder='Reason required'><button onclick="saveTopicName({i},'{esc(r['name_key'])}')">Save Topic Name</button>
    <input id=nk-{i} placeholder='New Name-Key'><button class=warn onclick="renameTopic({i},'{esc(r['name_key'])}',{r['record_count']})">Rename Key</button>
    <div class=pair><input id=co-{i} placeholder='Core e.g. ZKB'><input id=la-{i} placeholder='Lane e.g. 10010'></div><button class=danger onclick="reassignTopic({i},'{esc(r['name_key'])}',{r['record_count']})">Reassign Family</button></td></tr>""" for i, r in enumerate(rows))


def retirement_rows(rows: list[dict]) -> str:
    return "".join(f"<tr><td>{esc(r['z_code'])}</td><td>{esc(r['new_z_code'])}</td><td>{esc(r['reason'])}</td><td>{esc(r['first_issued_at'])}</td><td>{esc(r['source'])}</td></tr>" for r in rows)


def mirror_rows(rows: list[dict]) -> str:
    return "".join(f"<tr><td>{r['id']}</td><td>{esc(r['event_type'])}</td><td>{esc(r['aggregate_key'])}</td><td>{esc(r['status'])}</td><td>{r['attempts']}</td><td>{esc(r['available_at'])}</td><td><small>{esc(r['last_error'])}</small></td></tr>" for r in rows)


def page(view: str, search: str) -> str:
    metrics = database.metrics()
    alert = f"<div class=alert>Mirror needs attention: {metrics['retry_outbox']} item(s) are waiting to retry. Open Mirror Health for details.</div>" if metrics['retry_outbox'] else ""
    if view == "topics":
        headings, rows = "<th>Topic Name / Name-Key</th><th>Topic Key</th><th>Records</th><th>Status</th><th>Controlled actions</th>", topic_rows(database.admin_topics(search))
    elif view == "retired":
        headings, rows = "<th>Issued or retired Z-Code</th><th>Current alias</th><th>Reason</th><th>First issued</th><th>Source</th>", retirement_rows(database.admin_retirement_history(search))
    elif view == "mirror":
        headings, rows = "<th>ID</th><th>Event</th><th>Record</th><th>Status</th><th>Attempts</th><th>Next try</th><th>Error</th>", mirror_rows(database.admin_outbox())
    else:
        view = "records"
        headings, rows = "<th>Record Title / Z-Code</th><th>Topic Name / Name-Key</th><th>Core / Lane-Topic-Suffix</th><th>Status</th><th>Page Type</th><th>Notion URL</th><th>Controlled action</th>", record_rows(database.admin_records(search))
    return f"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width'><title>Z-Code Admin</title><style>
    body{{font-family:system-ui;margin:0;background:#f5f7fa;color:#172033}}header{{background:#13243a;color:white;padding:22px 4vw}}main{{padding:22px 4vw}}nav a{{color:white;margin-right:18px}}.cards{{display:flex;gap:12px;flex-wrap:wrap}}.card{{background:white;padding:14px 18px;border-radius:10px;box-shadow:0 1px 4px #ccd}}table{{width:100%;border-collapse:collapse;background:white;margin-top:18px;font-size:14px}}th,td{{padding:10px;border-bottom:1px solid #e5e7eb;vertical-align:top}}input{{box-sizing:border-box;width:100%;padding:7px;margin-bottom:5px}}.pair{{display:flex;gap:5px}}button{{background:#087f5b;color:white;border:0;padding:7px 11px;border-radius:5px;margin:2px;cursor:pointer}}button.secondary{{background:#40566f}}button.warn{{background:#b76e00}}button.danger{{background:#b42318}}.badge{{background:#e6fcf5;padding:3px 7px;border-radius:10px}}small{{color:#667}}.alert{{background:#ffe3e3;border-left:5px solid #c92a2a;padding:12px;margin:14px 0}}#notice{{position:fixed;right:20px;bottom:20px;background:#172033;color:white;padding:12px;border-radius:7px;display:none}}@media(max-width:900px){{table{{display:block;overflow:auto}}}}
    </style></head><body><header><h1>Z-Code Allocator Database</h1><p>Allocator is authoritative. Changes are audited and mirrored to Notion.</p><nav><a href='/?view=records'>Records</a><a href='/?view=topics'>Topics</a><a href='/?view=retired'>Retired & Aliases</a><a href='/?view=mirror'>Mirror Health</a></nav></header><main>{alert}
    <div class=cards><div class=card><b>{metrics['records']}</b><br>Records</div><div class=card><b>{metrics['topics']}</b><br>Topics</div><div class=card><b>{metrics['pending_reviews']}</b><br>Pending reviews</div><div class=card><b>{metrics['pending_outbox']}</b><br>Mirror queue</div></div>
    <form method=get><input type=hidden name=view value='{esc(view)}'><p><input name=search value='{esc(search)}' placeholder='Search this view'><button>Search</button></p></form><table><thead><tr>{headings}</tr></thead><tbody>{rows}</tbody></table>
    <p><a href='/api/audit' target=_blank>Audit trail</a> · <a href='/api/health' target=_blank>Health</a></p></main><div id=notice></div><script>
    function note(t,ok){{let n=document.getElementById('notice');n.textContent=t;n.style.background=ok?'#087f5b':'#c92a2a';n.style.display='block';setTimeout(()=>n.style.display='none',6000)}}
    async function call(url,method,body){{let r=await fetch(url,{{method,headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}});note(r.ok?'Saved and queued to Notion':await r.text(),r.ok);if(r.ok)setTimeout(()=>location.reload(),700)}}
    function saveRecord(i,z){{call('/api/records/'+encodeURIComponent(z),'PATCH',{{page_type:document.getElementById('t-'+i).value,notion_url:document.getElementById('u-'+i).value||null,reason:document.getElementById('r-'+i).value}})}}
    function resync(i,z){{call('/api/records/'+encodeURIComponent(z)+'/resync','POST',{{reason:document.getElementById('r-'+i).value}})}}
    function saveTopicName(i,k){{call('/api/topics/'+encodeURIComponent(k)+'/name','PATCH',{{topic_name:document.getElementById('tn-'+i).value,reason:document.getElementById('tr-'+i).value}})}}
    function renameTopic(i,k,n){{if(confirm('Rename this Name-Key for '+n+' record(s)? The old key remains a permanent alias.'))call('/api/topics/'+encodeURIComponent(k)+'/rename','POST',{{new_name_key:document.getElementById('nk-'+i).value,reason:document.getElementById('tr-'+i).value}})}}
    function reassignTopic(i,k,n){{if(confirm('Reassign '+n+' record(s) to a new family? Every Z-Code will change. Old codes remain retired aliases and are never reused.'))call('/api/topics/'+encodeURIComponent(k)+'/reassign','POST',{{new_z_knowledge_core:document.getElementById('co-'+i).value,new_knowledge_lane:document.getElementById('la-'+i).value,reason:document.getElementById('tr-'+i).value}})}}
    </script></body></html>"""


@app.get("/", response_class=HTMLResponse)
def home(view: str = Query(default="records", pattern="^(records|topics|retired|mirror)$"), search: str = Query(default="", max_length=128), _: str = Depends(authenticate)) -> str:
    return page(view, search)


@app.get("/api/health")
def health(_: str = Depends(authenticate)) -> dict:
    return {"ok": True, "service": "z-code-admin", "version": "1.3.0", "metrics": database.metrics()}


@app.get("/api/audit")
def audit(_: str = Depends(authenticate), limit: int = Query(default=100, ge=1, le=500)) -> dict:
    return {"items": database.admin_audit(limit)}


def conflict(exc: Exception) -> HTTPException:
    return HTTPException(status_code=404 if isinstance(exc, NotFound) else 409, detail=str(exc))


@app.patch("/api/records/{z_code}")
def update_record(z_code: str, request: RecordUpdate, actor: str = Depends(authenticate)) -> dict:
    try: return database.admin_update_record(z_code, request.page_type, request.notion_url, request.reason, actor)
    except (InvalidState, NotFound) as exc: raise conflict(exc) from exc


@app.post("/api/records/{z_code}/resync")
def resync_record(z_code: str, request: ResyncRequest, actor: str = Depends(authenticate)) -> dict:
    try: return database.admin_resync_record(z_code, request.reason, actor)
    except (InvalidState, NotFound) as exc: raise conflict(exc) from exc


@app.patch("/api/topics/{name_key}/name")
def update_topic_name(name_key: str, request: TopicNameUpdate, actor: str = Depends(authenticate)) -> dict:
    try: return database.admin_update_topic_name(name_key, request.topic_name, request.reason, actor)
    except (InvalidState, NotFound) as exc: raise conflict(exc) from exc


@app.post("/api/topics/{name_key}/rename")
def rename_topic(name_key: str, request: TopicRename, actor: str = Depends(authenticate)) -> dict:
    try: return database.rename_topic({"name_key": name_key, **request.model_dump()}, actor)
    except (AllocationConflict, InvalidState, NotFound) as exc: raise conflict(exc) from exc


@app.post("/api/topics/{name_key}/reassign")
def reassign_topic(name_key: str, request: TopicReassign, actor: str = Depends(authenticate)) -> dict:
    try: return database.reassign_topic({"name_key": name_key, **request.model_dump()}, actor)
    except (AllocationConflict, InvalidState, NotFound) as exc: raise conflict(exc) from exc

