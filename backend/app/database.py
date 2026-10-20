from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings
from app.utils.pending_files import clear_pending_files, discard_pending_files

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
            # Committed: the files written this request are now durable.
            clear_pending_files(session)
        except Exception:
            await session.rollback()
            # The DB row is gone, so discard any file written this request to
            # avoid an orphan (flush may have succeeded before commit failed).
            await discard_pending_files(session)
            raise
