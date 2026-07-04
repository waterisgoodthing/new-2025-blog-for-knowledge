from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/blog_db"
    JWT_SECRET_KEY: str = "your-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440
    ALLOWED_ORIGINS: str = "http://localhost:2025,http://localhost:3000,http://127.0.0.1:2025,http://127.0.0.1:3000,https://blog.limengyang.me,https://limengyang.me"
    ENABLE_REGISTRATION: bool = True
    REGISTRATION_KEY: str = ""
    AI_API_KEY: str = ""
    AI_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    AI_MODEL: str = "qwen3.7-plus"

    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    DASHSCOPE_MODEL: str = "qwen3.7-plus"

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseekv4pro"

    KEEP_ALIVE_ENABLED: bool = False
    KEEP_ALIVE_INTERVAL: int = 300
    KEEP_ALIVE_URL: str = "http://127.0.0.1:8000/api/health"

    AUTH_BYPASS: str = "false"
    AUTH_BYPASS_ALLOW: str = "false"

    WEBAUTHN_RP_ID: str = "localhost"
    WEBAUTHN_ORIGIN: str = "http://localhost:2025"
    WEBAUTHN_RP_NAME: str = "Blog Admin"

    OPERATOR_REGISTRATION_KEY: str = ""

    IMAGE_BASE_URL: str = "https://public-api.limengyang.me"
    UPLOAD_ROOT: str = str(Path(__file__).resolve().parents[1] / "uploads")
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
