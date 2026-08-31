"""Explicit SQLAlchemy model registry for Alembic schema lifecycle metadata.

Guest-message tables are intentionally excluded by Phase C+13 governance and
must not enter Alembic autogenerate through this registry.
"""

from app.database import Base

from .ai_call_log import AiCallLog
from .ai_run import AiRun
from .admin_profile import AdminProfile
from .attachment import Attachment, AttachmentLink
from .attempt import Attempt
from .audit import AuditLog
from .capture import CaptureItem
from .content import ManagedContentEntry
from .folder import Folder
from .mistake import Mistake, MistakeDraft
from .music import MusicItem
from .music_daily import (
    DailySong,
    MusicCandidate,
    MusicSourceRule,
    MusicSyncLog,
    NetEaseApiConfig,
)
from .note import Category, Note, Subject, Tag, User
from .knowledge_markdown import NoteLink, NoteVersion
from .question import DraftItem, Question, QuestionDraft, QuestionSource
from .recommendation import DailyRecommendation
from .review_item import ReviewItem, ReviewRecord
from .session import AdminPassword, AdminSession, PasskeyCredential
from .taxonomy import KnowledgePoint, KnowledgePointLink

MODEL_REGISTRY = (
    User,
    Tag,
    Subject,
    Category,
    Note,
    Folder,
    MusicItem,
    DailyRecommendation,
    AdminSession,
    PasskeyCredential,
    AdminPassword,
    AuditLog,
    NetEaseApiConfig,
    MusicSourceRule,
    MusicCandidate,
    DailySong,
    MusicSyncLog,
    ManagedContentEntry,
    KnowledgePoint,
    KnowledgePointLink,
    DraftItem,
    QuestionDraft,
    Question,
    QuestionSource,
    MistakeDraft,
    Mistake,
    ReviewItem,
    ReviewRecord,
    Attachment,
    AttachmentLink,
    CaptureItem,
    AiCallLog,
    AiRun,
    Attempt,
    AdminProfile,
    NoteVersion,
    NoteLink,
)

EXCLUDED_SCHEMA_MODELS = (
    "GuestMessage",
    "GuestMessageBan",
)

EXCLUDED_SCHEMA_TABLES = (
    "guest_messages",
    "guest_message_bans",
)

for table_name in EXCLUDED_SCHEMA_TABLES:
    table = Base.metadata.tables.get(table_name)
    if table is not None:
        Base.metadata.remove(table)

SCHEMA_LIFECYCLE_METADATA = Base.metadata
