import base64
import hashlib
import logging
import secrets
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.session import PasskeyCredential
from app.services import webauthn_challenge_service as challenge_service

logger = logging.getLogger(__name__)


def _get_rp_id() -> str:
    return get_settings().WEBAUTHN_RP_ID


def _get_origin() -> str:
    return get_settings().WEBAUTHN_ORIGIN


def _get_rp_name() -> str:
    return get_settings().WEBAUTHN_RP_NAME


def _resolve_rp_id(rp_id: str | None = None) -> str:
    return rp_id or _get_rp_id()


def _resolve_origin(origin: str | None = None) -> str:
    return origin or _get_origin()


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


async def _resolve_client_challenge(
    db: AsyncSession,
    credential,
    purpose: str,
    *,
    session_id: str | None = None,
    user_id=None,
):
    """Resolve the stored challenge the client actually answered (W4-F03).

    Returns ``(record, raw_challenge_bytes)`` or ``(None, None)``. Fails closed
    when the client payload is missing/malformed, no matching unconsumed and
    unexpired row exists for the purpose/binding, or the stored raw challenge
    differs from the client-presented bytes. Never falls back to the latest
    pending challenge.
    """
    client_bytes = challenge_service.client_challenge_bytes(credential)
    if client_bytes is None:
        return None, None
    record = await challenge_service.get_valid_challenge_by_hash(
        db,
        hashlib.sha256(client_bytes).hexdigest(),
        purpose,
        session_id=session_id,
        user_id=user_id,
    )
    if record is None:
        return None, None
    stored_bytes = _b64url_decode(record.challenge)
    if stored_bytes != client_bytes:
        logger.warning("Challenge hash/raw mismatch for purpose %s", purpose)
        return None, None
    return record, stored_bytes


async def generate_registration_options(
    db: AsyncSession,
    rp_id: str | None = None,
) -> dict:
    """Return PublicKeyCredentialCreationOptions and persist an unbound
    ``registration`` challenge (session_id/user_id NULL)."""
    challenge = secrets.token_bytes(32)
    user_id = secrets.token_bytes(16)
    await challenge_service.store_challenge(
        db, challenge, challenge_service.PURPOSE_REGISTRATION
    )
    return {
        "publicKey": {
            "rp": {"name": _get_rp_name(), "id": _resolve_rp_id(rp_id)},
            "user": {
                "id": _b64url_encode(user_id),
                "name": "admin",
                "displayName": "Administrator",
            },
            "challenge": _b64url_encode(challenge),
            "pubKeyCredParams": [
                {"type": "public-key", "alg": -7},
                {"type": "public-key", "alg": -257},
            ],
            "timeout": 60000,
            "attestation": "none",
            "authenticatorSelection": {
                "authenticatorAttachment": "platform",
                "userVerification": "required",
                "residentKey": "required",
            },
        }
    }


async def verify_registration(
    db: AsyncSession,
    attestation: dict,
    expected_origin: str | None = None,
    expected_rp_id: str | None = None,
) -> dict | None:
    """Verify an attestation against the ``registration`` challenge the client
    answered (matched by challenge hash, not merely the latest). Returns
    ``{"credential_id": str, "public_key": bytes, "sign_count": int}`` on success
    (``public_key`` is the raw COSE bytes) or ``None``. The challenge is marked
    consumed only on success."""
    from webauthn import verify_registration_response

    record, expected_challenge = await _resolve_client_challenge(
        db, attestation, challenge_service.PURPOSE_REGISTRATION
    )
    if not record:
        logger.warning("Registration: no matching challenge stored")
        return None

    try:
        verification = verify_registration_response(
            credential=attestation,
            expected_challenge=expected_challenge,
            expected_origin=_resolve_origin(expected_origin),
            expected_rp_id=_resolve_rp_id(expected_rp_id),
        )
        await challenge_service.mark_consumed(db, record)
        return {
            "credential_id": _b64url_encode(verification.credential_id),
            "public_key": verification.credential_public_key,
            "sign_count": verification.sign_count,
        }
    except Exception as e:
        logger.error(f"Registration verification failed: {e}")
        return None


async def generate_operator_registration_options(
    db: AsyncSession,
    session_id: str,
    rp_id: str | None = None,
) -> dict:
    """Return creation options and persist an ``operator_registration``
    challenge bound to the supplied ephemeral ``session_id``."""
    challenge = secrets.token_bytes(32)
    user_id = secrets.token_bytes(16)
    await challenge_service.store_challenge(
        db,
        challenge,
        challenge_service.PURPOSE_OPERATOR_REGISTRATION,
        session_id=session_id,
    )
    return {
        "publicKey": {
            "rp": {"name": _get_rp_name(), "id": _resolve_rp_id(rp_id)},
            "user": {
                "id": _b64url_encode(user_id),
                "name": "admin",
                "displayName": "Administrator",
            },
            "challenge": _b64url_encode(challenge),
            "pubKeyCredParams": [
                {"type": "public-key", "alg": -7},
                {"type": "public-key", "alg": -257},
            ],
            "timeout": 60000,
            "attestation": "none",
            "authenticatorSelection": {
                "authenticatorAttachment": "platform",
                "userVerification": "required",
                "residentKey": "required",
            },
        }
    }


