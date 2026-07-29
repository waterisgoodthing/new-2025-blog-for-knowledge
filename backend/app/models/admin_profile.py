import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AdminProfile(Base):
    __tablename__ = "admin_profiles"
    __table_args__ = (UniqueConstraint("user_id", name="uq_admin_profiles_user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    identity_title: Mapped[str] = mapped_column(String(100), nullable=False, default="", server_default="")
    signature: Mapped[str] = mapped_column(String(300), nullable=False, default="", server_default="")
    welcome_message: Mapped[str] = mapped_column(String(300), nullable=False, default="", server_default="")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Shanghai", server_default="Asia/Shanghai")
    home_preferences: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
