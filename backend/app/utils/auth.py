import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt

PASSKEY_SESSION_DAYS = 7
PASSWORD_SESSION_DAYS = 3


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except (TypeError, ValueError):
        return False


def generate_session_token() -> str:
    return secrets.token_urlsafe(48)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def get_session_expiry(auth_level: str) -> datetime:
    if auth_level == "passkey":
        days = PASSKEY_SESSION_DAYS
    else:
        days = PASSWORD_SESSION_DAYS
    return datetime.now(timezone.utc) + timedelta(days=days)
