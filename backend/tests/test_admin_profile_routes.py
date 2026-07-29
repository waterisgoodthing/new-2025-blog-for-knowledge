import unittest
import uuid

import pytest
from fastapi.routing import APIRoute
from sqlalchemy import delete
from fastapi.testclient import TestClient

import main
from app.routers import auth as auth_router
from app.database import async_session, engine
from app.models.admin_profile import AdminProfile
from app.models.note import User
from app.routers.auth import get_current_admin
from app.schemas.admin_profile import AdminProfileUpdate, HomePreferences
from app.services.admin_profile_service import get_or_create_profile, update_profile

TEST_ADMIN_ID = uuid.UUID("23247a68-7a00-4464-9d96-948c018fdffe")


def test_home_preferences_keep_a_learning_action_visible():
    with pytest.raises(ValueError, match="learning action"):
        HomePreferences(
            section_order=["today", "activity", "stats", "storage"],
            hidden_sections=["today", "activity"],
        )


def test_admin_profile_route_is_registered_and_admin_only():
    route = next(
        (
            route
            for route in main.app.routes
            if isinstance(route, APIRoute)
            and route.path == "/api/admin/profile"
            and "GET" in (route.methods or set())
        ),
        None,
    )

    put_route = next(
        route
        for route in main.app.routes
        if isinstance(route, APIRoute)
        and route.path == "/api/admin/profile"
        and "PUT" in (route.methods or set())
    )
    assert route is not None
    assert get_current_admin in {dependency.call for dependency in route.dependant.dependencies}
    assert get_current_admin in {dependency.call for dependency in put_route.dependant.dependencies}


class AdminProfileServiceTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.session = async_session()
        self.addAsyncCleanup(engine.dispose)
        self.addAsyncCleanup(self.session.close)
        self.user = User(
            id=uuid.uuid4(),
            username=f"i5-profile-{uuid.uuid4().hex[:8]}",
            password_hash="test-only",
            is_admin=True,
        )
        self.session.add(self.user)
        await self.session.commit()
        self.addAsyncCleanup(self._cleanup_user)

    async def _cleanup_user(self):
        await self.session.execute(delete(AdminProfile).where(AdminProfile.user_id == self.user.id))
        await self.session.execute(delete(User).where(User.id == self.user.id))
        await self.session.commit()

    async def test_profile_defaults_and_update_are_private_and_round_trip(self):
        profile = await get_or_create_profile(self.session, self.user.id)
        self.assertEqual(profile.display_name, self.user.username)
        self.assertEqual(profile.timezone, "Asia/Shanghai")
        self.assertTrue(profile.home_preferences["show_welcome"])

        updated = await update_profile(
            self.session,
            self.user.id,
            AdminProfileUpdate(
                display_name="I5 Owner",
                identity_title="Learner",
                signature="Keep learning",
                welcome_message="欢迎回来",
                timezone="UTC",
                home_preferences={
                    "show_welcome": True,
                    "section_order": ["today", "activity", "stats", "storage"],
                    "hidden_sections": ["storage"],
                },
            ),
        )
        await self.session.commit()

        self.assertEqual(updated.display_name, "I5 Owner")
        self.assertEqual(updated.timezone, "UTC")
        self.assertTrue(updated.home_preferences["show_welcome"])


def test_profile_http_requires_a_valid_admin_session():
    with TestClient(main.app) as client:
        response = client.get("/api/admin/profile")
        client.cookies.set("admin_session", "invalid-i5-session", path="/api")
        invalid = client.get("/api/admin/profile")

    assert response.status_code == 401
    assert invalid.status_code == 401


def test_profile_http_rejects_a_non_admin_session(monkeypatch):
    async def non_admin_session(*_args, **_kwargs):
        return User(id=uuid.uuid4(), username="i5-reader", is_admin=False), "password"

    monkeypatch.setattr(auth_router, "_resolve_session_user", non_admin_session)
    with TestClient(main.app) as client:
        client.cookies.set("admin_session", "non-admin-session", path="/api")
        response = client.get("/api/admin/profile")

    assert response.status_code == 403


def test_public_site_settings_does_not_include_private_profile_fields():
    with TestClient(main.app) as client:
        response = client.get("/api/content/site-settings")

    assert response.status_code == 200
    payload = response.json()
    assert "display_name" not in payload
    assert "timezone" not in payload


def test_profile_http_validates_timezone_and_round_trips_for_admin():
    async def admin_override():
        return User(id=TEST_ADMIN_ID, username="i4_closure", is_admin=True)

    main.app.dependency_overrides[get_current_admin] = admin_override
    try:
        with TestClient(main.app) as client:
            invalid = client.put(
                "/api/admin/profile",
                json={"display_name": "I5 Owner", "timezone": "Mars/Olympus"},
            )
            assert invalid.status_code == 422

            invalid_preferences = client.put(
                "/api/admin/profile",
                json={
                    "display_name": "I5 Owner",
                    "timezone": "UTC",
                    "home_preferences": {
                        "section_order": ["today", "today"],
                        "hidden_sections": [],
                    },
                },
            )
            assert invalid_preferences.status_code == 422

            hidden_learning_actions = client.put(
                "/api/admin/profile",
                json={
                    "display_name": "I5 Owner",
                    "timezone": "UTC",
                    "home_preferences": {
                        "show_welcome": True,
                        "section_order": ["today", "activity", "stats", "storage"],
                        "hidden_sections": ["today", "activity"],
                    },
                },
            )
            assert hidden_learning_actions.status_code == 422

            updated = client.put(
                "/api/admin/profile",
                json={
                    "display_name": "I5 Owner",
                    "identity_title": "Learner",
                    "signature": "Keep learning",
                    "welcome_message": "欢迎回来",
                    "timezone": "UTC",
                    "home_preferences": {
                        "show_welcome": True,
                        "section_order": ["today", "activity", "stats", "storage"],
                        "hidden_sections": ["storage"],
                    },
                },
            )
            assert updated.status_code == 200
            assert updated.json()["timezone"] == "UTC"

            loaded = client.get("/api/admin/profile")
            assert loaded.status_code == 200
            assert loaded.json()["display_name"] == "I5 Owner"
            assert loaded.json()["home_preferences"]["hidden_sections"] == ["storage"]
    finally:
        main.app.dependency_overrides.pop(get_current_admin, None)
