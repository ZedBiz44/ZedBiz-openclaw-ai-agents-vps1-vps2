from __future__ import annotations

import asyncio
import hmac
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import Settings
from .database import AllocationConflict, Database, InvalidState, NotFound
from .models import (
    AllocateRequest,
    ConfirmRequest,
    OutboxResultRequest,
    ReassignTopicRequest,
    ResolveReviewRequest,
)


security = HTTPBearer(auto_error=False)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    database = Database(settings.database_path, settings.reservation_ttl_minutes)
    database.initialize()

    async def sweeper() -> None:
        while True:
            await asyncio.sleep(settings.sweeper_interval_seconds)
            await asyncio.to_thread(database.sweep_stale)

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        task = None
        if settings.sweeper_interval_seconds > 0:
            task = asyncio.create_task(sweeper())
        try:
            yield
        finally:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

    app = FastAPI(title="ZedBiz Z-Code Allocator", version="1.0.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.database = database

    def authenticate(
        credentials: HTTPAuthorizationCredentials | None = Depends(security),
    ) -> str:
        if not credentials or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail={"code": "unauthorized", "message": "Bearer token required"})
        for agent, token in settings.api_keys.items():
            if hmac.compare_digest(credentials.credentials, token):
                return agent
        raise HTTPException(status_code=401, detail={"code": "unauthorized", "message": "Invalid API token"})

    def require_admin(actor: str = Depends(authenticate)) -> str:
        if actor not in settings.admin_agents:
            raise HTTPException(status_code=403, detail={"code": "forbidden", "message": "Edith/admin access required"})
        return actor

    def translate_error(exc: Exception) -> HTTPException:
        if isinstance(exc, AllocationConflict):
            return HTTPException(
                status_code=409,
                detail={
                    "code": "requires_review" if exc.queue_id else "conflict",
                    "message": exc.message,
                    "queue_id": exc.queue_id,
                },
            )
        if isinstance(exc, NotFound):
            return HTTPException(status_code=404, detail={"code": "not_found", "message": str(exc)})
        if isinstance(exc, InvalidState):
            return HTTPException(status_code=409, detail={"code": "invalid_state", "message": str(exc)})
        return HTTPException(status_code=500, detail={"code": "internal_error", "message": "Unexpected allocator failure"})

    @app.get("/health")
    def health() -> dict[str, object]:
        return {"ok": True, "service": "z-code-allocator", "version": app.version}

    @app.post("/v1/allocate")
    def allocate(request: AllocateRequest, actor: str = Depends(authenticate)) -> dict[str, object]:
        try:
            return database.allocate(request.model_dump(mode="json"), actor)
        except Exception as exc:
            raise translate_error(exc) from exc

    @app.post("/v1/confirm")
    def confirm(request: ConfirmRequest, actor: str = Depends(authenticate)) -> dict[str, object]:
        try:
            return database.confirm(request.model_dump(mode="json"), actor, actor in settings.admin_agents)
        except Exception as exc:
            raise translate_error(exc) from exc

    @app.get("/v1/status/{request_id}")
    def request_status(request_id: str, _: str = Depends(authenticate)) -> dict[str, object]:
        try:
            return database.status(request_id)
        except Exception as exc:
            raise translate_error(exc) from exc

    @app.get("/v1/lookup")
    def lookup(
        name_key: str = Query(min_length=1, max_length=128),
        _: str = Depends(authenticate),
    ) -> dict[str, object]:
        try:
            return database.lookup(name_key)
        except Exception as exc:
            raise translate_error(exc) from exc

    @app.get("/v1/admin/queue")
    def review_queue(
        actor: str = Depends(require_admin), status: str = "pending"
    ) -> dict[str, object]:
        return {"requested_by": actor, "items": database.list_reviews(status)}

    @app.post("/v1/admin/reviews/{queue_id}/resolve")
    def resolve_review(
        queue_id: str,
        request: ResolveReviewRequest,
        actor: str = Depends(require_admin),
    ) -> dict[str, object]:
        try:
            return database.resolve_review(queue_id, request.resolution, request.notes, actor)
        except Exception as exc:
            raise translate_error(exc) from exc

    @app.post("/v1/admin/reassign-topic")
    def reassign_topic(
        request: ReassignTopicRequest, actor: str = Depends(require_admin)
    ) -> dict[str, object]:
        try:
            return database.reassign_topic(request.model_dump(mode="json"), actor)
        except Exception as exc:
            raise translate_error(exc) from exc

    @app.post("/v1/admin/stale/sweep")
    def sweep_stale(actor: str = Depends(require_admin)) -> dict[str, object]:
        changed = database.sweep_stale(actor)
        return {"stale_count": len(changed), "z_codes": changed}

    @app.get("/v1/admin/outbox")
    def outbox(
        actor: str = Depends(require_admin), limit: int = Query(default=100, ge=1, le=500)
    ) -> dict[str, object]:
        return {"requested_by": actor, "items": database.list_outbox(limit)}

    @app.post("/v1/admin/outbox/{event_id}/complete")
    def complete_outbox(event_id: int, _: str = Depends(require_admin)) -> dict[str, object]:
        try:
            database.complete_outbox(event_id)
            return {"event_id": event_id, "status": "completed"}
        except Exception as exc:
            raise translate_error(exc) from exc

    @app.post("/v1/admin/outbox/{event_id}/fail")
    def fail_outbox(
        event_id: int,
        request: OutboxResultRequest,
        _: str = Depends(require_admin),
    ) -> dict[str, object]:
        try:
            database.fail_outbox(event_id, request.error or "Mirror worker reported failure")
            return {"event_id": event_id, "status": "retry"}
        except Exception as exc:
            raise translate_error(exc) from exc

    @app.get("/v1/admin/metrics")
    def metrics(_: str = Depends(require_admin)) -> dict[str, object]:
        return database.metrics()

    return app


def create_default_app() -> FastAPI:
    return create_app()
