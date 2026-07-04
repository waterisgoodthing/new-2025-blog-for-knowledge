import unittest

from app.cli import bootstrap_temp_admin, disable_temp_admin
from app.models.note import User
from app.utils.auth import verify_password


class _ScalarResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class _FakeSession:
    def __init__(self, existing_user=None):
        self.existing_user = existing_user
        self.added = []
        self.flushed = False
        self.refreshed = []

    async def execute(self, _statement):
        return _ScalarResult(self.existing_user)

    def add(self, value):
        self.added.append(value)
        if isinstance(value, User):
            self.existing_user = value

    async def flush(self):
        self.flushed = True

    async def refresh(self, value):
        self.refreshed.append(value)


class TempAdminBootstrapTest(unittest.IsolatedAsyncioTestCase):
    async def test_creates_missing_temporary_admin_user(self):
        session = _FakeSession()

        result = await bootstrap_temp_admin(session, username="temp-admin", password="generated-secret")

        self.assertTrue(result.created)
        self.assertEqual(result.user.username, "temp-admin")
        self.assertTrue(result.user.is_admin)
        self.assertTrue(verify_password("generated-secret", result.user.password_hash))
        self.assertTrue(session.flushed)
        self.assertEqual(session.refreshed, [result.user])

    async def test_rotates_existing_user_and_ensures_admin(self):
        existing = User(username="temp-admin", password_hash="old-hash", is_admin=False)
        session = _FakeSession(existing_user=existing)

        result = await bootstrap_temp_admin(session, username="temp-admin", password="new-secret")

        self.assertFalse(result.created)
        self.assertIs(result.user, existing)
        self.assertTrue(existing.is_admin)
        self.assertTrue(verify_password("new-secret", existing.password_hash))
        self.assertTrue(session.flushed)
        self.assertEqual(session.refreshed, [existing])

    async def test_disables_temporary_admin_user(self):
        existing = User(username="temp-admin", password_hash="old-hash", is_admin=True)
        session = _FakeSession(existing_user=existing)

        disabled = await disable_temp_admin(session, username="temp-admin")

        self.assertTrue(disabled)
        self.assertFalse(existing.is_admin)
        self.assertEqual(existing.password_hash, "disabled")
        self.assertTrue(session.flushed)
