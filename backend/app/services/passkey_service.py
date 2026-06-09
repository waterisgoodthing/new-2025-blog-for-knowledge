import base64
import json
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


def _get_rp_id() -> str:
    return get_settings().WEBAUTHN_RP_ID


def _get_origin() -> str:
    return get_settings().WEBAUTHN_ORIGIN


def _get_rp_name() -> str:
    return get_settings().WEBAUTHN_RP_NAME


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def generate_registration_options() -> dict:
    challenge = secrets.token_bytes(32)
    user_id = secrets.token_bytes(16)
    _reg_challenge_store["current"] = challenge
    return {
        "publicKey": {
            "rp": {"name": _get_rp_name(), "id": _get_rp_id()},
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


def verify_registration(attestation: dict) -> dict | None:
    from webauthn import verify_registration_response
    from webauthn.helpers.structs import RegistrationCredential

    expected_challenge = _reg_challenge_store.get("current")
    if not expected_challenge:
        logger.warning("Registration: no challenge stored")
        return None

    try:
        credential = RegistrationCredential.parse_raw(json.dumps(attestation))
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_origin=_get_origin(),
            expected_rp_id=_get_rp_id(),
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


def generate_authentication_options() -> dict:
    challenge = secrets.token_bytes(32)
    _auth_challenge_store["current"] = challenge
    return {
        "publicKey": {
            "challenge": _b64url_encode(challenge),
            "timeout": 60000,
            "rpId": _get_rp_id(),
            "userVerification": "required",
        }
    }


def verify_authentication(
    assertion: dict,
    stored_credential_id: str,
    stored_public_key: bytes,
    stored_sign_count: int,
) -> tuple[bool, int]:
    from webauthn import verify_authentication_response
    from webauthn.helpers.structs import AuthenticationCredential

    expected_challenge = _auth_challenge_store.get("current")
    if not expected_challenge:
        logger.warning("Auth: no challenge stored")
        return False, stored_sign_count

    try:
        credential = AuthenticationCredential.parse_raw(json.dumps(assertion))
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=expected_challenge,
            expected_rp_id=_get_rp_id(),
            expected_origin=_get_origin(),
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


async def get_credential(db: AsyncSession) -> PasskeyCredential | None:
    result = await db.execute(select(PasskeyCredential))
    return result.scalar_one_or_none()
