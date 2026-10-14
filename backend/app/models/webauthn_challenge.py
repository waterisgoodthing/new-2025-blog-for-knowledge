import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class WebAuthnChallenge(Base):
    __tablename__ = "webauthn_challenges"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    # W4-E08 approved deviation: the plan sketched a hash-only schema, but the
    # WebAuthn verifier needs the exact raw challenge bytes server-side, so the
    # raw challenge is retained here (b64url) and never logged. `challenge_hash`
    # is the sha256 hex form used for lookup/integrity.
    challenge: Mapped[str] = mapped_column(String(128), nullable=False)
    challenge_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    purpose: Mapped[str] = mapped_column(String(32), nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
            name="fk_webauthn_challenges_user_id",
        ),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Migration 033 declares these four indexes SQL-side; mirror them in model
    # metadata (F04) so ORM-managed autogenerate reports no unexplained drift.
    # The partial predicates must match 033 exactly.
    __table_args__ = (
        Index(
            "idx_webauthn_challenges_purpose_session",
            "purpose",
            "session_id",
            postgresql_where=text("session_id IS NOT NULL"),
        ),
        Index(
            "idx_webauthn_challenges_purpose_user",
            "purpose",
            "user_id",
            postgresql_where=text("user_id IS NOT NULL"),
        ),
        Index(
            "idx_webauthn_challenges_expires",
            "expires_at",
            postgresql_where=text("consumed_at IS NULL"),
        ),
        Index("idx_webauthn_challenges_challenge_hash", "challenge_hash"),
        CheckConstraint(
            "purpose IN ('registration','authentication','operator_registration')",
            name="ck_webauthn_challenges_purpose",
        ),
    )
