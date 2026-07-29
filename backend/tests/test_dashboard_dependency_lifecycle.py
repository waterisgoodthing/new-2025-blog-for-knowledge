import asyncio

import pytest
from sqlalchemy import event, text
from sqlalchemy.exc import SQLAlchemyError
from fastapi.testclient import TestClient

import main
from app.database import async_session, engine, get_db
from app.models.note import User
from app.routers.auth import get_current_admin
from app.routers import dashboard as dashboard_router


def test_get_db_commit_rollback_close_and_recovery_share_one_event_loop():
    commit_events: list[bool] = []
    rollback_events: list[bool] = []

    def on_commit(_connection):
        commit_events.append(True)

    def on_rollback(_connection):
        rollback_events.append(True)

    async def exercise():
        commit_dependency = get_db()
        commit_session = await commit_dependency.__anext__()
        await commit_session.execute(text("select 1"))
        with pytest.raises(StopAsyncIteration):
            await commit_dependency.asend(None)

        rollback_dependency = get_db()
        rollback_session = await rollback_dependency.__anext__()
        assert rollback_session is not None
        with pytest.raises(RuntimeError, match="dashboard dependency failure"):
            await rollback_dependency.athrow(RuntimeError("dashboard dependency failure"))

        async with async_session() as probe:
            assert await probe.scalar(text("select 1")) == 1

        await engine.dispose()

        with pytest.raises(StopAsyncIteration):
            await rollback_dependency.__anext__()

    event.listen(engine.sync_engine, "commit", on_commit)
    event.listen(engine.sync_engine, "rollback", on_rollback)
    try:
        asyncio.run(exercise())
    finally:
        event.remove(engine.sync_engine, "commit", on_commit)
        event.remove(engine.sync_engine, "rollback", on_rollback)

    assert commit_events
    assert rollback_events


def test_dashboard_sql_failure_rolls_back_real_http_dependency(monkeypatch):
    rollback_events: list[bool] = []

    def on_rollback(_connection):
        rollback_events.append(True)

    async def fail_summary(*_args, **_kwargs):
        raise SQLAlchemyError("forced dashboard failure")

    async def admin_override():
        return User(username="closure-admin", is_admin=True)

    event.listen(engine.sync_engine, "rollback", on_rollback)
    monkeypatch.setattr(dashboard_router.dashboard_service, "get_dashboard_summary", fail_summary)
    main.app.dependency_overrides[get_current_admin] = admin_override
    try:
        with TestClient(main.app) as client:
            response = client.get("/api/admin/dashboard/summary")
        assert response.status_code == 200
        assert response.json()["sections"]["learning"] == "unavailable"
    finally:
        main.app.dependency_overrides.pop(get_current_admin, None)
        event.remove(engine.sync_engine, "rollback", on_rollback)

    assert rollback_events
