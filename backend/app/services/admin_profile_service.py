import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_profile import AdminProfile
from app.models.note import User
from app.schemas.admin_profile import AdminProfileUpdate, HomePreferences


class AdminProfileNotFound(Exception):
    pass


def _default_profile(user: User) -> AdminProfile:
    return AdminProfile(
        user_id=user.id,
        display_name=user.username,
        identity_title="",
        signature="",
        welcome_message="",
        timezone="Asia/Shanghai",
        home_preferences=HomePreferences().model_dump(),
    )


async def get_or_create_profile(session: AsyncSession, user_id: uuid.UUID) -> AdminProfile:
    profile = await session.scalar(select(AdminProfile).where(AdminProfile.user_id == user_id))
    if profile is not None:
        return profile

    user = await session.get(User, user_id)
    if user is None:
        raise AdminProfileNotFound(f"User {user_id} not found")
    profile = _default_profile(user)
    session.add(profile)
    await session.flush()
    return profile


async def update_profile(session: AsyncSession, user_id: uuid.UUID, payload: AdminProfileUpdate) -> AdminProfile:
    profile = await get_or_create_profile(session, user_id)
    profile.display_name = payload.display_name
    profile.identity_title = payload.identity_title
    profile.signature = payload.signature
    profile.welcome_message = payload.welcome_message
    profile.timezone = payload.timezone
    profile.home_preferences = payload.home_preferences.model_dump()
    await session.flush()
    return profile
