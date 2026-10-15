from fastapi.testclient import TestClient

import main
from app.database import get_db
from app.models.note import User
from app.utils.auth import verify_password


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class _FakeDb:
    def __init__(self, user):
        self.user = user

    async def execute(self, _statement):
        return _ScalarResult(self.user)


def test_verify_password_treats_disabled_and_malformed_hashes_as_invalid():
    assert verify_password("any-password", "disabled") is False
    assert verify_password("any-password", "not-a-bcrypt-hash") is False


def test_disabled_account_password_login_returns_401():
    async def override_get_db():
        yield _FakeDb(User(username="temp-admin", password_hash="disabled", is_admin=False))

    main.app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(main.app) as client:
            response = client.post(
                "/api/auth/login",
                json={"username": "temp-admin", "password": "any-password"},
            )

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid credentials"}
    finally:
        main.app.dependency_overrides.pop(get_db, None)
