import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.session import AdminSession
from app.utils.auth import hash_session_token


async def record_audit(
    db: AsyncSession,
    action: str,
    entity_type: str | None = None,
    entity_id: str | None = None,
    before: dict | None = None,
    after: dict | None = None,
    actor_session_id: uuid.UUID | None = None,
    auth_level: str | None = None,
    ip: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    log = AuditLog(
        actor_session_id=actor_session_id,
        auth_level=auth_level,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before=before,
        after=after,
        ip=ip,
        user_agent=user_agent,
    )
    db.add(log)
    return log


async def resolve_session_info(
    db: AsyncSession,
    session_token: str | None,
    request=None,
) -> dict:
    result = {}
    if session_token:
        token_hash = hash_session_token(session_token)
        res = await db.execute(
            select(AdminSession).where(
                AdminSession.token_hash == token_hash,
                AdminSession.revoked == False,
            )
        )
        sess = res.scalar_one_or_none()
        if sess:
            result["actor_session_id"] = sess.id
            result["auth_level"] = sess.auth_level
    if request and request.client:
        result["ip"] = request.client.host
    if request:
        result["user_agent"] = request.headers.get("user-agent", "")[:500]
    return result


async def audit_action(
    db: AsyncSession,
    action: str,
    session_token: str | None = None,
    request=None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    before: dict | None = None,
    after: dict | None = None,
) -> AuditLog:
    info = await resolve_session_info(db, session_token, request)
    return await record_audit(
        db,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before=before,
        after=after,
        **info,
    )
