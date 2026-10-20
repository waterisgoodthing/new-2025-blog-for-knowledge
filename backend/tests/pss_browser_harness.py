from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Request

import main
from app.database import get_db
from app.models.note import User
from app.models.session import AdminSession
from app.utils.auth import hash_session_token


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class _HarnessDb:
    def __init__(self, session_token: str | None):
        self.session_token = session_token

    async def execute(self, statement):
        query = str(statement)
        if "admin_sessions" in query:
            session = _sessions.get(self.session_token)
            if "revoked = false" in query and session and session.revoked:
                return _ScalarResult(None)
            return _ScalarResult(session)
        if "users" in query:
            return _ScalarResult(_admin if self.session_token == "pss-browser-admin" else None)
        raise AssertionError(f"unexpected browser-harness database statement: {query}")

    def add(self, _value):
        return None


_admin = User(
    id=UUID("00000000-0000-0000-0000-000000000006"),
    username="isolated-browser-admin",
    password_hash="disabled",
    is_admin=True,
)


def _session(token: str, *, expires_at: datetime) -> AdminSession:
    return AdminSession(
        user_id=_admin.id,
        token_hash=hash_session_token(token),
        auth_level="password",
        expires_at=expires_at,
        revoked=False,
    )


_sessions = {
    "pss-browser-admin": _session(
        "pss-browser-admin",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    ),
    "pss-browser-expired": _session(
        "pss-browser-expired",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    ),
}


async def _override_get_db(request: Request):
    yield _HarnessDb(request.cookies.get("admin_session"))


main.app.dependency_overrides[get_db] = _override_get_db
app = main.app
