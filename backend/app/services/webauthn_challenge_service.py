import base64
import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.webauthn_challenge import WebAuthnChallenge

logger = logging.getLogger(__name__)

DEFAULT_TTL_SECONDS = 300

PURPOSE_REGISTRATION = "registration"
PURPOSE_AUTHENTICATION = "authentication"
PURPOSE_OPERATOR_REGISTRATION = "operator_registration"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(value: str) -> bytes:
    padding = 4 - len(value) % 4
    if padding != 4:
        value += "=" * padding
    return base64.urlsafe_b64decode(value)


def _client_data(credential) -> dict | None:
    """Decode a WebAuthn credential's ``clientDataJSON`` into a dict.

    Returns ``None`` for any missing/malformed/non-object payload so callers can
    fail closed instead of falling back to a different challenge.
    """
    if not isinstance(credential, dict):
        return None
    response = credential.get("response")
    if not isinstance(response, dict):
        return None
    encoded = response.get("clientDataJSON")
    if not isinstance(encoded, str) or not encoded:
        return None
    try:
        decoded = _b64url_decode(encoded).decode("utf-8")
        data = json.loads(decoded)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def client_challenge_bytes(credential) -> bytes | None:
    """Return the raw challenge bytes the client signed, or ``None``.

    Parses ``response.clientDataJSON`` (base64url JSON) and decodes its
    ``challenge`` field (also base64url) back to the original server bytes.
    """
    data = _client_data(credential)
    if data is None:
        return None
    challenge = data.get("challenge")
    if not isinstance(challenge, str) or not challenge:
        return None
    try:
        return _b64url_decode(challenge)
    except Exception:
        return None


def challenge_hash_from_credential(credential) -> str | None:
    """Return the sha256 hex of the client-presented challenge, or ``None``."""
    raw = client_challenge_bytes(credential)
    if raw is None:
        return None
    return hashlib.sha256(raw).hexdigest()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _resolve_ttl(ttl_seconds: int | None) -> int:
    if ttl_seconds is not None:
        return ttl_seconds
    configured = getattr(get_settings(), "WEBAUTHN_CHALLENGE_TTL_SECONDS", None)
    return int(configured) if configured else DEFAULT_TTL_SECONDS


async def store_challenge(
    db: AsyncSession,
    challenge: bytes,
    purpose: str,
    *,
    session_id: str | None = None,
    user_id=None,
    ttl_seconds: int | None = None,
) -> WebAuthnChallenge:
    # W4-E08: the raw challenge is persisted (b64url, never logged) because the
    # WebAuthn verifier needs the exact server-side bytes; challenge_hash (sha256
    # hex) is stored alongside for lookup/integrity and is the only digest form.
    await _opportunistic_cleanup(db)

    now = _now()
    record = WebAuthnChallenge(
        challenge=_b64url_encode(challenge),
        challenge_hash=hashlib.sha256(challenge).hexdigest(),
        purpose=purpose,
        session_id=session_id,
        user_id=user_id,
        created_at=now,
        expires_at=now + timedelta(seconds=_resolve_ttl(ttl_seconds)),
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def _opportunistic_cleanup(db: AsyncSession) -> None:
    """Best-effort expiry sweep so the table cannot grow unbounded.

    Runs in a SAVEPOINT: a cleanup failure rolls back only the sweep and never
    fails or aborts the caller's challenge store.
    """
    try:
        async with db.begin_nested():
            await cleanup_expired_challenges(db)
    except Exception:
        logger.warning("Opportunistic WebAuthn challenge cleanup failed", exc_info=True)


async def get_valid_challenge(
    db: AsyncSession,
    purpose: str,
    *,
    session_id: str | None = None,
    user_id=None,
    for_update: bool = True,
) -> WebAuthnChallenge | None:
    stmt = select(WebAuthnChallenge).where(
        WebAuthnChallenge.purpose == purpose,
        WebAuthnChallenge.consumed_at.is_(None),
        WebAuthnChallenge.expires_at > _now(),
    )
    if session_id is None:
        stmt = stmt.where(WebAuthnChallenge.session_id.is_(None))
    else:
        stmt = stmt.where(WebAuthnChallenge.session_id == session_id)
    if user_id is None:
        stmt = stmt.where(WebAuthnChallenge.user_id.is_(None))
    else:
        stmt = stmt.where(WebAuthnChallenge.user_id == user_id)
    stmt = stmt.order_by(
        WebAuthnChallenge.created_at.desc(),
        WebAuthnChallenge.id.desc(),
    ).limit(1)
    if for_update:
        stmt = stmt.with_for_update()
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_valid_challenge_by_hash(
    db: AsyncSession,
    challenge_hash: str,
    purpose: str,
    *,
    session_id: str | None = None,
    user_id=None,
    for_update: bool = True,
) -> WebAuthnChallenge | None:
    """Select the unconsumed, unexpired challenge matching an exact hash.

    This is the ceremony-verification lookup (W4-F03): it identifies the row the
    client actually answered instead of the newest pending row, so concurrent
    registration/authentication/operator ceremonies cannot overwrite or verify
    against each other's challenges. ``purpose`` and the session/user binding
    are enforced exactly like ``get_valid_challenge``.
    """
    stmt = select(WebAuthnChallenge).where(
        WebAuthnChallenge.challenge_hash == challenge_hash,
        WebAuthnChallenge.purpose == purpose,
        WebAuthnChallenge.consumed_at.is_(None),
        WebAuthnChallenge.expires_at > _now(),
    )
    if session_id is None:
        stmt = stmt.where(WebAuthnChallenge.session_id.is_(None))
    else:
        stmt = stmt.where(WebAuthnChallenge.session_id == session_id)
    if user_id is None:
        stmt = stmt.where(WebAuthnChallenge.user_id.is_(None))
    else:
        stmt = stmt.where(WebAuthnChallenge.user_id == user_id)
    stmt = stmt.order_by(
        WebAuthnChallenge.created_at.desc(),
        WebAuthnChallenge.id.desc(),
    ).limit(1)
    if for_update:
        stmt = stmt.with_for_update()
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def mark_consumed(db: AsyncSession, record: WebAuthnChallenge) -> None:
    record.consumed_at = _now()
    db.add(record)
    await db.flush()


async def cleanup_expired_challenges(
    db: AsyncSession, before: datetime | None = None
) -> int:
    if before is None:
        before = _now()
    result = await db.execute(
        delete(WebAuthnChallenge).where(WebAuthnChallenge.expires_at < before)
    )
    return int(result.rowcount or 0)