async def verify_operator_registration(
    db: AsyncSession,
    attestation: dict,
    session_id: str,
    expected_origin: str | None = None,
    expected_rp_id: str | None = None,
) -> dict | None:
    """Verify an operator attestation against the challenge the client answered,
    bound to ``session_id`` and matched by challenge hash. Returns
    ``{"credential_id": str, "public_key": bytes, "sign_count": int}`` or
    ``None``. The challenge is marked consumed BEFORE verification (preserved
    operator semantics)."""
    from webauthn import verify_registration_response

    record, expected_challenge = await _resolve_client_challenge(
        db,
        attestation,
        challenge_service.PURPOSE_OPERATOR_REGISTRATION,
        session_id=session_id,
    )
    if not record:
        logger.warning(f"Operator registration: no matching challenge for session {session_id[:8]}...")
        return None

    await challenge_service.mark_consumed(db, record)

    try:
        verification = verify_registration_response(
            credential=attestation,
            expected_challenge=expected_challenge,
            expected_origin=_resolve_origin(expected_origin),
            expected_rp_id=_resolve_rp_id(expected_rp_id),
        )
        return {
            "credential_id": _b64url_encode(verification.credential_id),
            "public_key": verification.credential_public_key,
            "sign_count": verification.sign_count,
        }
    except Exception as e:
        logger.error(f"Operator registration verification failed: {e}")
        return None


async def generate_authentication_options(
    db: AsyncSession,
    rp_id: str | None = None,
) -> dict:
    """Return PublicKeyCredentialRequestOptions and persist an unbound
    ``authentication`` challenge (session_id/user_id NULL)."""
    challenge = secrets.token_bytes(32)
    await challenge_service.store_challenge(
        db, challenge, challenge_service.PURPOSE_AUTHENTICATION
    )
    return {
        "publicKey": {
            "challenge": _b64url_encode(challenge),
            "timeout": 60000,
            "rpId": _resolve_rp_id(rp_id),
            "userVerification": "required",
        }
    }


async def verify_authentication(
    db: AsyncSession,
    assertion: dict,
    stored_credential_id: str,
    stored_public_key: bytes,
    stored_sign_count: int,
    expected_origin: str | None = None,
    expected_rp_id: str | None = None,
) -> tuple[bool, int]:
    """Verify an assertion against the ``authentication`` challenge the client
    answered (matched by challenge hash, not merely the latest). Returns
    ``(ok, sign_count)``; on failure the original ``stored_sign_count`` is
    returned unchanged. ``stored_public_key`` is the raw COSE bytes from the
    credential row (``stored_credential_id`` is carried for call-site symmetry
    but is not read by the verifier). The challenge is marked consumed only on
    success."""
    from webauthn import verify_authentication_response

    record, expected_challenge = await _resolve_client_challenge(
        db, assertion, challenge_service.PURPOSE_AUTHENTICATION
    )
    if not record:
        logger.warning("Auth: no matching challenge stored")
        return False, stored_sign_count

    try:
        verification = verify_authentication_response(
            credential=assertion,
            expected_challenge=expected_challenge,
            expected_rp_id=_resolve_rp_id(expected_rp_id),
            expected_origin=_resolve_origin(expected_origin),
            credential_public_key=stored_public_key,
            credential_current_sign_count=stored_sign_count,
            require_user_verification=True,
        )
        await challenge_service.mark_consumed(db, record)
        return True, verification.new_sign_count
    except Exception as e:
        logger.error(f"Authentication verification failed: {e}")
        return False, stored_sign_count


async def register_credential(
    db: AsyncSession,
    credential_id: str,
    public_key: bytes,
    device_name: str | None = None,
) -> PasskeyCredential:
    result = await db.execute(select(PasskeyCredential))
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError("A passkey is already registered. Use reset mode to replace it.")

    cred = PasskeyCredential(
        credential_id=credential_id,
        public_key=public_key,
        sign_count=0,
        device_name=device_name,
    )
    db.add(cred)
    await db.flush()
    await db.refresh(cred)
    return cred


async def reset_credential(db: AsyncSession) -> bool:
    result = await db.execute(select(PasskeyCredential))
    existing = result.scalar_one_or_none()
    if existing:
        await db.delete(existing)
        return True
    return False


async def replace_credential(
    db: AsyncSession,
    credential_id: str,
    public_key: bytes,
    device_name: str | None = None,
) -> PasskeyCredential:
    result = await db.execute(select(PasskeyCredential))
    existing = result.scalars().all()
    for cred in existing:
        await db.delete(cred)

    new_cred = PasskeyCredential(
        credential_id=credential_id,
        public_key=public_key,
        sign_count=0,
        device_name=device_name,
        last_used_at=None,
    )
    db.add(new_cred)
    await db.flush()
    await db.refresh(new_cred)
    return new_cred


async def get_credential(db: AsyncSession) -> PasskeyCredential | None:
    result = await db.execute(select(PasskeyCredential))
    return result.scalar_one_or_none()
