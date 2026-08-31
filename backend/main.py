from contextlib import asynccontextmanager

from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.config import get_settings
from app.database import engine, async_session
from app.middleware.request_observability import request_observability
from app.routers import admin_mistakes, admin_profile, ai, ai_polish, ai_runs, attachments, attempts, audit, auth, captures, categories, content, dashboard, diagnostics, drafts, file_workspace, folders, governance, guest_messages, knowledge, knowledge_points, mistake_drafts, music, music_manage, notes, questions, recommendations, review, review_items, search, subjects, suggestions, tags
from app.services.keep_alive import start_keep_alive, stop_keep_alive

EXPECTED_ALEMBIC_REVISION = "026"


def _is_enabled(value: str) -> bool:
    return value.lower() == "true"


async def validate_database_readiness() -> None:
    """Run read-only startup checks without creating or mutating schema."""
    async with async_session() as session:
        await session.execute(text("SELECT 1"))
        result = await session.execute(text("SELECT version_num FROM alembic_version"))
        versions = {row[0] for row in result}

    if EXPECTED_ALEMBIC_REVISION not in versions:
        raise RuntimeError(
            "Database schema is not at the expected Alembic revision "
            f"{EXPECTED_ALEMBIC_REVISION}; found {sorted(versions) or ['<none>']}."
        )


_DEV_ENVIRONMENTS = {"development", "dev", "local", "test"}


def validate_security_settings(settings) -> None:
    """Fail closed on insecure configuration outside development environments."""
    env = str(getattr(settings, "ENV", "development")).strip().lower()
    if env in _DEV_ENVIRONMENTS:
        return

    if settings.JWT_SECRET_KEY == "your-secret-key-change-this":
        raise RuntimeError("JWT_SECRET_KEY is insecure for non-development environments.")

    if _is_enabled(getattr(settings, "AUTH_BYPASS", "false")) and _is_enabled(
        getattr(settings, "AUTH_BYPASS_ALLOW", "false")
    ):
        raise RuntimeError(
            "AUTH_BYPASS and AUTH_BYPASS_ALLOW cannot both be enabled outside development."
        )

    if not settings.ALLOWED_ORIGINS.strip() or "*" in settings.ALLOWED_ORIGINS:
        raise RuntimeError("CORS config is insecure for non-development environments.")

    if env == "production" and getattr(settings, "ENABLE_REGISTRATION", False):
        raise RuntimeError("ENABLE_REGISTRATION cannot be enabled in production.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    
    validate_security_settings(settings)

    await validate_database_readiness()

    stop_event = None
    if settings.KEEP_ALIVE_ENABLED:
        stop_event = start_keep_alive()

    yield

    if stop_event is not None:
        await stop_keep_alive(stop_event)
    await engine.dispose()


app = FastAPI(title="Blog + Notes + Mistakes API", version="1.0.0", lifespan=lifespan)
app.middleware("http")(request_observability)

settings = get_settings()
origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(diagnostics.router)
app.include_router(content.router)
app.include_router(notes.router)
app.include_router(review.router)
app.include_router(tags.router)
app.include_router(subjects.router)
app.include_router(knowledge_points.router)
app.include_router(drafts.router)
app.include_router(questions.router)
app.include_router(attempts.router)
app.include_router(admin_profile.router)
app.include_router(mistake_drafts.router)
app.include_router(admin_mistakes.router)
app.include_router(review_items.router)
app.include_router(attachments.router)
app.include_router(attachments.links_router)
app.include_router(file_workspace.router)
app.include_router(search.router)
app.include_router(governance.router)
app.include_router(captures.router)
app.include_router(categories.router)

app.include_router(music.router)
app.include_router(recommendations.router)
app.include_router(ai.router)
app.include_router(ai_polish.router)
app.include_router(ai_runs.router)
app.include_router(folders.router)
app.include_router(knowledge.router)
app.include_router(suggestions.router)
app.include_router(audit.router)
app.include_router(music_manage.router)
app.include_router(guest_messages.router)

_images_dir = str(Path(__file__).resolve().parent.parent / "public" / "images")
os.makedirs(_images_dir, exist_ok=True)
app.mount("/images", StaticFiles(directory=_images_dir), name="images")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
