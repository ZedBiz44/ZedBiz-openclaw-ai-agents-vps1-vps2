from __future__ import annotations

import hmac
import html
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

from .database import Database, InvalidState, NotFound


security = HTTPBasic()
database = Database(os.getenv("ZCODE_DATABASE_PATH", "/data/zcode.db"))
database.initialize()
app = FastAPI(title="Z-Code Admin Dashboard", docs_url=None, redoc_url=None)


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


class ResyncRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


def page(records: list[dict], search: str) -> str:
    rows = "".join(
        f"""<tr><td><strong>{html.escape(r['z_code'])}</strong><br><small>{html.escape(r['name_key'])}</small></td>
        <td><span class='badge'>{html.escape(r['status'])}</span></td>
        <td><input id='type-{i}' value='{html.escape(r['page_type'])}'></td>
        <td><input id='url-{i}' value='{html.escape(r['notion_url'] or '')}' placeholder='Notion URL'></td>
        <td><input id='reason-{i}' placeholder='Reason required'><button onclick=\"save({i},'{html.escape(r['z_code'])}')\">Save</button><button class='secondary' onclick=\"resync({i},'{html.escape(r['z_code'])}')\">Resync</button></td></tr>"""
        for i, r in enumerate(records)
    )
    metrics = database.metrics()
    return f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>
    <title>Z-Code Admin</title><style>
    body{{font-family:system-ui;margin:0;background:#f5f7fa;color:#172033}}header{{background:#13243a;color:white;padding:22px 4vw}}main{{padding:22px 4vw}}.cards{{display:flex;gap:12px;flex-wrap:wrap}}.card{{background:white;padding:14px 18px;border-radius:10px;box-shadow:0 1px 4px #ccd}}table{{width:100%;border-collapse:collapse;background:white;margin-top:18px;font-size:14px}}th,td{{padding:10px;border-bottom:1px solid #e5e7eb;vertical-align:top}}input{{box-sizing:border-box;width:100%;padding:7px;margin-bottom:5px}}button{{background:#087f5b;color:white;border:0;padding:7px 11px;border-radius:5px;margin-right:5px;cursor:pointer}}button.secondary{{background:#40566f}}.badge{{background:#e6fcf5;padding:3px 7px;border-radius:10px}}small{{color:#667}}#notice{{position:fixed;right:20px;bottom:20px;background:#172033;color:white;padding:12px;border-radius:7px;display:none}}@media(max-width:900px){{table{{display:block;overflow:auto}}}}
    </style></head><body><header><h1>Z-Code Allocator Database</h1><p>Controlled-write administration. Every change is audited and queued to the Notion mirror.</p></header><main>
    <div class='cards'><div class='card'><strong>{metrics['records']}</strong><br>Records</div><div class='card'><strong>{metrics['topics']}</strong><br>Topics</div><div class='card'><strong>{metrics['pending_reviews']}</strong><br>Pending reviews</div><div class='card'><strong>{metrics['pending_outbox']}</strong><br>Mirror queue</div></div>
    <form method='get'><p><input name='search' value='{html.escape(search)}' placeholder='Search Z-Code, Name-Key or Notion URL'><button>Search</button></p></form>
    <table><thead><tr><th>Z-Code / Name-Key</th><th>Status</th><th>Page Type</th><th>Notion URL</th><th>Controlled action</th></tr></thead><tbody>{rows}</tbody></table>
    <p><a href='api/audit' target='_blank'>View audit trail (JSON)</a> · <a href='api/health' target='_blank'>Health</a></p></main><div id='notice'></div>
    <script>
    function note(t,ok){{let n=document.getElementById('notice');n.textContent=t;n.style.background=ok?'#087f5b':'#c92a2a';n.style.display='block';setTimeout(()=>n.style.display='none',5000)}}
    async function save(i,z){{let body={{page_type:document.getElementById('type-'+i).value,notion_url:document.getElementById('url-'+i).value||null,reason:document.getElementById('reason-'+i).value}};let r=await fetch('api/records/'+encodeURIComponent(z),{{method:'PATCH',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}});note(r.ok?'Saved and queued to Notion':await r.text(),r.ok)}}
    async function resync(i,z){{let reason=document.getElementById('reason-'+i).value;let r=await fetch('api/records/'+encodeURIComponent(z)+'/resync',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{reason}})}});note(r.ok?'Resync queued':await r.text(),r.ok)}}
    </script></body></html>"""


@app.get("/", response_class=HTMLResponse)
def home(search: str = Query(default="", max_length=128), _: str = Depends(authenticate)) -> str:
    return page(database.admin_records(search), search)


@app.get("/api/health")
def health(_: str = Depends(authenticate)) -> dict:
    return {"ok": True, "service": "z-code-admin", "metrics": database.metrics()}


@app.get("/api/audit")
def audit(_: str = Depends(authenticate), limit: int = Query(default=100, ge=1, le=500)) -> dict:
    return {"items": database.admin_audit(limit)}


@app.patch("/api/records/{z_code}")
def update_record(z_code: str, request: RecordUpdate, actor: str = Depends(authenticate)) -> dict:
    try:
        return database.admin_update_record(z_code, request.page_type, request.notion_url, request.reason, actor)
    except (InvalidState, NotFound) as exc:
        raise HTTPException(status_code=409 if isinstance(exc, InvalidState) else 404, detail=str(exc)) from exc


@app.post("/api/records/{z_code}/resync")
def resync_record(z_code: str, request: ResyncRequest, actor: str = Depends(authenticate)) -> dict:
    try:
        return database.admin_resync_record(z_code, request.reason, actor)
    except (InvalidState, NotFound) as exc:
        raise HTTPException(status_code=409 if isinstance(exc, InvalidState) else 404, detail=str(exc)) from exc
