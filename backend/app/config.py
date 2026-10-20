from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


def parse_login_throttle_delays(value: str) -> list[float]:
    """Parse ``LOGIN_THROTTLE_DELAYS`` ("2,5,15") into an ordered list of floats.

    Blank entries, non-numeric entries, and negative values are ignored so a
    malformed ``.env`` override degrades to "no delay" instead of raising during
    a login attempt. Order is preserved: index 0 is the shortest delay.
    """
    delays: list[float] = []
    for raw in str(value or "").split(","):
        token = raw.strip()
        if not token:
            continue
        try:
            seconds = float(token)
        except ValueError:
            continue
        if seconds < 0:
            continue
        delays.append(seconds)
    return delays


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

    # F04/D06: automatic OCR/vision recognition is off by default until a real
    # provider evaluation meets the PR-14 bar. When false, the recognize/retry
    # entry points refuse before any provider call and the manual entry path is
    # the supported flow. Set true only under separate provider authorization.
    OCR_AUTO_RECOGNITION_ENABLED: bool = False

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-v4-pro"

    KEEP_ALIVE_ENABLED: bool = False
    KEEP_ALIVE_INTERVAL: int = 300
    KEEP_ALIVE_URL: str = "http://127.0.0.1:8000/api/health"

    AUTH_BYPASS: str = "false"
    AUTH_BYPASS_ALLOW: str = "false"

    WEBAUTHN_RP_ID: str = "localhost"
    WEBAUTHN_ORIGIN: str = "http://localhost:2025"
    WEBAUTHN_RP_NAME: str = "Blog Admin"
    WEBAUTHN_CHALLENGE_TTL_SECONDS: int = 300

    LOGIN_THROTTLE_ENABLED: bool = True
    LOGIN_THROTTLE_WARN_THRESHOLD: int = 3
    LOGIN_THROTTLE_DELAYS: str = "2,5,15"
    LOGIN_THROTTLE_IP_TTL_SECONDS: int = 3600
    LOGIN_THROTTLE_ACCOUNT_MAX_FAILURES: int = 10
    LOGIN_THROTTLE_MAX_ACCOUNTS: int = 10_000

    OPERATOR_REGISTRATION_KEY: str = ""

    IMAGE_BASE_URL: str = "https://public-api.limengyang.me"
    UPLOAD_ROOT: str = str(Path(__file__).resolve().parents[1] / "uploads")
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
