from contextlib import asynccontextmanager

from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.config import get_settings
from app.database import engine, Base, async_session
from app.routers import ai, ai_polish, audit, auth, categories, content, folders, knowledge, music, music_manage, notes, recommendations, review, subjects, suggestions, tags
from app.services.keep_alive import start_keep_alive, stop_keep_alive


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    
    # 生产安全检查
    if settings.ENV == "production":
        # 1. 默认 JWT 密钥检测并阻断
        if settings.JWT_SECRET_KEY == "your-secret-key-change-this":
            import sys
            print("\n" + "="*80)
            print("CRITICAL SECURITY ERROR: JWT_SECRET_KEY must be changed in production!")
            print("Please set JWT_SECRET_KEY environment variable to a strong random key.")
            print("="*80 + "\n")
            sys.exit("JWT_SECRET_KEY is insecure for production.")
        
        # 2. 生产环境 CORS 通配符 * 检测并阻断
        if not settings.ALLOWED_ORIGINS or "*" in settings.ALLOWED_ORIGINS:
            import sys
            print("\n" + "="*80)
            print("CRITICAL SECURITY ERROR: CORS ALLOWED_ORIGINS must be configured in production and cannot contain '*'!")
            print("Please set ALLOWED_ORIGINS environment variable to explicit origins.")
            print("="*80 + "\n")
            sys.exit("CORS config is insecure for production.")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    stop_event = None
    if settings.KEEP_ALIVE_ENABLED:
        stop_event = start_keep_alive()

    yield

    if stop_event is not None:
        await stop_keep_alive(stop_event)
    await engine.dispose()


app = FastAPI(title="Blog + Notes + Mistakes API", version="1.0.0", lifespan=lifespan)

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
app.include_router(content.router)
app.include_router(notes.router)
app.include_router(review.router)
app.include_router(tags.router)
app.include_router(subjects.router)
app.include_router(categories.router)

app.include_router(music.router)
app.include_router(recommendations.router)
app.include_router(ai.router)
app.include_router(ai_polish.router)
app.include_router(folders.router)
app.include_router(knowledge.router)
app.include_router(suggestions.router)
app.include_router(audit.router)
app.include_router(music_manage.router)

_images_dir = str(Path(__file__).resolve().parent.parent / "public" / "images")
os.makedirs(_images_dir, exist_ok=True)
app.mount("/images", StaticFiles(directory=_images_dir), name="images")


@app.get("/api/health")
async def health():
    db_ok = True
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return {"status": "ok", "db": "ok" if db_ok else "error"}
