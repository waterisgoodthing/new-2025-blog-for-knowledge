from pydantic_settings import BaseSettings
from functools import lru_cache


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
    AI_BASE_URL: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-4o"

    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    DASHSCOPE_MODEL: str = "qwen-vl-max"

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    GITHUB_TOKEN: str = ""
    GITHUB_OWNER: str = ""
    GITHUB_REPO: str = ""
    GITHUB_BRANCH: str = "main"

    KEEP_ALIVE_ENABLED: bool = False
    KEEP_ALIVE_INTERVAL: int = 300
    KEEP_ALIVE_URL: str = "http://127.0.0.1:8000/api/health"

    AUTH_BYPASS: str = "true"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
