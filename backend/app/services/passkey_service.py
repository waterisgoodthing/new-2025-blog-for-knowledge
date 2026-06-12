import base64
import logging
import secrets
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.session import PasskeyCredential

logger = logging.getLogger(__name__)

_reg_challenge_store: dict[str, bytes] = {}
_auth_challenge_store: dict[str, bytes] = {}
_operator_reg_challenge_store: dict[str, bytes] = {}


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


def generate_registration_options(
    rp_id: str | None = None,
) -> dict:
    challenge = secrets.token_bytes(32)
    user_id = secrets.token_bytes(16)
    _reg_challenge_store["current"] = challenge
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


def verify_registration(
    attestation: dict,
    expected_origin: str | None = None,
    expected_rp_id: str | None = None,
) -> dict | None:
    from webauthn import verify_registration_response

    expected_challenge = _reg_challenge_store.get("current")
    if not expected_challenge:
        logger.warning("Registration: no challenge stored")
        return None

    try:
        verification = verify_registration_response(
            credential=attestation,
            expected_challenge=expected_challenge,
            expected_origin=_resolve_origin(expected_origin),
            expected_rp_id=_resolve_rp_id(expected_rp_id),
        )
        del _reg_challenge_store["current"]
        return {
            "credential_id": _b64url_encode(verification.credential_id),
            "public_key": verification.credential_public_key,
            "sign_count": verification.sign_count,
        }
    except Exception as e:
        logger.error(f"Registration verification failed: {e}")
        return None


def generate_operator_registration_options(
    session_id: str,
    rp_id: str | None = None,
) -> dict:
    challenge = secrets.token_bytes(32)
    user_id = secrets.token_bytes(16)
    _operator_reg_challenge_store[session_id] = challenge
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


def verify_operator_registration(
    attestation: dict,
    session_id: str,
    expected_origin: str | None = None,
    expected_rp_id: str | None = None,
) -> dict | None:
    from webauthn import verify_registration_response

    expected_challenge = _operator_reg_challenge_store.pop(session_id, None)
    if not expected_challenge:
        logger.warning(f"Operator registration: no challenge for session {session_id[:8]}...")
        return None

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


def generate_authentication_options(
    rp_id: str | None = None,
) -> dict:
    challenge = secrets.token_bytes(32)
    _auth_challenge_store["current"] = challenge
    return {
        "publicKey": {
            "challenge": _b64url_encode(challenge),
            "timeout": 60000,
            "rpId": _resolve_rp_id(rp_id),
            "userVerification": "required",
        }
    }


def verify_authentication(
    assertion: dict,
    stored_credential_id: str,
    stored_public_key: bytes,
    stored_sign_count: int,
    expected_origin: str | None = None,
    expected_rp_id: str | None = None,
) -> tuple[bool, int]:
    from webauthn import verify_authentication_response

    expected_challenge = _auth_challenge_store.get("current")
    if not expected_challenge:
        logger.warning("Auth: no challenge stored")
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
        del _auth_challenge_store["current"]
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
